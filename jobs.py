import sqlite3
import uuid
import os

DB_PATH = 'jobs.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            audio_file TEXT,
            error TEXT
        )
    ''')
    conn.commit()
    conn.close()

def create_job():
    job_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO jobs (id, status) VALUES (?, ?)', (job_id, 'queued'))
    conn.commit()
    conn.close()
    return job_id

def update_job_status(job_id, status, audio_file=None, error=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE jobs 
        SET status = ?, audio_file = ?, error = ?
        WHERE id = ?
    ''', (status, audio_file, error, job_id))
    conn.commit()
    conn.close()

def get_job_status(job_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT status, audio_file, error FROM jobs WHERE id = ?', (job_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "status": row[0],
            "audio_file": row[1],
            "error": row[2]
        }
    return None
