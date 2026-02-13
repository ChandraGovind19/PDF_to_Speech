import requests



resp = requests.post("https://af0c-35-227-165-90.ngrok-free.app/tts", json={"text": "Hello world"})
with open("output_1.wav", "wb") as f:
    f.write(resp.content)


print("Audio saved as output.wav")
