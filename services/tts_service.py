
import boto3
from botocore.config import Config
import concurrent.futures

MAX_CHARS = 3000  # AWS Polly max text length per request
MONTHLY_CHAR_LIMIT = 4_500_000  # Safety limit

# Configure AWS client for robust retries (adaptive mode handles rate limits)
polly_config = Config(
    retries = {
        'max_attempts': 10,
        'mode': 'adaptive'
    }
)

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
        polly = boto3.client("polly", region_name="us-east-1", config=polly_config)
        response = polly.synthesize_speech(
            Text=chunk,
            OutputFormat="mp3",
            VoiceId=voice_id,
            Engine=engine
        )
        return response["AudioStream"].read()
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

    # Use ThreadPoolExecutor for parallel processing (limit to 5 to avoid AWS rate limits)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_index = {
            executor.submit(convert_chunk_to_speech, chunk, voice_id, engine): i 
            for i, chunk in enumerate(chunks)
        }
        
        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                audio_bytes = future.result()
                if audio_bytes:
                    audio_segments[index] = audio_bytes
                else:
                    raise RuntimeError(f"Failed to convert chunk {index}")
            except Exception as e:
                print(f"Chunk {index} generated an exception: {e}")
                # You might want to handle partial failures or retry logic here
                raise e

    # Combine all segments directly (binary concatenation)
    with open(output_path, 'wb') as f:
        for segment in audio_segments:
            if segment:
                f.write(segment)
            else:
                 print("Warning: Missing audio segment during assembly.")

    return output_path
