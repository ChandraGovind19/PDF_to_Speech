
import boto3
import io
import concurrent.futures
from pydub import AudioSegment

MAX_CHARS = 3000  # AWS Polly max text length per request
MONTHLY_CHAR_LIMIT = 4_500_000  # Safety limit

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

def convert_chunk_to_speech(chunk, voice_id="Joanna", engine="neural"):
    """
    Converts a single text chunk to speech using AWS Polly.
    """
    try:
        polly = boto3.client("polly", region_name="us-east-1")
        response = polly.synthesize_speech(
            Text=chunk,
            OutputFormat="mp3",
            VoiceId=voice_id,
            Engine=engine
        )
        return io.BytesIO(response["AudioStream"].read())
    except Exception as e:
        print(f"Error converting chunk: {e}")
        return None  # Or raise, depending on desired behavior

def text_to_speech_service(text, output_path, voice_id="Joanna", engine="neural"):
    """
    Converts text to speech using parallel processing for chunks.
    """
    total_chars = len(text)
    if total_chars > MONTHLY_CHAR_LIMIT:
        raise ValueError(
            f"Text length ({total_chars:,}) exceeds monthly safety limit ({MONTHLY_CHAR_LIMIT:,})."
        )

    chunks = chunk_text(text)
    print(f"Total chunks to process: {len(chunks)}")
    print(f"Using Voice: {voice_id}, Engine: {engine}")
    
    # Placeholder for ordered audio segments
    audio_segments = [None] * len(chunks)

    # Use ThreadPoolExecutor for parallel processing
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_index = {
            executor.submit(convert_chunk_to_speech, chunk, voice_id, engine): i 
            for i, chunk in enumerate(chunks)
        }
        
        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                audio_stream = future.result()
                if audio_stream:
                    audio_segments[index] = AudioSegment.from_file(audio_stream, format="mp3")
                else:
                    raise RuntimeError(f"Failed to convert chunk {index}")
            except Exception as e:
                print(f"Chunk {index} generated an exception: {e}")
                # You might want to handle partial failures or retry logic here
                raise e

    # Combine all segments
    final_audio = AudioSegment.silent(duration=0)
    for segment in audio_segments:
        if segment:
            final_audio += segment
        else:
             print("Warning: Missing audio segment during assembly.")

    final_audio.export(output_path, format="mp3")
    return output_path
