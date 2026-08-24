"""
AI Director module – automatically enriches plain copied text with emotion tags
and natural pauses using Gemini Flash before sending it to the TTS synthesizer.
"""

import re
import sys
from typing import Optional
from .config import resolve_api_key

DIRECTOR_PROMPTS = {
    "default": """You are an expert voice-acting director preparing text for expressive Text-to-Speech synthesis.
Analyze the emotional tone and rhythm of the following text, and enrich it with appropriate inline emotion tags in square brackets (e.g. [excited], [energetic], [happy], [curious], [whisper], [thoughtful], [confident]) and natural pauses in parentheses (e.g. (kurze Pause)).

RULES:
1. Do NOT alter, summarize, or remove the original wording.
2. Keep the original language (German/English/etc.).
3. Return ONLY the annotated text. Do NOT include any explanations, greetings, or markdown code blocks.

Text:
""",
    "wifey": """You are a kawaii anime / affectionate wifey voice director.
Enrich the following text with ultra-cute, playful, affectionate tags like [sweet], [giggle], [whisper], [happy], [shy], [playful], [affectionate] and natural cute pauses like (kichert leise), (cute pause), (süße Pause).

RULES:
1. Do NOT alter the original wording.
2. Return ONLY the annotated text without code blocks or preambles.

Text:
""",
    "crazy": """You are a chaotic, wildly theatrical, manic voice director.
Enrich the following text with unhinged, unpredictable, hyper-energetic tags like [manic], [shouting], [whisper], [laughing], [excited], [sarcastic], [hyper] and pauses like (irres Lachen), (plötzliche Pause), (wildes Kichern).

RULES:
1. Do NOT alter the original wording.
2. Return ONLY the annotated text without code blocks or preambles.

Text:
"""
}


def has_emotion_tags(text: str) -> bool:
    """Checks if the text already contains inline emotion tags like [excited] or (pause)."""
    return bool(re.search(r"\[(excited|energetic|happy|curious|whisper|thoughtful|confident|sarcastic|fast|sad|calm|sweet|giggle|shy|playful|affectionate|manic|shouting|laughing|hyper)\]", text, re.IGNORECASE))


def enrich_with_emotions(
    text: str,
    style: str = "energetic",
    api_key: Optional[str] = None,
    model: str = "gemini-3.1-flash-lite-preview",
) -> str:
    """
    Analyzes plain text and injects expressive emotion and pause tags based on the active style.
    If the text already contains tags, it is returned unchanged.
    """
    clean_text = text.strip()
    if not clean_text or len(clean_text) < 15 or has_emotion_tags(clean_text):
        return clean_text

    key = resolve_api_key(api_key, prompt_if_missing=False)
    if not key:
        return clean_text

    # Select director persona
    if style in ("wifey", "uwu"):
        prompt_template = DIRECTOR_PROMPTS["wifey"]
    elif style in ("crazy", "random"):
        prompt_template = DIRECTOR_PROMPTS["crazy"]
    else:
        prompt_template = DIRECTOR_PROMPTS["default"]

    try:
        from google import genai

        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model=model,
            contents=prompt_template + clean_text,
        )
        if response and response.text:
            annotated = response.text.strip()
            # Clean up potential markdown code fence wrapping
            if annotated.startswith("```") and annotated.endswith("```"):
                lines = annotated.split("\n")
                annotated = "\n".join(lines[1:-1]).strip()
            return annotated
    except Exception:
        pass

    return clean_text
