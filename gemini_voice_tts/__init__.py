"""
Gemini Voice TTS – High quality, expressive Text-to-Speech powered by Google AI Studio.
"""

from .tts import synthesize, speak, split_text_into_chunks, AVAILABLE_VOICES, STYLE_PRESETS
from .director import enrich_with_emotions, has_emotion_tags
from .config import resolve_api_key, set_api_key, clear_config
from .clipboard import get_clipboard_text
from .listener import listen_clipboard, run_hotkey_listener, watch_file

__version__ = "1.3.0"
__all__ = [
    "synthesize",
    "speak",
    "split_text_into_chunks",
    "enrich_with_emotions",
    "has_emotion_tags",
    "AVAILABLE_VOICES",
    "STYLE_PRESETS",
    "resolve_api_key",
    "set_api_key",
    "clear_config",
    "get_clipboard_text",
    "listen_clipboard",
    "run_hotkey_listener",
    "watch_file",
]
