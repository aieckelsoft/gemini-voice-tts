"""
Background listeners and watchers:
1. Live clipboard watcher (automatically speaks text copied via Ctrl+C / Cmd+C)
2. Global Windows hotkey listener (Ctrl+Alt+S captures selection and speaks)
3. File watcher (speaks newly appended lines/paragraphs from a log/chat file)
"""

import os
import sys
import time
from typing import Optional
from .clipboard import get_clipboard_text
from .tts import speak


def listen_clipboard(
    voice: str = "Puck",
    style: str = "energetic",
    custom_prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    poll_interval: float = 0.4,
) -> None:
    """
    Continuously monitors the system clipboard.
    Whenever new text is copied (Ctrl+C / Cmd+C), it is automatically spoken aloud.
    """
    print("=" * 65)
    print("🎧 GEMINI LIVE-CLIPBOARD LISTENER")
    print(f"   Voice: {voice} | Style: {style}")
    print("   👉 Select any text in your editor, browser, or chat.")
    print("   👉 Press Ctrl+C (or Cmd+C) -> Spoken aloud automatically!")
    print("   [Press Ctrl+C in this terminal to stop]")
    print("=" * 65)

    last_text = get_clipboard_text()

    try:
        while True:
            time.sleep(poll_interval)
            current_text = get_clipboard_text().strip()

            if current_text and current_text != last_text:
                last_text = current_text
                # Only speak meaningful text
                if len(current_text) >= 2:
                    preview = current_text.replace("\n", " ")
                    if len(preview) > 75:
                        preview = preview[:72] + "..."
                    print(f"\n📋 Copied text detected ({len(current_text)} chars): \"{preview}\"")
                    speak(
                        text=current_text,
                        voice=voice,
                        style=style,
                        custom_prompt=custom_prompt,
                        api_key=api_key,
                    )
    except KeyboardInterrupt:
        print("\n🛑 Clipboard listener stopped.")


def run_hotkey_listener(
    voice: str = "Puck",
    style: str = "energetic",
    custom_prompt: Optional[str] = None,
    api_key: Optional[str] = None,
) -> None:
    """
    Registers a global Windows shortcut (Ctrl+Alt+S).
    When triggered, sends Ctrl+C to copy selected text and immediately reads it aloud.
    """
    if sys.platform != "win32":
        print("❌ Global hotkey mode is currently only supported on Windows.", file=sys.stderr)
        print("   Use 'gemini-tts --listen' instead for cross-platform automatic reading.", file=sys.stderr)
        return

    import ctypes
    from ctypes import wintypes
    import subprocess

    user32 = ctypes.windll.user32
    MOD_CONTROL = 0x0002
    MOD_ALT = 0x0001
    VK_S = 0x53
    HOTKEY_ID = 101

    if not user32.RegisterHotKey(None, HOTKEY_ID, MOD_CONTROL | MOD_ALT, VK_S):
        print("❌ Could not register hotkey Ctrl+Alt+S. Another instance may be running.", file=sys.stderr)
        return

    print("=" * 65)
    print("⚡ GEMINI GLOBAL HOTKEY ACTIVE: Ctrl + Alt + S")
    print(f"   Voice: {voice} | Style: {style}")
    print("   👉 Highlight any text on screen.")
    print("   👉 Press Ctrl + Alt + S -> Text is copied and spoken immediately!")
    print("   [Press Ctrl+C in this terminal to stop]")
    print("=" * 65)

    try:
        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == 0x0312:  # WM_HOTKEY
                # Simulate Ctrl+C
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command",
                     "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('^c')"],
                    capture_output=True
                )
                time.sleep(0.12)
                text = get_clipboard_text().strip()
                if text:
                    print(f"\n⚡ Hotkey triggered! ({len(text)} chars)")
                    speak(
                        text=text,
                        voice=voice,
                        style=style,
                        custom_prompt=custom_prompt,
                        api_key=api_key,
                    )
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
    except KeyboardInterrupt:
        pass
    finally:
        user32.UnregisterHotKey(None, HOTKEY_ID)
        print("\n🛑 Hotkey listener stopped.")


def watch_file(
    filepath: str,
    voice: str = "Puck",
    style: str = "energetic",
    custom_prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    poll_interval: float = 1.0,
) -> None:
    """Monitors a file and speaks new content as it is appended."""
    print(f"👁️  Watching file: {filepath} (Press Ctrl+C to stop)...")
    last_content = ""
    last_mtime = 0.0

    if os.path.exists(filepath):
        last_mtime = os.path.getmtime(filepath)
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            last_content = f.read()

    try:
        while True:
            time.sleep(poll_interval)
            if not os.path.exists(filepath):
                continue
            mtime = os.path.getmtime(filepath)
            if mtime <= last_mtime:
                continue
            last_mtime = mtime
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            if content != last_content:
                new_text = content[len(last_content):].strip()
                if new_text:
                    print(f"\n📄 New file content detected ({len(new_text)} chars)...")
                    speak(
                        text=new_text,
                        voice=voice,
                        style=style,
                        custom_prompt=custom_prompt,
                        api_key=api_key,
                    )
                last_content = content
    except KeyboardInterrupt:
        print("\n🛑 File watcher stopped.")
