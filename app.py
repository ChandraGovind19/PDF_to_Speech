
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
import threading
import uuid
from jobs import init_db, create_job, update_job_status, get_job_status
from services.pdf_service import extract_text_from_pdf
from services.tts_service import text_to_speech_service

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this for production
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['AUDIO_FOLDER'] = 'static/audio'

# Initialize local SQLite job tracker
init_db()

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)

def process_pdf_thread(job_id, pdf_path, audio_path, voice_id, engine):
    """Background thread to process the PDF and update SQLite DB."""
    update_job_status(job_id, 'processing')
    try:
        # 1. Extract Text
        text = extract_text_from_pdf(pdf_path)
        if not text.strip():
            update_job_status(job_id, 'failed', error="Could not extract text. Image-based PDF or empty.")
            return

        # 2. Convert to Speech
        text_to_speech_service(text, audio_path, voice_id=voice_id, engine=engine)
        
        # Success
        audio_filename = os.path.basename(audio_path)
        update_job_status(job_id, 'finished', audio_file=audio_filename)

    except Exception as e:
        import traceback
        traceback.print_exc()
        update_job_status(job_id, 'failed', error=str(e))
    finally:
        # Cleanup uploaded PDF
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

@app.route('/')
def index():
    audio_file = request.args.get('audio_file')
    filename = request.args.get('filename')
    return render_template('index.html', audio_file=audio_file, filename=filename)

@app.route('/convert', methods=['GET', 'POST'])
def convert():
    if request.method == 'GET':
        return redirect(url_for('index'))

    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and file.filename.endswith('.pdf'):
        try:
            # Save uploaded file
            filename = str(uuid.uuid4()) + "_" + file.filename
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(pdf_path)
            
            audio_filename = os.path.splitext(filename)[0] + ".mp3"
            audio_path = os.path.join(app.config['AUDIO_FOLDER'], audio_filename)
            
            # Get Voice Options
            voice_id = request.form.get('voice', 'Joanna')
            engine = request.form.get('engine', 'neural')
            
            # Create a job in DB
            job_id = create_job()

            # Start background thread
            thread = threading.Thread(
                target=process_pdf_thread,
                args=(job_id, pdf_path, audio_path, voice_id, engine)
            )
            thread.start()
            
            return {"job_id": job_id}

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": str(e)}, 500
    else:
        return {"error": "Invalid file type. Please upload a PDF."}, 400

@app.route('/status/<job_id>')
def job_status(job_id):
    job = get_job_status(job_id)
    if job is None:
        return {"status": "failed", "error": "Job not found"}
    
    return job

if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get('PORT', 5001)))
