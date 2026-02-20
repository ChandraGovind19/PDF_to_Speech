
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
import uuid
from services.pdf_service import extract_text_from_pdf
from services.tts_service import text_to_speech_service
import redis
from rq import Queue

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this for production
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['AUDIO_FOLDER'] = 'static/audio'

# Setup Redis Queue
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis_conn = redis.from_url(redis_url)
q = Queue(connection=redis_conn)
app.secret_key = 'supersecretkey'  # Change this for production
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['AUDIO_FOLDER'] = 'static/audio'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)

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
            
            # Enqueue the background job
            job = q.enqueue('tasks.process_pdf_to_audio', pdf_path, audio_path, voice_id, engine, job_timeout=3600)
            
            return {"job_id": job.get_id()}

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": str(e)}, 500
    else:
        return {"error": "Invalid file type. Please upload a PDF."}, 400

@app.route('/status/<job_id>')
def job_status(job_id):
    job = q.fetch_job(job_id)
    if job is None:
        return {"status": "failed", "error": "Job not found"}
    
    if job.is_finished:
        result = job.result
        if "error" in result:
            return {"status": "failed", "error": result["error"]}
        return {
            "status": "finished", 
            "audio_file": result["audio_file"]
        }
    elif job.is_failed:
        return {"status": "failed", "error": "Job failed during execution"}
    else:
        return {"status": "processing"}

if __name__ == '__main__':
    app.run(debug=True)
