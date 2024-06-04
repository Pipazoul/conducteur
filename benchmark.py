import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# The URL and headers for the request
url = 'http://localhost:8000/predict'
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer anotherTOken'
    }
data = json.dumps({
    "image": "r8.im/stability-ai/sdxl@sha256:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
    "input": {
        "width": 768,
        "height": 768,
        "prompt": "A hot banana",
        "refine": "expert_ensemble_refiner",
        "scheduler": "K_EULER",
        "lora_scale": 0.6,
        "num_outputs": 1,
        "guidance_scale": 7.5,
        "apply_watermark": False,
        "high_noise_frac": 0.8,
        "negative_prompt": "",
        "prompt_strength": 0.8,
        "num_inference_steps": 25
    }
})

def send_request(request_id):
    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, data=data)
        duration = time.time() - start_time
        if response.status_code == 200:
            return (request_id, duration, "JSON response")
        else:
            return (request_id, duration, "Error response")
    except Exception as e:
        return (request_id, None, str(e))

def benchmark_requests(n):
    with ThreadPoolExecutor(max_workers=n) as executor:
        futures = [executor.submit(send_request, i) for i in range(n)]
        for future in as_completed(futures):
            request_id, duration, response_type = future.result()
            print(f"Request ID: {request_id}, Response Time: {duration} seconds, Type: {response_type}")

if __name__ == "__main__":
    benchmark_requests(100)
