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
        time.sleep(30)
        
    response = requests.get(url, headers=headers)
    response_data = response.json()
            
    result_url = response_data['result_url']
    download_video_from_uri(result_url, "static/idle.mp4")


def download_video_from_uri(uri, local_file_path):
    response = requests.get(uri, stream=True)
    if response.status_code == 200:
        with open(local_file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Video downloaded successfully to {local_file_path}")
    else:
        print(f"Failed to download the video. Status code: {response.status_code}")
        
        
import boto3
from botocore.exceptions import NoCredentialsError


s3 = boto3.client('s3', aws_access_key_id=app_config.aws_access_key_id,
                  aws_secret_access_key=app_config.aws_secret_access_key)

filename = "your_avatar.png"
filepath = "static/img/your_avatar.png"

try:
    with open(filepath, 'rb') as image_file:
        s3.put_object(Body=image_file, Bucket='digital-me-rediminds', Key=filename)
except NoCredentialsError:
    print({"error": "S3 credentials not found"})


# Return the URL to the audio file
public_url = f"https://digital-me-rediminds.s3.amazonaws.com/{filename}"
        
video_id = create_holder_video(public_url)
get_holder_video(video_id)