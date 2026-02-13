
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
import uuid
from services.pdf_service import extract_text_from_pdf
from services.tts_service import text_to_speech_service

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this for production
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['AUDIO_FOLDER'] = 'static/audio'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

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
            
            # 1. Extract Text
            try:
                text = extract_text_from_pdf(pdf_path)
                if not text.strip():
                     flash('Could not extract text from PDF. It might be an image-based PDF or empty.')
                     return redirect(url_for('index'))
            except Exception as e:
                import traceback
                traceback.print_exc()
                flash(f"Error extracting text: {str(e)}")
                return redirect(url_for('index'))

            # 2. Convert to Speech
            audio_filename = os.path.splitext(filename)[0] + ".mp3"
            audio_path = os.path.join(app.config['AUDIO_FOLDER'], audio_filename)
            
            # Get Voice Options
            voice_id = request.form.get('voice', 'Joanna')
            engine = request.form.get('engine', 'neural')
            
            try:
                text_to_speech_service(text, audio_path, voice_id=voice_id, engine=engine)
            except Exception as e:
                import traceback
                traceback.print_exc()
                flash(f"Error converting to speech: {str(e)}")
                return redirect(url_for('index'))

            return render_template('index.html', audio_file=audio_filename, filename=file.filename)

        except Exception as e:
            import traceback
            traceback.print_exc()
            flash(f"An unexpected error occurred: {str(e)}")
            return redirect(url_for('index'))
        finally:
            # Cleanup uploaded PDF
            if 'pdf_path' in locals() and os.path.exists(pdf_path):
                os.remove(pdf_path)
    else:
        flash('Invalid file type. Please upload a PDF.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
