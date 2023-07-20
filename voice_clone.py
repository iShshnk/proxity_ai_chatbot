import requests
import app_config
import json

url = "https://api.elevenlabs.io/v1/voices/add"

headers = {
  "Accept": "application/json",
  "xi-api-key": app_config.ELEVENLABS_API_KEY
}

def get_voice_clone(name, samples):
    data = {
        'name': name,
        'labels': '{"accent": "American"}',
        'description': 'Voice description'
    }

    # files = [
    #     ('files', ('sample1.mp3', open('sample1.mp3', 'rb'), 'audio/mpeg')),
    #     ('files', ('sample2.mp3', open('sample2.mp3', 'rb'), 'audio/mpeg'))
    # ]
    
    files = []
    
    i = 0
    
    for sample in samples:
        files.append(('files', (f"sample{i}.mp3", open(sample, 'rb'), 'audio/mpeg')))
        i+=1

    response = requests.post(url, headers=headers, data=data, files=files)
    
    response_data = response.json()
    
    print(response_data)
    return response_data["voice_id"]