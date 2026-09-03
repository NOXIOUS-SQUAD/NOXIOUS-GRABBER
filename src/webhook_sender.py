import requests
from datetime import datetime
from config import WEBHOOK_URL, WEBHOOK_NAME, WEBHOOK_AVATAR

def send_to_webhook(content, file_path=None):
    try:
        if not WEBHOOK_URL or WEBHOOK_URL == "YOUR_WEBHOOK_HERE":
            return
        if file_path:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.split('\\')[-1].split('/')[-1], f)}
                data = {
                    'username': WEBHOOK_NAME,
                    'avatar_url': WEBHOOK_AVATAR,
                    'content': content
                }
                requests.post(WEBHOOK_URL, data=data, files=files, timeout=15)
        else:
            data = {
                'username': WEBHOOK_NAME,
                'avatar_url': WEBHOOK_AVATAR,
                'content': content
            }
            requests.post(WEBHOOK_URL, json=data, timeout=10)
    except:
        pass

def send_embed(title, fields, color=0x5865f2):
    try:
        if not WEBHOOK_URL or WEBHOOK_URL == "YOUR_WEBHOOK_HERE":
            return
        embed = {
            'title': title,
            'color': color,
            'fields': fields,
            'footer': {'text': 'NOXIOUS SQUAD| @nscsp12', 'icon_url': WEBHOOK_AVATAR},
            'timestamp': datetime.now().isoformat()
        }
        data = {
            'username': WEBHOOK_NAME,
            'avatar_url': WEBHOOK_AVATAR,
            'embeds': [embed]
        }
        requests.post(WEBHOOK_URL, json=data, timeout=10)
    except:
        pass
