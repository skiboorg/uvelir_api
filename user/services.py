import json

import requests


def send_tg_mgs(to_id,message):
    Headers = { 'Content-Type':'application/json'}
    data = {
        "chat_id":to_id,
        "message":message
    }
    res = requests.post('http://0.0.0.0:5000/send_message',headers=Headers,data=json.dumps(data))