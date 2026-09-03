import os

def get_clipboard_text():
    try:
        import win32clipboard
        try:
            win32clipboard.OpenClipboard()
            try:
                if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                    data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                    if data:
                        win32clipboard.CloseClipboard()
                        return str(data).strip()[:2000]
            except:
                pass
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
        except:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
    except:
        pass

    try:
        import ctypes
        from ctypes import wintypes
        CF_UNICODETEXT = 13
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        try:
            user32.OpenClipboard.argtypes = [wintypes.HWND]
            user32.OpenClipboard.restype = wintypes.BOOL
            user32.CloseClipboard.argtypes = []
            user32.CloseClipboard.restype = wintypes.BOOL
            user32.IsClipboardFormatAvailable.argtypes = [wintypes.UINT]
            user32.IsClipboardFormatAvailable.restype = wintypes.BOOL
            user32.GetClipboardData.argtypes = [wintypes.UINT]
            user32.GetClipboardData.restype = wintypes.HANDLE
            kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
            kernel32.GlobalLock.restype = wintypes.LPVOID
            kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
            kernel32.GlobalUnlock.restype = wintypes.BOOL
            kernel32.GlobalSize.argtypes = [wintypes.HGLOBAL]
            kernel32.GlobalSize.restype = ctypes.c_size_t
        except:
            pass

        if not user32.OpenClipboard(None):
            return None
        try:
            if not user32.IsClipboardFormatAvailable(CF_UNICODETEXT):
                user32.CloseClipboard()
                return None
            handle = user32.GetClipboardData(CF_UNICODETEXT)
            if not handle:
                user32.CloseClipboard()
                return None
            locked = kernel32.GlobalLock(handle)
            if not locked:
                user32.CloseClipboard()
                return None
            try:
                size = kernel32.GlobalSize(handle)
                if size == 0:
                    text = ctypes.wstring_at(locked)
                else:
                    max_chars = min(size // 2, 2000)
                    text = ctypes.wstring_at(locked, max_chars)
                kernel32.GlobalUnlock(handle)
                user32.CloseClipboard()
                if text:
                    return text.strip()[:2000]
            except:
                try:
                    kernel32.GlobalUnlock(handle)
                except:
                    pass
                user32.CloseClipboard()
                return None
        except:
            try:
                user32.CloseClipboard()
            except:
                pass
            return None
    except:
        pass

    try:
        import pyperclip
        t = pyperclip.paste()
        if t:
            return str(t).strip()[:2000]
    except:
        pass
    return None

def get_clipboard_info():
    txt = get_clipboard_text()
    if txt:
        return txt
    return None
