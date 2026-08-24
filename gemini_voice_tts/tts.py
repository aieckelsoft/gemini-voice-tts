"""
Core Gemini Text-to-Speech synthesizer with Director-Prompting, Emotion Tag support,
and Intelligent Auto-Chunking for arbitrarily long texts (whole pages, articles, books).
"""

import io
import os
import re
import sys
import wave
from typing import List, Optional
from .config import resolve_api_key
from .playback import pcm_to_wav, play_wav_bytes

# Supported default voices
AVAILABLE_VOICES = [
    "Puck",     # Energetic, dynamic, engaging (Default)
    "Kore",     # Clear, professional, articulate
    "Charon",   # Deep, authoritative, masculine
    "Fenrir",   # Bold, strong, powerful
    "Aoede",    # Warm, melodic, gentle
    "Leda",     # Soft, calm, reassuring
    "Orus",     # Grounded, relaxed, balanced
    "Perseus",  # Crisp, neutral, steady
    "Zephyr",   # Light, breezy, natural
]

# Built-in style prompts for natural, expressive speech synthesis
STYLE_PRESETS = {
    "energetic": (
        "Director's Note: Read the following text in a highly energetic, enthusiastic, "
        "lively, engaging, and expressive voice. Use natural pitch variation, "
        "vibrant intonation, realistic pauses, and an authentic conversational flow. "
        "Respect all [emotion] and (pause) cues in the script precisely."
    ),
    "wifey": (
        "Director's Note: Read the following text in an ultra-cute, sweet, affectionate, "
        "and playful anime kawaii wifey tone. Use gentle giggles, soft sighs, blushing inflections, "
        "and adorable expressiveness. Respect all [sweet], [giggle], [whisper], [shy], [affectionate] cues."
    ),
    "uwu": (
        "Director's Note: Read the following text in an ultra-cute, sweet, affectionate, "
        "and playful anime kawaii wifey tone. Use gentle giggles, soft sighs, blushing inflections, "
        "and adorable expressiveness. Respect all [sweet], [giggle], [whisper], [shy], [affectionate] cues."
    ),
    "crazy": (
        "Director's Note: Read the following text in a wildly chaotic, theatrical, manic, "
        "unpredictable, and hyper-energetic tone. Swing dynamically between intense excitement, "
        "sarcastic whispers, sudden shouts, and bursts of unhinged energy. "
        "Respect all [manic], [shouting], [whisper], [laughing], [hyper], [sarcastic] cues."
    ),
    "random": (
        "Director's Note: Read the following text in a wildly chaotic, theatrical, manic, "
        "unpredictable, and hyper-energetic tone. Swing dynamically between intense excitement, "
        "sarcastic whispers, sudden shouts, and bursts of unhinged energy. "
        "Respect all [manic], [shouting], [whisper], [laughing], [hyper], [sarcastic] cues."
    ),
    "casual": (
        "Director's Note: Read the following text in a relaxed, friendly, natural, "
        "and conversational tone, like talking to a close teammate or friend."
    ),
    "storyteller": (
        "Director's Note: Read the following text like a skilled audiobook narrator: "
        "expressive, immersive, dynamic pacing, vivid emotional inflection, and dramatic timing."
    ),
    "tech": (
        "Director's Note: Read the following technical explanation in a crisp, sharp, "
        "confident, professional, yet lively and engaging voice."
    ),
    "news": (
        "Director's Note: Read the following in a confident, clear, articulate, "
        "and engaging broadcast anchor style."
    ),
    "raw": ""  # No director's note prepended
}


def split_text_into_chunks(text: str, max_chunk_chars: int = 2500) -> List[str]:
    """
    Intelligently splits long text into digestible chunks at paragraph or sentence boundaries.
    Prevents token cutoffs while preserving natural speaking cadence and thought continuity.
    """
    clean = text.strip()
    if len(clean) <= max_chunk_chars:
        return [clean] if clean else []

    chunks: List[str] = []
    # 1. Split by paragraphs
    paragraphs = re.split(r"\n\s*\n", clean)
    current_chunk: List[str] = []
    current_len = 0

    for para in paragraphs:
        p = para.strip()
        if not p:
            continue

        # If a single paragraph is larger than max_chunk_chars, split by sentences
        if len(p) > max_chunk_chars:
            sentences = re.split(r"(?<=[.!?])\s+", p)
            for sent in sentences:
                s = sent.strip()
                if not s:
                    continue
                if current_len + len(s) + 1 > max_chunk_chars:
                    if current_chunk:
                        chunks.append(" ".join(current_chunk))
                        current_chunk = []
                        current_len = 0
                current_chunk.append(s)
                current_len += len(s) + 1
        else:
            if current_len + len(p) + 2 > max_chunk_chars:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = []
                    current_len = 0
            current_chunk.append(p)
            current_len += len(p) + 2

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


