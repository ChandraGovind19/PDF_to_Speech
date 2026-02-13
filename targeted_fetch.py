import boto3
import json

def fetch_targeted():
    polly = boto3.client('polly', region_name='us-east-1')
    
    langs = ['hi-IN', 'ta-IN']
    results = {}
    
    for lang in langs:
        try:
            response = polly.describe_voices(LanguageCode=lang)
            voices = response.get('Voices', [])
            # Simplify for readability
            simple_voices = []
            for v in voices:
                simple_voices.append({
                    'Id': v['Id'],
                    'Gender': v.get('Gender'),
                    'Engines': v.get('SupportedEngines')
                })
            results[lang] = simple_voices
        except Exception as e:
            results[lang] = str(e)
            
    with open('targeted_voices.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("Saved to targeted_voices.json")

if __name__ == "__main__":
    fetch_targeted()
