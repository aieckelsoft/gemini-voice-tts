# 🔊 Gemini Voice TTS

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Google AI Studio](https://img.shields.io/badge/Google%20AI%20Studio-Free%20Tier-green.svg)](https://aistudio.google.com/)

**Free, natural, and energetic Text-to-Speech powered by Google Gemini (AI Studio).**  
Uses Director-Prompting and inline Emotion Tags (`[excited]`, `[whisper]`, `(pause)`) for lively, authentic speech.

---

## ⚡ Quick Start (Hands-Free Live Mode)

### 1. Install
```bash
pip install git+https://github.com/aieckelsoft/gemini-voice-tts.git
```

### 2. Run Live Listener
```bash
tts -l
```
*(On first run, it will ask for your free [Google AI Studio API Key](https://aistudio.google.com/apikey) and save it permanently).*

### 3. Highlight & Speak!
1. **Highlight any text** in your browser, IDE, or chat.
2. Hold `Ctrl` and press `C` **twice quickly (`Ctrl + C + C`)**.
3. 🔊 **Gemini reads the passage aloud instantly!**
   - *Single `Ctrl+C` continues to work normally for regular copying.*

---

## 🎭 Emotion & Director Tags

Embed emotion cues in square brackets `[...]` or pauses in parentheses `(...)`:

```bash
tts "[excited] Der neue MCP ist jetzt verfügbar! (kurze Pause) [happy] Das spart uns richtig viel Zeit."
```

| Tag | Effect |
|---|---|
| `[excited]` | High energy & enthusiasm |
| `[energetic]` | Bold and dynamic |
| `[happy]` | Cheerful and warm |
| `[curious]` | Inquisitive & questioning |
| `[whisper]` | Soft and intimate |
| `[sarcastic]` | Dry / ironic inflection |
| `[fast]` | Faster tempo |
| `(kurze Pause)` | Natural conversational pause |

---

## 🎙️ Voices & Styles

```bash
# Choose voice (--voice) and style (--style)
tts --voice Puck --style energetic "Lass uns loslegen!"
```

| Voice | Character | Style Presets |
|---|---|---|
| **`Puck`** *(Default)* | Energetic, expressive, dynamic | **`energetic`** *(Default)*: Lively, vibrant intonation |
| **`Kore`** | Clear, professional, articulate | **`casual`**: Relaxed, conversational |
| **`Charon`** | Deep, authoritative, masculine | **`storyteller`**: Immersive audiobook narrator |
| **`Fenrir`** | Bold, commanding, powerful | **`tech`**: Crisp, precise technical delivery |
| **`Aoede`** | Warm, melodic, gentle | **`news`**: Clear broadcast anchor |
| **`Leda`** | Soft, calm, reassuring | **`raw`**: Direct text without director notes |
| **`Orus` / `Perseus` / `Zephyr`** | Grounded / Neutral / Modern | |

List all options: `tts --list-voices` or `tts --list-styles`

---

## 📊 Text Length & Auto-Chunking

* **Single Paragraphs:** Rendered instantly in ~1 second.
* **Full Pages & Long Documents:** Texts over 2,500 characters are **automatically split at sentence/paragraph boundaries**, synthesized chunk-by-chunk, and concatenated into a seamless audio stream. No token cutoffs!

---

## 🛠️ CLI Cheat Sheet

```bash
tts -l                                          # Live mode: reads on Double-Ctrl+C
tts                                             # Read current clipboard text
tts "Hallo Welt!"                               # Speak direct text
tts --voice Charon --style storyteller "Text"   # Custom voice & style
tts --file document.txt --output speech.wav     # Synthesize file to WAV
tts config --set-key <YOUR_KEY>                 # Update API key
```

---

## 🐍 Python Library

```python
from gemini_voice_tts import speak

# Direct speech
speak("[excited] Bereit für den nächsten Schritt!", voice="Puck", style="energetic")

# Save to file
speak("Dokumentation...", output_file="output.wav")
```

---

## 📄 License

MIT License © 2026 [AI eckelsoft](https://github.com/aieckelsoft).
