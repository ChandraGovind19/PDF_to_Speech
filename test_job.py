import time
import requests

API_URL = "http://127.0.0.1:5001"
FILE_PATH = "dummy.pdf"

print(f"Uploading {FILE_PATH}...")
with open(FILE_PATH, 'rb') as f:
    files = {'file': (FILE_PATH, f, 'application/pdf')}
    data = {'voice': 'Joanna', 'engine': 'neural'}
    resp = requests.post(f"{API_URL}/convert", files=files, data=data)

if resp.status_code != 200:
    print(f"Failed to submit job: {resp.text}")
    exit(1)

job_id = resp.json().get('job_id')
print(f"Job ID received: {job_id}")
print("Polling status...")

while True:
    status_resp = requests.get(f"{API_URL}/status/{job_id}")
    status_data = status_resp.json()
    
    status = status_data.get('status')
    print(f"Current status: {status}")
    
    if status == 'finished':
        print(f"Success! Audio file generated: {status_data.get('audio_file')}")
        break
    elif status == 'failed':
        print(f"Job failed: {status_data.get('error')}")
        break
        
    time.sleep(3)
