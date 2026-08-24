"""
Command-line interface for Gemini Voice TTS.
Provides commands: `gemini-tts` and `tts`.
"""

import argparse
import sys
from .config import load_config, set_api_key, clear_config, resolve_api_key, CONFIG_FILE
from .clipboard import get_clipboard_text
from .tts import speak, AVAILABLE_VOICES, STYLE_PRESETS
from .listener import listen_clipboard, run_hotkey_listener, watch_file

__version__ = "1.3.0"


def print_voices():
    """Prints a friendly table of available Gemini voices."""
    print("=" * 60)
    print("🎙️  AVAILABLE GEMINI VOICES")
    print("=" * 60)
    descriptions = {
        "Puck": "Energetic, expressive, dynamic, youthful (Default)",
        "Kore": "Clear, professional, articulate, balanced",
        "Charon": "Deep, authoritative, masculine, resonant",
        "Fenrir": "Bold, strong, commanding, powerful",
        "Aoede": "Warm, lyrical, gentle, friendly",
        "Leda": "Soft, calming, smooth, reassuring",
        "Orus": "Grounded, relaxed, natural, steady",
        "Perseus": "Crisp, neutral, precise, focused",
        "Zephyr": "Light, breezy, casual, modern",
    }
    for voice in AVAILABLE_VOICES:
        desc = descriptions.get(voice, "")
        marker = "👉 " if voice == "Puck" else "   "
        print(f"{marker}{voice:<10} - {desc}")
    print("\nUse with: gemini-tts --voice <VoiceName> \"Your text\"")
    print("=" * 60)


def print_styles():
    """Prints available style presets."""
    print("=" * 60)
    print("🎭 AVAILABLE STYLE PRESETS (--style)")
    print("=" * 60)
    for style, prompt in STYLE_PRESETS.items():
        marker = "👉 " if style == "energetic" else "   "
        summary = prompt.replace("Director's Note: ", "") if prompt else "No pre-prompt (raw input)"
        print(f"{marker}{style:<12} : {summary[:70]}...")
    print("\nUse with: gemini-tts --style <StyleName> \"Your text\"")
    print("=" * 60)


from .config import (
    load_config,
    set_api_key,
    set_default_style,
    set_default_voice,
    get_default_style,
    get_default_voice,
    clear_config,
    resolve_api_key,
    CONFIG_FILE,
)


def handle_config_command(args):
    """Handles the `tts config` subcommand."""
    if args.set_key:
        set_api_key(args.set_key)
    elif args.set_style:
        set_default_style(args.set_style)
    elif args.set_voice:
        set_default_voice(args.set_voice)
    elif args.clear:
        clear_config()
    elif args.show:
        cfg = load_config()
        key = cfg.get("api_key", "")
        style = cfg.get("default_style", "energetic")
        voice = cfg.get("default_voice", "Puck")
        print("=" * 60)
        print("⚙️  GEMINI VOICE TTS CONFIGURATION")
        print("=" * 60)
        if key:
            masked = key[:6] + "..." + key[-4:] if len(key) > 10 else "***"
            print(f"🔑 API Key        : {masked}")
        else:
            resolved = resolve_api_key(prompt_if_missing=False)
            masked = (resolved[:6] + "..." + resolved[-4:]) if (resolved and len(resolved) > 10) else "Not set"
            print(f"🔑 API Key (Env)  : {masked}")
        print(f"🎭 Default Style  : {style}")
        print(f"🎙️ Default Voice  : {voice}")
        print(f"📁 Config File    : {CONFIG_FILE}")
        print("=" * 60)
    else:
        print("Usage: gemini-tts config [--set-key KEY | --set-style STYLE | --set-voice VOICE | --show | --clear]")


