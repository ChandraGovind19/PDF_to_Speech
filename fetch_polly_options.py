import boto3
import json
import os

def get_polly_options():
    print("Starting Polly fetch...")
    try:
        # Check if boto3 is imported
        print("Boto3 version:", boto3.__version__)
        
        # Initialize client
        polly = boto3.client('polly', region_name='us-east-1')
        print("Client created.")
        
        voices = []
        next_token = None
        
        while True:
            if next_token:
                response = polly.describe_voices(NextToken=next_token)
            else:
                response = polly.describe_voices()
            
            voices.extend(response.get('Voices', []))
            next_token = response.get('NextToken')
            
            if not next_token:
                break
                
        print(f"Fetched {len(voices)} voices.")
        
        if not voices:
            print("No voices found. Check credentials/region.")
            return

        organized_voices = {}
        for voice in voices:
            lang_code = voice['LanguageCode']
            lang_name = voice.get('LanguageName', 'Unknown')
            
            if lang_code not in organized_voices:
                organized_voices[lang_code] = {
                    'language': lang_name,
                    'voices': []
                }
            
            organized_voices[lang_code]['voices'].append({
                'Id': voice['Id'],
                'Gender': voice.get('Gender', 'Unknown'),
                'SupportedEngines': voice.get('SupportedEngines', [])
            })

        # Save to a file to ensure we get the data
        with open('polly_voices.json', 'w') as f:
            json.dump(organized_voices, f, indent=2)
        print("Saved to polly_voices.json")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    get_polly_options()
