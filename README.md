# 🔊 Gemini Voice TTS

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Google AI Studio](https://img.shields.io/badge/Google%20AI%20Studio-Free%20Tier-green.svg)](https://aistudio.google.com/)

**Gemini Voice TTS** is a free, ultra-expressive, and natural Text-to-Speech (TTS) CLI tool and Python library powered by Google Gemini (Google AI Studio).

Unlike conventional flat robotic TTS engines, Gemini Voice TTS utilizes **Director-Prompting** and **native Emotion Tags** to deliver energetic, lively, and highly authentic speech synthesis with realistic pauses and natural rhythm.

---

## ✨ Features

- 🆓 **100% Free Tier:** Works with free API keys from [Google AI Studio](https://aistudio.google.com/apikey) (no credit card required).
- 🎭 **Emotion & Director Tags:** Full support for inline emotion cues (`[excited]`, `[whisper]`, `[happy]`) and natural pauses (`(kurze Pause)`).
- 🎧 **Live-Clipboard Listener (`tts --listen`):** Automatically speaks any text you copy with `Ctrl+C` in real-time.
- ⚡ **Global Hotkey (`Ctrl + Alt + S`):** Highlight text on any window and press shortcut to read aloud.
- 🎙️ **9 Expressive Voices:** `Puck` (dynamic/youthful), `Kore` (articulate/professional), `Charon` (deep/resonant), `Fenrir` (bold), etc.
- 🌍 **Cross-Platform:** Native support for Windows, macOS, and Linux.
- 🔒 **Zero Sensitive Data:** Clean configuration stored locally in `~/.gemini_tts/config.json`.
- 🐍 **Python Library:** Easy import into your own Python scripts and AI agent workflows.

---

## 📦 Installation

### Option 1: Install from GitHub
```bash
pip install git+https://github.com/aieckelsoft/gemini-voice-tts.git
```

### Option 2: Clone & Install Editable
```bash
git clone https://github.com/aieckelsoft/gemini-voice-tts.git
cd gemini-voice-tts
pip install -e .
```

---

## 🔑 First-Time Setup (API Key)

1. Get your **free** API key from **[Google AI Studio](https://aistudio.google.com/apikey)**.
2. Run `tts` or `gemini-tts` for the first time — the CLI will automatically guide you and save the key:
   ```bash
   tts
   ```
3. Or save it directly anytime:
   ```bash
   tts config --set-key YOUR_GEMINI_API_KEY
   ```

*(You can also set the `GEMINI_API_KEY` environment variable if preferred).*

---

## 🚀 Usage Guide

### 1. Read Current Clipboard
Simply highlight text, press `Ctrl+C`, and run:
```bash
tts
```

### 2. Live-Clipboard Listener (Hands-Free!)
Run this once in a background terminal:
```bash
tts -l
# or
tts --listen
```
👉 Now, whenever you highlight text in your browser, IDE, or chat and press **`Ctrl+C`**, it will be spoken aloud automatically!

### 3. Global Hotkey (Windows)
```bash
tts --hotkey
```
👉 Highlight any text on screen and press **`Ctrl + Alt + S`** to speak it instantly.

### 4. Direct Text Input
```bash
tts "Hallo! Das ist ein Test der Gemini Voice Bridge."
```

### 5. Emotion Tags & Director Cues
Add emotion cues in square brackets `[...]` or pauses in parentheses `(...)`:
```bash
tts "[excited] Der neue MCP ist jetzt als Tool verfügbar! (kurze Pause) [happy] Das spart uns richtig viel Zeit."
```

Supported emotion tags:
* `[excited]` – High energy & enthusiasm
* `[energetic]` – Bold and dynamic
* `[happy]` – Cheerful and warm
* `[curious]` – Inquisitive & questioning
* `[whisper]` – Soft and intimate
* `[sarcastic]` – Dry / ironic inflection
* `[fast]` – Accelerated tempo
* `(kurze Pause)` / `(pause)` – Natural timing break

---

## 🎙️ Available Voices (`--voice`)

| Voice | Tone & Character | Best For |
|---|---|---|
| **`Puck`** *(Default)* | Energetic, dynamic, expressive, youthful | Agent responses, gaming, casual speech |
| **`Kore`** | Clear, articulate, balanced, professional | Documentation, technical explanations |
| **`Charon`** | Deep, authoritative, masculine, resonant | Narration, dramatic content |
| **`Fenrir`** | Bold, commanding, powerful | Announcements, action |
| **`Aoede`** | Warm, melodic, gentle | Storytelling, friendly chats |
| **`Leda`** | Soft, soothing, calm | Relaxed reading, meditation |
| **`Orus`** | Grounded, steady, natural | Podcasts, news |
| **`Perseus`** | Crisp, neutral, precise | Tutorials, instructions |
| **`Zephyr`** | Light, breezy, modern | Quick prompts, UI voice |

List all voices:
```bash
tts --list-voices
```

---

## 🎭 Speech Style Presets (`--style`)

| Preset | Description |
|---|---|
| **`energetic`** *(Default)* | Enthusiastic, lively, vibrant German/English intonation |
| **`casual`** | Relaxed and friendly, like a chat with a teammate |
| **`storyteller`** | Immersive audiobook narrator style |
| **`tech`** | Crisp, confident, technical delivery |
| **`news`** | Articulate news broadcast style |
| **`raw`** | Direct text without prepended director notes |

```bash
tts --style storyteller "Es war einmal eine UEFN Arena..."
```

---

## 📊 Text Length & Auto-Chunking (How Much Text Can You Read?)

| Text Length | Single Request | With Gemini Voice TTS | Best For |
|---|---|---|---|
| **1 – 3 Paragraphs** (~500 – 2,500 chars) | ✅ Optimal | ⚡ Instant Render (~1–2s) | Agent responses, chat messages, UI prompts |
| **1 Full Page** (~3,000 – 5,000 chars) | ⚠️ Near API Token Limit | ⚡ 1–2 Chunks (Seamless) | Blog posts, articles, documentation pages |
| **Multi-Page Document** (10,000 – 50,000+ chars) | ❌ Exceeds single API turn | 🚀 **Auto-Chunking & Concatenation** | Full chapters, essays, long transcripts |

### How Auto-Chunking Works:
1. **Intelligent Splitting:** Texts exceeding ~2,500 characters are automatically split at paragraph boundaries (`\n\n`) or sentence endings (`. `, `! `, `? `). Thoughts and sentences are never cut in half.
2. **Audio Stitching:** Each chunk is synthesized sequentially, and the raw PCM audio frames are seamlessly concatenated into a single, continuous audio stream or WAV file.
3. **No Length Ceiling:** You can pass an entire document via `--file` or pipe without worrying about token cutoffs!

---

## 💾 Save Audio to File

```bash
tts "Welcome to our game!" --output welcome.wav
```

---

## 🐍 Python API

You can use Gemini Voice TTS directly inside your Python projects:

```python
from gemini_voice_tts import speak, synthesize

# 1. Speak directly through speakers
speak(
    text="[excited] System initialisiert und bereit!",
    voice="Puck",
    style="energetic"
)

# 2. Get WAV bytes
wav_data = synthesize("Hallo Welt!", voice="Kore")

# 3. Save to file
speak("Audio Nachricht", output_file="output.wav")
```

---

## 🛠️ CLI Cheat Sheet

```bash
# Read clipboard text
tts

# Speak specific text
tts "Your text here"

# Live clipboard watcher
tts --listen

# Windows global hotkey (Ctrl+Alt+S)
tts --hotkey

# Use a specific voice & style
tts --voice Charon --style storyteller "Deep story text..."

# Read from a file
tts --file notes.txt

# Save to .wav file
tts "Save me" --output speech.wav

# Pipe from stdin
echo "Pipeline text" | tts

# Configure API key
tts config --set-key <YOUR_KEY>
tts config --show
tts config --clear
```

---

## 📄 License

MIT License © 2026 [AI eckelsoft](https://github.com/aieckelsoft). Free for personal and commercial use.
