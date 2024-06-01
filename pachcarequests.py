import requests
import json as Json

def send_get_request(url, headers):
    response = requests.get(url, headers=headers)
    return Json.loads(response.text)

def send_post_request(url, headers = "", data = None, json=None, files=None):
    response = requests.post(url, headers=headers, data=data, json=json, files=files)
    if response.status_code == 200 or response.status_code == 201:
        if response.text:
            return Json.loads(response.text)
    print(f'Response code [{response.status_code}]: {response.text}')
    return {}

def send_delete_request(url, headers, json):
    response = requests.delete(url, headers=headers, json=json)
    return response