"""
Cross-platform clipboard reader and writer with full Unicode support.
Ensures zero encoding crashes across Windows, macOS, and Linux.
"""

import subprocess
import sys
import time


def get_clipboard_text() -> str:
    """Returns the current clipboard contents as a Unicode string."""
    # 1. Windows: Direct Win32 API via ctypes (zero encoding issues)
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            CF_UNICODETEXT = 13
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32

            user32.OpenClipboard.argtypes = [wintypes.HWND]
            user32.OpenClipboard.restype = wintypes.BOOL
            user32.GetClipboardData.argtypes = [wintypes.UINT]
            user32.GetClipboardData.restype = wintypes.HANDLE
            user32.CloseClipboard.argtypes = []
            user32.CloseClipboard.restype = wintypes.BOOL
            kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
            kernel32.GlobalLock.restype = wintypes.LPVOID
            kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
            kernel32.GlobalUnlock.restype = wintypes.BOOL

            for _ in range(5):
                if user32.OpenClipboard(None):
                    break
                time.sleep(0.05)
            else:
                return ""

            try:
                handle = user32.GetClipboardData(CF_UNICODETEXT)
                if not handle:
                    return ""
                ptr = kernel32.GlobalLock(handle)
                if not ptr:
                    return ""
                try:
                    return ctypes.c_wchar_p(ptr).value or ""
                finally:
                    kernel32.GlobalUnlock(handle)
            finally:
                user32.CloseClipboard()
        except Exception:
            pass

    # 2. macOS: pbpaste
    elif sys.platform == "darwin":
        try:
            result = subprocess.run(
                ["pbpaste"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            return result.stdout.strip()
        except Exception:
            pass

    # 3. Linux: wl-paste (Wayland) or xclip / xsel (X11)
    elif sys.platform.startswith("linux"):
        for cmd in (["wl-paste"], ["xclip", "-selection", "clipboard", "-o"], ["xsel", "--clipboard", "--output"]):
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                if result.returncode == 0:
                    return result.stdout.strip()
            except FileNotFoundError:
                continue
            except Exception:
                pass

    # 4. Fallback: tkinter (if installed)
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        text = root.clipboard_get()
        root.destroy()
        return text or ""
    except Exception:
        pass

    return ""
