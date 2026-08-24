"""
Background listeners:
- Live clipboard listener with Double-Ctrl+C (Ctrl+C+C) trigger.
- Global Windows hotkey listener (Ctrl+Alt+S).
- File watcher.
"""

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
    double_copy_timeout: float = 0.55,
) -> None:
    """
    Monitors the clipboard for a Double Ctrl+C (Ctrl+C+C) trigger.
    Single Ctrl+C behaves normally (for standard copying).
    Rapid Double Ctrl+C immediately triggers TTS.
    """
    print("=" * 65)
    print("🎧 GEMINI LIVE-CLIPBOARD LISTENER (Hands-Free)")
    print(f"   Voice: {voice} | Style: {style}")
    print("   👉 Highlight text & press Double-Ctrl+C (Ctrl + C + C) to speak!")
    print("   ℹ️  Single Ctrl+C works normally without triggering TTS.")
    print("   [Press Ctrl+C in this terminal to stop]")
    print("=" * 65)

    # Windows sequence counter if available
    use_win_seq = False
    user32 = None
    last_seq = 0
    if sys.platform == "win32":
        try:
            import ctypes
            user32 = ctypes.windll.user32
            last_seq = user32.GetClipboardSequenceNumber()
            use_win_seq = True
        except Exception:
            pass

    last_copy_time = 0.0

    try:
        while True:
            time.sleep(0.04)
            copy_event = False

            if use_win_seq:
                current_seq = user32.GetClipboardSequenceNumber()
                if current_seq != last_seq:
                    last_seq = current_seq
                    copy_event = True
            else:
                # Fallback for non-Windows
                current_text = get_clipboard_text()
                if current_text:
                    copy_event = True

            if copy_event:
                now = time.time()
                elapsed = now - last_copy_time
                last_copy_time = now

                # Double copy detected within the timeout window!
                if 0.04 < elapsed < double_copy_timeout:
                    text = get_clipboard_text().strip()
                    if len(text) >= 2:
                        preview = text.replace("\n", " ")
                        if len(preview) > 75:
                            preview = preview[:72] + "..."
                        print(f"\n⚡ Double-Ctrl+C detected ({len(text)} chars): \"{preview}\"")
                        speak(
                            text=text,
                            voice=voice,
                            style=style,
                            custom_prompt=custom_prompt,
                            api_key=api_key,
                        )
                        # Reset timer so a third accidental tap doesn't immediately refire
                        last_copy_time = 0.0

    except KeyboardInterrupt:
        print("\n🛑 Live listener stopped.")


def run_hotkey_listener(
    voice: str = "Puck",
    style: str = "energetic",
    custom_prompt: Optional[str] = None,
    api_key: Optional[str] = None,
) -> None:
    """Registers a global Windows shortcut (Ctrl+Alt+S) to speak highlighted text."""
    if sys.platform != "win32":
        print("❌ Global hotkey mode is only supported on Windows. Use 'gemini-tts --listen' instead.", file=sys.stderr)
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
        print("❌ Could not register hotkey Ctrl+Alt+S.", file=sys.stderr)
        return

    print("=" * 65)
    print("⚡ GEMINI GLOBAL HOTKEY: Ctrl + Alt + S")
    print(f"   Voice: {voice} | Style: {style}")
    print("   👉 Highlight text anywhere & press Ctrl + Alt + S to speak.")
    print("   [Press Ctrl+C in this terminal to stop]")
    print("=" * 65)

    try:
        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == 0x0312:  # WM_HOTKEY
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command",
                     "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('^c')"],
                    capture_output=True
                )
                time.sleep(0.12)
                text = get_clipboard_text().strip()
                if text:
                    print(f"\n⚡ Hotkey triggered ({len(text)} chars)")
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
    import os
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
                    print(f"\n📄 New file content ({len(new_text)} chars)...")
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
