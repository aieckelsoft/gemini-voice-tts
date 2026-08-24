"""
Cross-platform audio playback module for Gemini Voice TTS.
Plays WAV audio cleanly across Windows, macOS, and Linux without blocking.
"""

import io
import os
import subprocess
import sys
import tempfile
import time
import wave


def pcm_to_wav(pcm_data: bytes, sample_rate: int = 24000,
               channels: int = 1, sample_width: int = 2) -> bytes:
    """Converts raw 16-bit PCM audio bytes into a standard WAV container."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)
    return buf.getvalue()


def play_wav_bytes(wav_bytes: bytes, async_play: bool = False) -> None:
    """Plays WAV audio bytes on the default system audio output."""
    tmp_path = os.path.join(tempfile.gettempdir(), f"gemini_tts_{int(time.time() * 1000)}.wav")
    with open(tmp_path, "wb") as f:
        f.write(wav_bytes)

    # ---------------- Windows Playback ----------------
    if sys.platform == "win32":
        # 1. ffplay
        try:
            cmd = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", tmp_path]
            if async_play:
                subprocess.Popen(cmd)
                return
            result = subprocess.run(cmd, timeout=180, capture_output=True)
            if result.returncode == 0:
                _safe_delete(tmp_path)
                return
        except (FileNotFoundError, Exception):
            pass

        # 2. PowerShell SoundPlayer
        try:
            ps_script = f'$p = New-Object System.Media.SoundPlayer("{tmp_path}"); $p.PlaySync();'
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                timeout=180, capture_output=True
            )
            if result.returncode == 0:
                _safe_delete(tmp_path)
                return
        except Exception:
            pass

        # 3. Standard Windows System Launcher
        try:
            subprocess.Popen(["powershell", "-NoProfile", "-Command", f'Start-Process "{tmp_path}"'])
            return
        except Exception:
            pass

    # ---------------- macOS Playback ----------------
    elif sys.platform == "darwin":
        try:
            cmd = ["afplay", tmp_path]
            if async_play:
                subprocess.Popen(cmd)
                return
            result = subprocess.run(cmd, timeout=180, capture_output=True)
            if result.returncode == 0:
                _safe_delete(tmp_path)
                return
        except (FileNotFoundError, Exception):
            pass

    # ---------------- Linux Playback ----------------
    elif sys.platform.startswith("linux"):
        for player in (["paplay", tmp_path], ["aplay", "-q", tmp_path], ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", tmp_path]):
            try:
                if async_play:
                    subprocess.Popen(player)
                    return
                result = subprocess.run(player, timeout=180, capture_output=True)
                if result.returncode == 0:
                    _safe_delete(tmp_path)
                    return
            except (FileNotFoundError, Exception):
                continue

    # Fallback message
    print(f"🔊 Audio saved to: {tmp_path}", file=sys.stderr)


def _safe_delete(path: str) -> None:
    """Safely removes temporary audio file."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
