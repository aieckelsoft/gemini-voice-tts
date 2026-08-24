"""
Core Gemini Text-to-Speech synthesizer with Director-Prompting and Emotion Tag support.
Uses Google AI Studio free tier models (e.g. gemini-2.5-flash-preview-tts).
"""

import os
import sys
from typing import Optional, Tuple
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


def synthesize(
    text: str,
    voice: str = "Puck",
    style: str = "energetic",
    custom_prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = "gemini-2.5-flash-preview-tts",
) -> Optional[bytes]:
    """
    Synthesizes speech from text using Google's Gemini TTS API.
    Returns WAV byte data on success, or None on failure.
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

    # Safety character ceiling for Free Tier token limits
    if len(clean_text) > 4000:
        clean_text = clean_text[:4000]

    # Build prompt with Director's Notes
    director_note = custom_prompt if custom_prompt is not None else STYLE_PRESETS.get(style, STYLE_PRESETS["energetic"])
    
    if director_note:
        full_prompt = f"{director_note}\n\nSpeaker: {clean_text}"
    else:
        full_prompt = clean_text

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=key)

        response = client.models.generate_content(
            model=model,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice,
                        )
                    )
                ),
            ),
        )

        audio_part = response.candidates[0].content.parts[0]
        pcm_data = audio_part.inline_data.data
        return pcm_to_wav(pcm_data)

    except ImportError:
        print("❌ Error: 'google-genai' package is required.", file=sys.stderr)
        print("   Install via: pip install google-genai", file=sys.stderr)
        return None
    except Exception as e:
        print(f"❌ Gemini TTS API error: {e}", file=sys.stderr)
        return None


def speak(
    text: str,
    voice: str = "Puck",
    style: str = "energetic",
    custom_prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    output_file: Optional[str] = None,
    model: str = "gemini-2.5-flash-preview-tts",
) -> bool:
    """
    Synthesizes and either plays the speech aloud or writes it to an output file.
    """
    wav_bytes = synthesize(
        text=text,
        voice=voice,
        style=style,
        custom_prompt=custom_prompt,
        api_key=api_key,
        model=model,
    )
    if not wav_bytes:
        return False

    if output_file:
        try:
            with open(output_file, "wb") as f:
                f.write(wav_bytes)
            print(f"💾 Saved audio to: {output_file}")
            return True
        except Exception as e:
            print(f"❌ Error writing to {output_file}: {e}", file=sys.stderr)
            return False

    play_wav_bytes(wav_bytes)
    return True
