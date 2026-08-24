"""
AI Director module – automatically enriches plain copied text with emotion tags
and natural pauses using Gemini Flash before sending it to the TTS synthesizer.
"""

import re
import sys
from typing import Optional
from .config import resolve_api_key

DIRECTOR_PROMPT = """You are an expert voice-acting director preparing text for expressive Text-to-Speech synthesis.
Analyze the emotional tone and rhythm of the following text, and enrich it with appropriate inline emotion tags in square brackets (e.g. [excited], [energetic], [happy], [curious], [whisper], [thoughtful], [confident]) and natural pauses in parentheses (e.g. (kurze Pause)).

RULES:
1. Do NOT alter, summarize, or remove the original wording.
2. Keep the original language (German/English/etc.).
3. Return ONLY the annotated text. Do NOT include any explanations, greetings, or markdown code blocks.

Text:
"""


def has_emotion_tags(text: str) -> bool:
    """Checks if the text already contains inline emotion tags like [excited] or (pause)."""
    return bool(re.search(r"\[(excited|energetic|happy|curious|whisper|thoughtful|confident|sarcastic|fast|sad|calm)\]", text, re.IGNORECASE))


def enrich_with_emotions(
    text: str,
    api_key: Optional[str] = None,
    model: str = "gemini-3.1-flash-lite-preview",
) -> str:
    """
    Analyzes plain text and injects expressive emotion and pause tags.
    If the text already contains tags, it is returned unchanged.
    """
    clean_text = text.strip()
    if not clean_text or len(clean_text) < 15 or has_emotion_tags(clean_text):
        return clean_text

    key = resolve_api_key(api_key, prompt_if_missing=False)
    if not key:
        return clean_text

    try:
        from google import genai

        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model=model,
            contents=DIRECTOR_PROMPT + clean_text,
        )
        if response and response.text:
            annotated = response.text.strip()
            # Clean up potential markdown code fence wrapping
            if annotated.startswith("```") and annotated.endswith("```"):
                lines = annotated.split("\n")
                annotated = "\n".join(lines[1:-1]).strip()
            return annotated
    except Exception as e:
        # Graceful fallback: return original text if AI director fails
        pass

    return clean_text
