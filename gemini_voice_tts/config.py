"""
Configuration and API key management for Gemini Voice TTS.
Handles interactive setup, local persistence (~/.gemini_tts/config.json),
environment variables, and Windows Registry.
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".gemini_tts"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict:
    """Loads configuration from ~/.gemini_tts/config.json."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_config(config: dict) -> None:
    """Saves configuration to ~/.gemini_tts/config.json."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def resolve_api_key(explicit_key: Optional[str] = None, prompt_if_missing: bool = True) -> Optional[str]:
    """
    Finds the Gemini API Key from:
    1. Explicit CLI argument
    2. GEMINI_API_KEY or GOOGLE_API_KEY environment variables
    3. User config file (~/.gemini_tts/config.json)
    4. Windows User Registry (HKCU\\Environment)
    5. Interactive prompt (if prompt_if_missing is True)
    """
    if explicit_key and explicit_key.strip():
        return explicit_key.strip()

    # 1. Environment variables
    for var in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        val = os.environ.get(var)
        if val and val.strip():
            return val.strip()

    # 2. Local config file
    config = load_config()
    if config.get("api_key"):
        return config["api_key"].strip()

    # 3. Windows Registry (User Environment)
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as reg_key:
                for var in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
                    try:
                        val, _ = winreg.QueryValueEx(reg_key, var)
                        if val and str(val).strip():
                            return str(val).strip()
                    except FileNotFoundError:
                        pass
        except Exception:
            pass

    # 4. Interactive prompt for first-time users
    if prompt_if_missing and sys.stdin.isatty():
        return prompt_for_api_key()

    return None


def prompt_for_api_key() -> Optional[str]:
    """Interactively guides the user to set up their free Google AI Studio API key."""
    print("=" * 65)
    print("🔑 Google Gemini API Key erforderlich / Setup")
    print("=" * 65)
    print("Du benötigst einen kostenlosen Gemini API Key von Google AI Studio:")
    print(" 👉 Erstelle deinen Key gratis hier: https://aistudio.google.com/apikey")
    print(" (Keine Kreditkarte erforderlich, 100% kostenloser Free Tier)")
    print("-" * 65)

    try:
        entered_key = input("Bitte füge deinen API Key hier ein: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nAbgebrochen.")
        return None

    if not entered_key:
        print("❌ Kein Key eingegeben.")
        return None

    # Save to config file
    config = load_config()
    config["api_key"] = entered_key
    save_config(config)
    print(f"✅ API Key wurde sicher gespeichert in: {CONFIG_FILE}")

    # On Windows, also offer to persist to user environment
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, "GEMINI_API_KEY", 0, winreg.REG_SZ, entered_key)
        except Exception:
            pass

    return entered_key


def set_api_key(key: str) -> None:
    """Explicitly sets and persists the API key."""
    config = load_config()
    config["api_key"] = key.strip()
    save_config(config)
    print(f"✅ API Key gespeichert in {CONFIG_FILE}")


def clear_config() -> None:
    """Removes stored configuration."""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
        print("✅ Gespeicherte Konfiguration gelöscht.")
    else:
        print("ℹ️ Keine Konfiguration vorhanden.")
