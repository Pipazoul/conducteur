import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random

images = [
    "yassinsiouda/cog-flux:neopotism-realism",
    "r8.im/stability-ai/sdxl@sha256:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
    "r8.im/fofr/epicrealismxl-lightning-hades@sha256:0ca10b1fd361c1c5568720736411eaa89d9684415eb61fd36875b4d3c20f605a",
    "imagenotfound"
]

def send_request(request_id):
    # The URL and headers for the request
    url = 'http://localhost:8000/predict'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer token'
        }
    data = json.dumps({
        "image": images[random.randint(0, len(images)-1)] ,
        "input": {
            "prompt": "A hot banana",
        }
    })
    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, data=data)
        duration = time.time() - start_time
        if response.status_code == 200:
            return (request_id, duration, "JSON response")
        elif response.status_code == 400 or response.status_code == 404: # Added this line to catch specific error codes
            return (request_id, duration, f"Error {response.status_code}: {response.text}")
        else:
            return (request_id, duration, f"Error response with status code {response.status_code}: {response.text}")
    except Exception as e:
        return (request_id, None, str(e))

def benchmark_requests(n):
    with ThreadPoolExecutor(max_workers=n) as executor:
        futures = [executor.submit(send_request, i) for i in range(n)]
        for future in as_completed(futures):
            request_id, duration, response_type = future.result()
            print(f"Request ID: {request_id}, Response Time: {duration} seconds, Type: {response_type}")

    
if __name__ == "__main__":
    benchmark_requests(50)
