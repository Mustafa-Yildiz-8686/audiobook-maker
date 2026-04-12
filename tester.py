import asyncio
import edge_tts
import os

# -------- CONFIG --------
TEXT = """The alarms screamed in a jagged, rhythmic pulse as the airlock’s reinforced glass 
began to spiderweb under the crushing pressure of the deep-sea abyss. Elias lunged 
for the manual override, his fingers slick with hydraulic fluid and sweat, while the 
roar of the encroaching ocean muffled the frantic pounding of his own heart. Just as the first 
crystalline shards shattered inward, he slammed the lever home, the heavy titanium bulkhead 
hissing shut with a fraction of a second to spare. Silence suddenly flooded the chamber, 
thick and heavy, broken only by the low, predatory hum of something massive circling the exterior of the hull."""

VOICES = [
    "en-US-AriaNeural",
    "en-US-GuyNeural",
    "en-GB-RyanNeural",
    # add more voices here
]

OUTPUT_DIR = "voice_tests"
# ------------------------

async def generate_voice(voice, text, output_file):
    communicate = edge_tts.Communicate(text, voice=voice)
    await communicate.save(output_file)

async def main():
    # Create output folder if not exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    tasks = []

    for voice in VOICES:
        filename = f"{voice}.mp3"
        output_path = os.path.join(OUTPUT_DIR, filename)

        print(f"Generating: {voice}")
        tasks.append(generate_voice(voice, TEXT, output_path))

    # Run all tasks asynchronously
    await asyncio.gather(*tasks)

    print("Done. Check the 'voice_tests' folder.")

if __name__ == "__main__":
    asyncio.run(main())