def _synthesize_single_chunk(
    chunk_text: str,
    client,
    types_module,
    voice: str,
    director_note: str,
    model: str = "gemini-2.5-flash-preview-tts",
    max_retries: int = 2,
) -> Optional[bytes]:
    """Synthesizes a single chunk and returns raw PCM bytes with auto-retry on 429."""
    import time
    full_prompt = f"{director_note}\n\nSpeaker: {chunk_text}" if director_note else chunk_text

    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=full_prompt,
                config=types_module.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types_module.SpeechConfig(
                        voice_config=types_module.VoiceConfig(
                            prebuilt_voice_config=types_module.PrebuiltVoiceConfig(
                                voice_name=voice,
                            )
                        )
                    ),
                ),
            )
            audio_part = response.candidates[0].content.parts[0]
            return audio_part.inline_data.data
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                # Check for daily vs burst limit
                if "PerDay" in err_str:
                    print("\n⚠️  Tägliches Free-Tier-Limit (10 Requests/Tag) für dieses Google AI Studio Projekt erreicht.", file=sys.stderr)
                    print("   👉 Lösung 1: Erstelle in Google AI Studio ein weiteres Projekt (kostenlos) und trage den Key ein: tts config --set-key <KEY>", file=sys.stderr)
                    print("   👉 Lösung 2: Verknüpfe ein Billing-Konto im Google Cloud Projekt (1000+ Requests/Tag, die ersten Millionen Tokens bleiben quasi kostenlos).", file=sys.stderr)
                    return None

                if attempt < max_retries:
                    wait_time = 15.0
                    import re
                    match = re.search(r"retry in (\d+(\.\d+)?)s", err_str)
                    if match:
                        wait_time = min(float(match.group(1)) + 1.0, 30.0)
                    print(f"\n⏳ Rate Limit (429). Warte {wait_time:.1f}s für automatischen Retry...", file=sys.stderr)
                    time.sleep(wait_time)
                    continue

            print(f"❌ Gemini TTS API error on chunk: {e}", file=sys.stderr)
            return None

    return None


from .director import enrich_with_emotions, has_emotion_tags


def synthesize(
    text: str,
    voice: str = "Puck",
    style: str = "energetic",
    custom_prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    auto_director: bool = True,
    model: str = "gemini-2.5-flash-preview-tts",
) -> Optional[bytes]:
    """
    Synthesizes speech from text using Google's Gemini TTS API.
    Supports arbitrarily long texts via automatic intelligent chunking.
    Auto-enriches plain text with emotion tags when auto_director is enabled.
    Returns complete WAV byte data on success, or None on failure.
    """
    key = resolve_api_key(api_key)
    if not key:
        print("❌ Error: No Gemini API Key found.", file=sys.stderr)
        print("   Set it via: tts config --set-key <YOUR_KEY>", file=sys.stderr)
        print("   Or get one for free at: https://aistudio.google.com/apikey", file=sys.stderr)
        return None

    clean_text = text.strip()
    if not clean_text:
        return None

    # Step 1: Auto-Director (adds emotion & pause tags based on the active style)
    if auto_director and style != "raw" and not has_emotion_tags(clean_text) and len(clean_text) >= 15:
        annotated = enrich_with_emotions(clean_text, style=style, api_key=key)
        if annotated != clean_text:
            clean_text = annotated

    chunks = split_text_into_chunks(clean_text, max_chunk_chars=2500)
    if not chunks:
        return None

    director_note = custom_prompt if custom_prompt is not None else STYLE_PRESETS.get(style, STYLE_PRESETS["energetic"])

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=key)

        # Collect raw PCM audio from all chunks
        all_pcm = bytearray()
        total_chunks = len(chunks)

        if total_chunks > 1:
            print(f"📚 Long text detected ({len(clean_text)} chars) -> Split into {total_chunks} parts for seamless rendering...", file=sys.stderr)

        for i, chunk in enumerate(chunks, 1):
            if total_chunks > 1:
                print(f"   ⏳ Generating part {i}/{total_chunks} ({len(chunk)} chars)...", file=sys.stderr)
            pcm = _synthesize_single_chunk(chunk, client, types, voice, director_note, model)
            if pcm:
                all_pcm.extend(pcm)
            else:
                print(f"⚠️ Warning: Part {i} failed to synthesize.", file=sys.stderr)

        if not all_pcm:
            return None

        return pcm_to_wav(bytes(all_pcm))

    except ImportError:
        print("❌ Error: 'google-genai' package is required.", file=sys.stderr)
        print("   Install via: pip install google-genai", file=sys.stderr)
        return None


def speak(
    text: str,
    voice: str = "Puck",
    style: str = "energetic",
    custom_prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    auto_director: bool = True,
    output_file: Optional[str] = None,
    model: str = "gemini-2.5-flash-preview-tts",
) -> bool:
    """
    Synthesizes and either plays the speech aloud or writes it to an output file.
    Handles short paragraphs, whole pages, and long documents automatically.
    """
    wav_bytes = synthesize(
        text=text,
        voice=voice,
        style=style,
        custom_prompt=custom_prompt,
        api_key=api_key,
        auto_director=auto_director,
        model=model,
    )
    if not wav_bytes:
        return False

    if output_file:
        try:
            with open(output_file, "wb") as f:
                f.write(wav_bytes)
            print(f"💾 Saved complete audio ({len(wav_bytes)} bytes) to: {output_file}")
            return True
        except Exception as e:
            print(f"❌ Error writing to {output_file}: {e}", file=sys.stderr)
            return False

    play_wav_bytes(wav_bytes)
    return True
