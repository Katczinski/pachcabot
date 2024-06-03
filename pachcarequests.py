import requests
import json as Json

accept_codes = [ 200, 201, 202, 204 ]

def send_get_request(url, headers) -> Json:
    response = requests.get(url, headers=headers)
    if response.status_code in accept_codes:
        if response.text:
            return Json.loads(response.text)
    print(f'Response code [{response.status_code}]: {response.text}')
    return { "data": {} }

def send_post_request(url, headers = "", data = None, json=None, files=None) -> Json:
    response = requests.post(url, headers=headers, data=data, json=json, files=files)
    if response.status_code in accept_codes:
        if response.text:
            return Json.loads(response.text)
    print(f'Response code [{response.status_code}]: {response.text}')
    return { "data": {} }

def send_delete_request(url, headers, json) -> Json:
    response = requests.delete(url, headers=headers, json=json)
    if response.status_code in accept_codes:
        if response.text:
            return Json.loads(response.text)
    print(f'Response code [{response.status_code}]: {response.text}')
    return { "data": {} }

def send_put_request(url, headers = "", data = None, json=None, files=None) -> Json:
    response = requests.put(url, headers=headers, data=data, json=json, files=files)
    if response.status_code in accept_codes:
        if response.text:
            return Json.loads(response.text)
    print(f'Response code [{response.status_code}]: {response.text}')
    return { "data": {} }