import os
import sys
import json
import shutil

CURRENT_VERSION = "1.2.0"
GITHUB_REPO = "Chuvak12/SyncifyStudio"
APP_NAME = "SyncifyStudio"
REG_RUN_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

try:
    import winreg
except ImportError:
    winreg = None


def get_app_data_dir():
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        path = os.path.join(base, "SyncifyStudio")
    else:
        path = os.path.join(os.path.expanduser("~"), ".syncifystudio")
    os.makedirs(path, exist_ok=True)
    return path


DATA_DIR = get_app_data_dir()
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
AUTH_FILE = os.path.join(DATA_DIR, "browser.json")
SNAPSHOT_FILE = os.path.join(DATA_DIR, "spotify_snapshot.json")
LOST_FILE = os.path.join(DATA_DIR, "lost_tracks.json")
CACHE_FILE = os.path.join(DATA_DIR, "search_cache.json")


def auto_migrate_local_files():
    base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    for f_name in ["browser.json", "config.json", "spotify_snapshot.json", "lost_tracks.json"]:
        old_p = os.path.join(base_dir, f_name)
        new_p = os.path.join(DATA_DIR, f_name)
        if os.path.exists(old_p) and not os.path.exists(new_p):
            try:
                shutil.copy2(old_p, new_p)
            except Exception:
                pass


auto_migrate_local_files()


def atomic_json_save(data, filepath):
    tmp = filepath + f".tmp_{os.getpid()}"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, filepath)
    except Exception:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass


def get_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "sp_url": "",
        "ytm_url": "",
        "sync_delete": 1,
        "safe_mode": 1,
        "auto_sync": 0,
        "auto_sync_interval": 24,  # часы (6, 12, 24, 48)
        "close_to_tray": 0,
        "autostart": 0,
        "notifications": 1,        # уведомления Windows
        "theme": "spotify",
        "search_workers": 4,       # потоки поиска
        "batch_size": 25,          # размер пачки заливки
        "fuzzy_threshold": 0.78,   # порог нечеткого поиска
        "verbose_logging": 0       # подробный лог
    }


def save_config_dict(cfg):
    atomic_json_save(cfg, CONFIG_FILE)


def set_windows_autostart(enable: bool):
    if not winreg:
        return False
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_PATH, 0, winreg.KEY_ALL_ACCESS)
        if enable:
            cmd = f'"{sys.executable}"' if getattr(sys, 'frozen', False) else f'"{sys.executable}" "{os.path.abspath(__file__)}"'
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def open_data_directory():
    """Открывает системную папку %APPDATA%/SyncifyStudio в Проводнике."""
    try:
        if sys.platform == "win32":
            os.startfile(DATA_DIR)
        else:
            import subprocess
            subprocess.Popen(["xdg-open", DATA_DIR])
        return True
    except Exception:
        return False