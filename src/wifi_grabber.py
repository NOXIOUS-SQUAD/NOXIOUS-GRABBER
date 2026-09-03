import subprocess
import re

def get_wifi_passwords():
    results = []
    try:
        output = subprocess.check_output(
            ['netsh', 'wlan', 'show', 'profiles'],
            shell=True,
            text=True,
            encoding='utf-8'
        )
        profile_names = re.findall(r"All User Profile\s*:\s*(.*)", output)
        for profile in profile_names:
            profile = profile.strip()
            try:
                password_output = subprocess.check_output(
                    ['netsh', 'wlan', 'show', 'profile', profile, 'key=clear'],
                    shell=True,
                    text=True,
                    encoding='utf-8'
                )
                password_match = re.search(r"Key Content\s*:\s*(.*)", password_output)
                password = password_match.group(1).strip() if password_match else "No password found"
                results.append({
                    'ssid': profile,
                    'password': password
                })
            except:
                results.append({
                    'ssid': profile,
                    'password': "Unable to retrieve"
                })
    except:
        pass
    return results
