import os
import platform
import subprocess
import socket
import ctypes

try:
    import psutil
except:
    psutil = None

def get_extended_system_info():
    data = {}
    try:
        data['cpu_detailed'] = platform.processor() or "Unknown"
        data['arch'] = platform.machine()
        if psutil:
            data['cores_physical'] = psutil.cpu_count(logical=False)
            data['cores_logical'] = psutil.cpu_count(logical=True)
    except:
        pass
    try:
        if psutil:
            mem = psutil.virtual_memory()
            data['ram_total_gb'] = round(mem.total / (1024**3), 2)
            data['ram_available_gb'] = round(mem.available / (1024**3), 2)
    except:
        pass
    try:
        data['gpu'] = "Unknown"
        out = ""
        try:
            out = subprocess.check_output("wmic path win32_VideoController get name", shell=True, text=True, encoding='utf-8', errors='ignore', stderr=subprocess.DEVNULL, timeout=5)
        except:
            out = ""
        if not out or "no se reconoce" in out.lower():
            try:
                out = subprocess.check_output('powershell -Command "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name"', shell=True, text=True, encoding='utf-8', errors='ignore', stderr=subprocess.DEVNULL, timeout=8)
            except:
                out = ""
        lines = [l.strip() for l in out.splitlines() if l.strip() and "Name" not in l]
        if lines:
            data['gpu'] = ", ".join(lines[:2])
    except:
        pass
    try:
        data['screen_res'] = "Unknown"
        user32 = ctypes.windll.user32
        w = user32.GetSystemMetrics(0)
        h = user32.GetSystemMetrics(1)
        data['screen_res'] = f"{w}x{h}"
    except:
        pass
    try:
        import time
        if psutil:
            boot = psutil.boot_time()
            uptime_s = time.time() - boot
            h = int(uptime_s // 3600)
            m = int((uptime_s % 3600) // 60)
            data['uptime'] = f"{h}h {m}m"
    except:
        pass
    try:
        if psutil:
            data['processes'] = len(psutil.pids())
    except:
        pass
    return data

def get_network_info():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "Unknown"
    try:
        out = subprocess.check_output("ipconfig", shell=True, text=True, encoding='utf-8', errors='ignore', timeout=5)
        import re
        ips = re.findall(r"IPv4.*?:\s*(.*)", out)
        if ips:
            local_ip = ips[0].strip()
    except:
        pass
    return {'local_ip': local_ip}

def get_startup_apps():
    apps = []
    try:
        import winreg
        paths = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        ]
        for hive, path in paths:
            try:
                key = winreg.OpenKey(hive, path)
                i = 0
                while True:
                    try:
                        name, val, _ = winreg.EnumValue(key, i)
                        apps.append(f"{name}: {val[:120]}")
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(key)
            except:
                continue
    except:
        pass
    return apps[:20]

def get_recent_files(limit=20):
    files = []
    try:
        recent = os.path.join(os.getenv('APPDATA') or '', r"Microsoft\Windows\Recent")
        if os.path.exists(recent):
            for item in os.listdir(recent)[:limit]:
                files.append(item)
    except:
        pass
    return files
