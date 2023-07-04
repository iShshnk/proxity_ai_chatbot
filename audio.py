import app_config
import requests
import subprocess

url = 'https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB/stream'
headers = {
    'accept': '*/*',
    'xi-api-key': app_config.ELEVENLABS_API_KEY,
    'Content-Type': 'application/json'
}

def play_audio(text):
    data = {
            'text': text,
            "model_id": "eleven_monolingual_v1",
            'voice_settings': {
                'stability': 0.50,
                'similarity_boost': 0.30
                }
            }
    res = requests.post(url, headers=headers, json=data, stream=True)
    res.raise_for_status()
    # use subprocess to pipe the audio data to ffplay and play it
    ffplay_cmd = ['ffplay', '-autoexit', '-']
    ffplay_proc = subprocess.Popen(ffplay_cmd, stdin=subprocess.PIPE)
    for chunk in res.iter_content(chunk_size=4096):
        ffplay_proc.stdin.write(chunk)
        print("Downloading...")
    # close the ffplay process when finished
    ffplay_proc.stdin.close()
    ffplay_proc.wait()