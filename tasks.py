import os
from services.pdf_service import extract_text_from_pdf
from services.tts_service import text_to_speech_service

def process_pdf_to_audio(pdf_path, audio_path, voice_id, engine):
    """
    Background job to process the PDF and generate audio.
    """
    try:
        # 1. Extract Text
        text = extract_text_from_pdf(pdf_path)
        if not text.strip():
            return {"error": "Could not extract text from PDF. It might be an image-based PDF or empty."}

        # 2. Convert to Speech
        text_to_speech_service(text, audio_path, voice_id=voice_id, engine=engine)
        
        return {"audio_file": os.path.basename(audio_path)}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
    finally:
        # Cleanup uploaded PDF
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
