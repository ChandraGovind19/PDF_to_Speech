import sys
import os
import io
import boto3
from pydub import AudioSegment

MAX_CHARS = 3000  # AWS Polly max text length per request
MONTHLY_CHAR_LIMIT = 4_500_000  # Safety limit to stay under free tier (out of 5M)

def chunk_text(text, chunk_size=MAX_CHARS):
    """Split text into chunks without breaking words."""
    words = text.split()
    chunks, current_chunk = [], ""

    for word in words:
        if len(current_chunk) + len(word) + 1 <= chunk_size:
            current_chunk += (" " if current_chunk else "") + word
        else:
            chunks.append(current_chunk)
            current_chunk = word
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def convert_text_to_speech(text, voice_id="Joanna", engine="neural"):
    polly = boto3.client("polly", region_name="us-east-1")
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat="mp3",
        VoiceId=voice_id,
        Engine=engine
    )
    return io.BytesIO(response["AudioStream"].read())

def read_text_from_file(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tts_app.py input.txt")
        sys.exit(1)

    input_file = sys.argv[1]
    try:
        text = read_text_from_file(input_file)
        if not text:
            raise ValueError("The input text file is empty.")

        total_chars = len(text)
        print(f"Total characters in file: {total_chars}")

        # SAFEGUARD: Stop if over monthly free-tier safe limit
        if total_chars > MONTHLY_CHAR_LIMIT:
            raise ValueError(
                f"File has {total_chars:,} characters which exceeds your monthly safety limit "
                f"({MONTHLY_CHAR_LIMIT:,}).\nReduce file size to avoid charges."
            )

        chunks = chunk_text(text)
        print(f"Total chunks to process: {len(chunks)}")

        final_audio = AudioSegment.silent(duration=0)  # Start empty

        for i, chunk in enumerate(chunks, start=1):
            print(f"Processing chunk {i}/{len(chunks)} ({len(chunk)} chars)...")
            audio_stream = convert_text_to_speech(chunk)
            segment = AudioSegment.from_file(audio_stream, format="mp3")
            final_audio += segment

        output_path = "final_polly_output.mp3"
        final_audio.export(output_path, format="mp3")
        print(f"Final audio saved as {output_path}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
