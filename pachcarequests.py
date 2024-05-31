import requests
import json

def send_get_request(url, headers):
    response = requests.get(url, headers=headers)
    return json.loads(response.text)

def send_post_request(url, headers, data):  
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200 or response.status_code == 201:
        if response.text:
            return json.loads(response.text)
    print(f'Response code [{response.status_code}]: {response.text}')
    return {}

def send_delete_request(url, headers, data):
    response = requests.delete(url, headers=headers, json=data)
    return response