def main():
    # Force UTF-8 on Windows terminals
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    current_default_voice = get_default_voice()
    current_default_style = get_default_style()

    parser = argparse.ArgumentParser(
        prog="gemini-tts",
        description="🔊 Gemini Voice TTS – Free, natural & energetic Text-to-Speech powered by Google AI Studio.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gemini-tts                                     # Reads current clipboard text aloud
  gemini-tts --listen                            # Auto-reads on Double-Ctrl+C (Ctrl+C+C)
  gemini-tts config --set-style uwu              # Permanently set default style to uwu/wifey
  gemini-tts config --set-voice Aoede            # Permanently set default voice to Aoede
  gemini-tts config --show                       # Display current configuration
        """,
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommands")
    config_parser = subparsers.add_parser("config", help="Manage API key, default style, and voice")
    config_parser.add_argument("--set-key", "-k", help="Store your Google Gemini API key")
    config_parser.add_argument("--set-style", "-s", choices=list(STYLE_PRESETS.keys()), help="Set permanent default style (e.g. uwu, wifey, crazy)")
    config_parser.add_argument("--set-voice", "-v", choices=AVAILABLE_VOICES, help="Set permanent default voice (e.g. Aoede, Puck, Kore)")
    config_parser.add_argument("--show", action="store_true", help="Display current configuration")
    config_parser.add_argument("--clear", action="store_true", help="Remove stored configuration")

    # Main arguments
    parser.add_argument("text", nargs="*", help="Text to speak (reads clipboard if omitted)")
    parser.add_argument("--clipboard", "-c", action="store_true", help="Read text from clipboard")
    parser.add_argument("--listen", "-l", action="store_true", help="Live mode: auto-speaks newly copied text (Double-Ctrl+C)")
    parser.add_argument("--hotkey", "-hk", action="store_true", help="Global shortcut mode (Ctrl+Alt+S)")
    parser.add_argument("--file", "-f", help="Read text from file")
    parser.add_argument("--watch", "-w", help="Watch file and speak newly appended content")
    parser.add_argument("--output", "-o", help="Save synthesized audio to a .wav file instead of playing")
    parser.add_argument("--voice", "-v", default=current_default_voice, choices=AVAILABLE_VOICES, help=f"Voice persona (default: {current_default_voice})")
    parser.add_argument("--style", "-s", default=current_default_style, choices=list(STYLE_PRESETS.keys()), help=f"Style preset (default: {current_default_style})")
    parser.add_argument("--prompt", "-p", help="Custom director prompt (overrides --style)")
    parser.add_argument("--api-key", help="Explicit Gemini API key for this run")
    parser.add_argument("--list-voices", action="store_true", help="List all available voice personalities")
    parser.add_argument("--list-styles", action="store_true", help="List all available speech style presets")
    parser.add_argument("--no-director", action="store_true", help="Disable AI Director (do not auto-inject emotion tags into plain text)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args()

    # Subcommand handling
    if args.subcommand == "config":
        handle_config_command(args)
        return

    # Informational helpers
    if args.list_voices:
        print_voices()
        return
    if args.list_styles:
        print_styles()
        return

    # 1. Live clipboard listener mode
    if args.listen:
        listen_clipboard(voice=args.voice, style=args.style, custom_prompt=args.prompt, api_key=args.api_key)
        return

    # 2. Global hotkey mode
    if args.hotkey:
        run_hotkey_listener(voice=args.voice, style=args.style, custom_prompt=args.prompt, api_key=args.api_key)
        return

    # 3. Watch file mode
    if args.watch:
        watch_file(args.watch, voice=args.voice, style=args.style, custom_prompt=args.prompt, api_key=args.api_key)
        return

    # 4. Resolve text content
    text = None
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except Exception as e:
            print(f"❌ Error reading file {args.file}: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.text:
        text = " ".join(args.text)
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        # Default behavior with zero arguments: Read clipboard
        text = get_clipboard_text().strip()
        if not text:
            print("📋 Clipboard is currently empty.")
            print("   👉 Highlight text anywhere, press Double-Ctrl+C (Ctrl+C+C) or run 'tts'.")
            sys.exit(0)
        preview = text.replace("\n", " ")
        if len(preview) > 60:
            preview = preview[:57] + "..."
        print(f"📋 Reading clipboard: \"{preview}\"")

    if not text or not text.strip():
        print("⚠️ No text to speak.", file=sys.stderr)
        sys.exit(1)

    # 5. Synthesize and speak / save
    success = speak(
        text=text,
        voice=args.voice,
        style=args.style,
        custom_prompt=args.prompt,
        api_key=args.api_key,
        auto_director=not args.no_director,
        output_file=args.output,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
