"""
Audiobook Generator using Edge TTS

Usage:
1. Put your text file in the same folder as this script and name it 'book.txt'.
2. Set the VOICE variable to your preferred voice (default: 'en-GB-RyanNeural').
3. Run the script:
       python audiobook.py
4. The script will:
       - Split the text into natural chunks
       - Generate MP3 files for each chunk asynchronously
       - Add small pauses between chunks for smoother listening
       - Merge all parts into a single 'book.mp3'
       - Clean up temporary audio files automatically
5. The final audiobook will be saved as 'book.mp3' in the same folder.

Requirements:
- Python 3.8+ with edge-tts installed in a virtual environment
- ffmpeg installed for merging audio files
"""


import asyncio
import edge_tts
import os
import subprocess
from pathlib import Path

# -------- CONFIG --------
INPUT_FILE = "book.txt"
OUTPUT_FILE = "book.mp3"
VOICE = "en-GB-RyanNeural"
MAX_CHARS = 3000
PAUSE_DURATION = 0.5
TEMP_DIR = "temp_audio"
MAX_RETRIES = 3  # number of retry attempts per chunk
RETRY_DELAY = 2  # seconds to wait between retries
# ------------------------

def split_text(text, max_chars):
    import re
    # Normalize line endings
    text = text.replace("\r\n", "\n")
    
    # Detect paragraph separator dynamically
    if "\n\n" in text:
        paragraphs = text.split("\n\n")
    else:
        # Fall back to single newlines if double newlines are absent
        paragraphs = [p for p in text.split("\n") if p.strip()]
        
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        # If a single paragraph is longer than max_chars, split it into sentences
        if len(para) > max_chars:
            sub_chunks = []
            # Match sentence endings followed by space or end of string
            raw_sentences = re.split(r"(?<=[.!?])\s+", para)
            current_sub = ""
            for sentence in raw_sentences:
                if len(current_sub) + len(sentence) + 1 <= max_chars:
                    current_sub = (current_sub + " " + sentence).strip()
                else:
                    if current_sub:
                        sub_chunks.append(current_sub)
                    current_sub = sentence
            if current_sub:
                sub_chunks.append(current_sub)
                
            # Process sub-chunks
            for sub in sub_chunks:
                if len(current_chunk) + len(sub) + 2 <= max_chars:
                    current_chunk = (current_chunk + "\n\n" + sub).strip()
                else:
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    current_chunk = sub
        else:
            if len(current_chunk) + len(para) + 2 <= max_chars:
                current_chunk = (current_chunk + "\n\n" + para).strip()
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = para
                
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
        
    return chunks

async def generate_chunk(text, index, total):
    filename = os.path.join(TEMP_DIR, f"part_{index}.mp3")
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            print(f"[{index+1}/{total}] Generating chunk: {filename} (Attempt {attempt+1})")
            communicate = edge_tts.Communicate(text, voice=VOICE)
            await communicate.save(filename)
            return filename
        except Exception as e:
            attempt += 1
            print(f"Error generating chunk {index}: {e}")
            if attempt < MAX_RETRIES:
                print(f"Retrying in {RETRY_DELAY}s...")
                await asyncio.sleep(RETRY_DELAY)
            else:
                print(f"Failed to generate chunk {index} after {MAX_RETRIES} attempts.")
                return None

async def generate_all(chunks):
    tasks = [generate_chunk(chunk, i, len(chunks)) for i, chunk in enumerate(chunks)]
    results = await asyncio.gather(*tasks)
    # filter out any None (failed) chunks
    return [r for r in results if r is not None]

def merge_audio(file_list):
    list_file = os.path.join(TEMP_DIR, "files.txt")

    # generate a short silent pause file for gaps between chunks
    pause_file = os.path.join(TEMP_DIR, "pause.mp3")
    if not os.path.exists(pause_file):
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"anullsrc=r=24000:cl=mono",
            "-t", str(PAUSE_DURATION),
            pause_file
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

    # write the concat list with absolute paths to avoid resolution issues
    with open(list_file, "w") as f:
        for file in file_list:
            f.write(f"file '{os.path.abspath(file)}'\n")
            f.write(f"file '{os.path.abspath(pause_file)}'\n")

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        OUTPUT_FILE
    ], stdin=subprocess.DEVNULL)
    print(f"Final audiobook saved as: {OUTPUT_FILE}")

def cleanup_temp():
    for file in Path(TEMP_DIR).glob("*"):
        file.unlink()
    os.rmdir(TEMP_DIR)

async def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    os.makedirs(TEMP_DIR, exist_ok=True)

    chunks = split_text(text, MAX_CHARS)
    print(f"Total chunks: {len(chunks)}")

    file_list = await generate_all(chunks)
    if not file_list:
        print("No chunks were generated. Exiting.")
        return

    merge_audio(file_list)
    cleanup_temp()

if __name__ == "__main__":
    asyncio.run(main())