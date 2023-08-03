import requests
import app_config
import time

url = "https://api.d-id.com/animations"

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Basic {app_config.API_KEY}"
}

def create_holder_video(img_path):
    payload = { "source_url": img_path }
    response = requests.post(url, json=payload, headers=headers)
    response_data = response.json()
    return response_data["id"]
    
def get_holder_video(video_id):
    url = f"https://api.d-id.com/animations/{video_id}"
    response = requests.get(url, headers=headers)
    response_data = response.json()

    if(response_data['status']!='done'):
        time.sleep(10)
        
    response = requests.get(url, headers=headers)
    response_data = response.json()
    
    if(response_data['status']!='done'):
        time.sleep(10)
        
    response = requests.get(url, headers=headers)
    response_data = response.json()
    
    if(response_data['status']!='done'):
        time.sleep(10)
        
    response = requests.get(url, headers=headers)
    response_data = response.json()
            
    result_url = response_data['result_url']
    download_video_from_uri(result_url, "static/idle.mp4")
    
def get_holder_video_url(video_id):
    url = f"https://api.d-id.com/animations/{video_id}"
    response = requests.get(url, headers=headers)
    response_data = response.json()

    if(response_data['status']!='done'):
        time.sleep(10)
        
    response = requests.get(url, headers=headers)
    response_data = response.json()
    
    if(response_data['status']!='done'):
        time.sleep(10)
        
    response = requests.get(url, headers=headers)
    response_data = response.json()
    
    if(response_data['status']!='done'):
        time.sleep(10)
        
    response = requests.get(url, headers=headers)
    response_data = response.json()
            
    return response_data['result_url']


def download_video_from_uri(uri, local_file_path):
    response = requests.get(uri, stream=True)
    if response.status_code == 200:
        with open(local_file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Video downloaded successfully to {local_file_path}")
    else:
        print(f"Failed to download the video. Status code: {response.status_code}") 