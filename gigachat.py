import json
from random import choices

import requests
import urllib3
import uuid


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_token():
  rq_uid = str(uuid.uuid4())
  url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

  payload={
    'scope': 'GIGACHAT_API_PERS'
  }
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'RqUID': rq_uid,
    'Authorization': 'Basic MDIwYWRjOTQtZDdmMy00YzEyLWFlODktZWUwN2ZjZWE5ZThmOjdlNWEyNGVhLTAwY2UtNDEzMS1iMDllLWJkZjQyZDEwNDg3NQ=='
  }

  response = requests.request("POST", url, headers=headers, data=payload,verify=False)

  return response.json()['access_token']


def send_message(text, token):
  url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

  payload = json.dumps({
    "model": 'GigaChat',
    "messages": [
      {
        "role": 'user',
        "content": text
      }
    ],
    "temperature": 1,
    "top_p": 0.1,
    'n': 1,
    "stream": False,
    "max_tokens": 512,
    'repetition_penalty': 1,
    "update_interval": 0
  })
  headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
  }

  response = requests.request("POST", url, headers=headers, data=payload, verify=False)
  return response.json()['choices'][0]['message']['content']
