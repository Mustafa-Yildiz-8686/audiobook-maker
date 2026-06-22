# 🎧 Audiobook Maker

Convert any text file into a natural-sounding audiobook using Microsoft Edge's neural text-to-speech engine — completely free, no API key required.

## Features

- 🗣️ **High-quality neural voices** — powered by [Edge TTS](https://github.com/rany2/edge-tts) with 300+ voices in 60+ languages
- ⚡ **Async chunk generation** — processes multiple text chunks concurrently for speed
- 🔄 **Automatic retry** — retries failed chunks up to 3 times with configurable delay
- 🎵 **Natural pauses** — inserts short silence between chunks for smoother listening
- 🧹 **Auto cleanup** — removes temporary files after merging
- 📖 **Smart text splitting** — splits by paragraph boundaries to avoid cutting mid-sentence

## Prerequisites

- **Python 3.8+**
- **ffmpeg** — must be installed and available in your PATH
  ```bash
  # Ubuntu / Debian
  sudo apt install ffmpeg

  # macOS
  brew install ffmpeg

  # Windows (via Chocolatey)
  choco install ffmpeg
  ```

## Installation

```bash
git clone https://github.com/Mustafa-Yildiz-8686/audiobook-maker.git
cd audiobook-maker

python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

## Usage

1. Place your text file in the project folder and name it `book.txt`
2. Run the script:
   ```bash
   python audiobook.py
   ```
3. Your audiobook will be saved as `book.mp3`

### Configuration

Edit the config section at the top of `audiobook.py`:

```python
INPUT_FILE = "book.txt"       # input text file
OUTPUT_FILE = "book.mp3"      # output audiobook file
VOICE = "en-GB-RyanNeural"    # TTS voice to use
MAX_CHARS = 3000              # max characters per chunk
PAUSE_DURATION = 0.5          # seconds of silence between chunks
MAX_RETRIES = 3               # retry attempts per chunk
RETRY_DELAY = 2               # seconds between retries
```

### Voice Tester

Not sure which voice to use? The included `tester.py` generates sample audio for multiple voices so you can compare:

```bash
python tester.py
```

Samples are saved to the `voice_tests/` folder. Edit the `VOICES` list in `tester.py` to try different options.

> **Tip:** Run `edge-tts --list-voices` to see all available voices.

## How It Works

1. **Split** — the input text is divided into chunks at paragraph boundaries (≤3000 chars each)
2. **Generate** — each chunk is sent to Edge TTS concurrently with async/await
3. **Merge** — ffmpeg concatenates all chunks with short pauses into a single MP3
4. **Cleanup** — temporary audio files are automatically removed

## License

MIT
