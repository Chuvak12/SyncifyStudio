import os
import sys
import json
import time
import threading
import subprocess
import urllib.request
import webbrowser
import webview
from ytmusicapi import YTMusic

try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    pystray = None

from config import (
    CURRENT_VERSION, GITHUB_REPO, DATA_DIR, AUTH_FILE, SNAPSHOT_FILE, LOST_FILE, CACHE_FILE,
    get_config, save_config_dict, set_windows_autostart, atomic_json_save, open_data_directory
)
from auth import save_browser_auth, repair_browser_json
from sync_engine import (
    fetch_all_spotify, calculate_playlist_insights, parse_playlist_id,
    is_track_similar, search_cache, resolve_single_track
)
from ui import HTML_UI

main_window = None
tray_icon_instance = None


def send_log(text, log_type="normal"):
    if main_window:
        try:
            escaped = json.dumps(text)
            main_window.evaluate_js(f"appendLog({escaped}, '{log_type}')")
        except Exception:
            pass


def send_progress(percent, text=""):
    if main_window:
        try:
            main_window.evaluate_js(f"updateProgress({int(percent)}, {json.dumps(text)})")
        except Exception:
            pass


def send_toast(title, message):
    cfg = get_config()
    if cfg.get("notifications", 1) == 0:
        return
    global tray_icon_instance
    if tray_icon_instance:
        try:
            tray_icon_instance.notify(message, title)
        except Exception:
            pass


def create_tray_image():
    if os.path.exists("icon.ico"):
        try:
            return Image.open("icon.ico")
        except Exception:
            pass
    img = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((2, 2, 62, 62), fill=(30, 215, 96))
    draw.ellipse((20, 20, 44, 44), fill=(0, 0, 0))
    return img


def exit_app_clean():
    global tray_icon_instance
    if tray_icon_instance:
        try:
            tray_icon_instance.stop()
        except Exception:
            pass
        tray_icon_instance = None
    os._exit(0)


def setup_tray(api_instance):
    global tray_icon_instance
    if not pystray or tray_icon_instance:
        return

    def on_open(icon=None, item=None):
        if main_window:
            try:
                main_window.show()
            except Exception:
                pass

    menu = pystray.Menu(
        pystray.MenuItem("Открыть Syncify Studio", on_open, default=True),
        pystray.MenuItem("⚡ Быстрый синхрон", lambda icon, item: api_instance.quick_sync()),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Выход", lambda icon, item: exit_app_clean())
    )

    try:
        tray_icon_instance = pystray.Icon("SyncifyStudio", create_tray_image(), "Syncify Studio", menu)
        threading.Thread(target=tray_icon_instance.run, daemon=True).start()
    except Exception:
        pass


class AppApi:
    def __init__(self):
        self._is_syncing = False
        self._auto_sync_active = False
        self._cancel_requested = False

    def open_browser(self, url):
        try:
            webbrowser.open(url)
        except Exception:
            pass

    def open_appdata(self):
        open_data_directory()

    def clear_cache(self):
        search_cache.clear()
        send_log("[✓] Кэш быстрого поиска очищен.", "success")
        if main_window:
            main_window.evaluate_js("updateStatus()")

    def reset_snapshot(self):
        if os.path.exists(SNAPSHOT_FILE):
            try:
                os.remove(SNAPSHOT_FILE)
            except Exception:
                pass
        send_log("[✓] Слепок базы Spotify сброшен.", "success")
        if main_window:
            main_window.evaluate_js("updateStatus()")

    def get_diagnostics(self):
        cfg = get_config()
        diag = {
            "version": CURRENT_VERSION,
            "platform": sys.platform,
            "python": sys.version,
            "data_dir": DATA_DIR,
            "has_auth": os.path.exists(AUTH_FILE),
            "has_snapshot": os.path.exists(SNAPSHOT_FILE),
            "cached_tracks": search_cache.count(),
            "config": cfg
        }
        return json.dumps(diag, indent=2, ensure_ascii=False)

    def cancel_process(self):
        self._cancel_requested = True
        send_log("[!] Операция отменена пользователем.", "warn")

    def check_update(self):
        if not GITHUB_REPO or "/" not in GITHUB_REPO:
            return None
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            req = urllib.request.Request(url, headers={"User-Agent": "SyncifyApp"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode())
                tag = data.get("tag_name", "").lstrip("v").strip()
                c_parts = [int(x) for x in CURRENT_VERSION.split(".")]
                l_parts = [int(x) for x in tag.split(".")]
                if l_parts > c_parts:
                    for asset in data.get("assets", []):
                        if asset.get("name", "").lower().endswith(".exe"):
                            return {
                                "has_update": True,
                                "version": tag,
                                "notes": data.get("body", "Улучшения и фиксы."),
                                "download_url": asset.get("browser_download_url")
                            }
        except Exception:
            pass
        return None

    def apply_update(self, download_url):
        if not getattr(sys, 'frozen', False):
            send_log("[-] Обновление доступно только в готовом .exe файле!", "warn")
            return

        def update_thread():
            try:
                current_exe = sys.executable
                new_exe = current_exe + ".new"
                send_log("[~] Скачивание нового файла SyncifyStudio.exe...", "info")
                urllib.request.urlretrieve(download_url, new_exe)
                send_log("[✓] Скачано! Перезапуск...", "success")
                cmd = f'ping 127.0.0.1 -n 3 > nul & move /y "{new_exe}" "{current_exe}" & start "" "{current_exe}"'
                subprocess.Popen(f'cmd.exe /c {cmd}', shell=True)
                exit_app_clean()
            except Exception as e:
                send_log(f"[-] Ошибка при обновлении: {e}", "error")

        threading.Thread(target=update_thread, daemon=True).start()

    def get_config(self):
        return get_config()

    def save_config(self, cfg_data):
        save_config_dict(cfg_data)

    def set_autostart(self, enable):
        ok = set_windows_autostart(bool(enable))
        if ok:
            send_log(f"[i] Автозапуск Windows: {'Включен' if enable else 'Выключен'}", "info")
        return ok

    def get_status(self):
        is_auth = os.path.exists(AUTH_FILE)
        snap_cnt = 0
        if os.path.exists(SNAPSHOT_FILE):
            try:
                with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
                    snap_cnt = len(json.load(f))
            except Exception:
                pass
        lost_cnt = 0
        if os.path.exists(LOST_FILE):
            try:
                with open(LOST_FILE, "r", encoding="utf-8") as f:
                    lost_cnt = len(json.load(f))
            except Exception:
                pass
        return {
            "is_auth": is_auth,
            "snapshot_count": snap_cnt,
            "lost_count": lost_cnt,
            "cache_count": search_cache.count()
        }

    def save_auth(self, raw_input):
        try:
            ok = save_browser_auth(raw_input)
            if ok:
                send_log("[✓] YouTube Music успешно авторизован!", "success")
            return ok
        except Exception as e:
            send_log(f"[-] {e}", "error")
            return False

    def fetch_tracks(self):
        cfg = get_config()
        sp_url = cfg.get("sp_url", "")
        if not sp_url:
            return {"success": False, "error": "Укажите ссылку на Spotify!"}
        try:
            tracks = fetch_all_spotify(sp_url)
            insights = calculate_playlist_insights(tracks)
            return {"success": True, "tracks": tracks, "insights": insights}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def quick_sync(self):
        if self._is_syncing:
            send_log("[!] Процесс уже выполняется...", "warn")
            return
        threading.Thread(target=self._run_sync_worker, args=(None, False), daemon=True).start()

    def sync_selected(self, selected_tracks):
        if self._is_syncing:
            send_log("[!] Процесс уже выполняется...", "warn")
            return
        threading.Thread(target=self._run_sync_worker, args=(selected_tracks, True), daemon=True).start()

    def _run_sync_worker(self, selected_tracks, manual):
        self._is_syncing = True
        self._cancel_requested = False
        try:
            cfg = get_config()
            sp_url = cfg.get("sp_url")
            ytm_url = cfg.get("ytm_url")
            ytm_pid = parse_playlist_id(ytm_url, r"list=([a-zA-Z0-9_-]+)")
            sync_delete = cfg.get("sync_delete", 1) == 1
            workers = int(cfg.get("search_workers", 4))
            batch_size = int(cfg.get("batch_size", 25))
            verbose = cfg.get("verbose_logging", 0) == 1

            if not (sp_url and ytm_pid):
                send_log("[-] Укажите ссылки на оба плейлиста!", "error")
                return

            if not os.path.exists(AUTH_FILE):
                send_log("[-] Авторизуйте YouTube Music перед синхронизацией!", "error")
                return

            repair_browser_json()
            yt = YTMusic(AUTH_FILE)
            yt_playlist = yt.get_playlist(ytm_pid, limit=None)
            current_yt = yt_playlist.get('tracks', [])

            if not manual:
                current_sp = fetch_all_spotify(sp_url)
                known_queries = set()
                if os.path.exists(SNAPSHOT_FILE):
                    try:
                        with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
                            known_queries = set(json.load(f))
                    except Exception:
                        pass

                if not known_queries:
                    queries = [t["query"].lower() for t in current_sp]
                    atomic_json_save(queries, SNAPSHOT_FILE)
                    send_log(f"[✓] База зафиксирована: {len(current_sp)} треков запомнено.", "success")
                    return

                current_sp_queries = {t["query"].lower() for t in current_sp}
                truly_new = [t for t in current_sp if t["query"].lower() not in known_queries]
                deleted_from_spotify = [q for q in known_queries if q not in current_sp_queries]

                if sync_delete and deleted_from_spotify:
                    send_log(f"[-] Замечено удаление из Spotify: {len(deleted_from_spotify)} треков.", "warn")
                    to_remove = []
                    for yt_t in current_yt:
                        yt_title = yt_t.get('title', '')
                        yt_artists = " ".join([a.get('name', '') for a in yt_t.get('artists', [])])
                        for del_q in deleted_from_spotify:
                            if is_track_similar(del_q, "", yt_title, yt_artists):
                                to_remove.append(yt_t)
                                break
                    if to_remove:
                        yt.remove_playlist_items(ytm_pid, to_remove)
                        send_log(f"[✓] Удалено из YouTube Music: {len(to_remove)} треков", "warn")
                        current_yt = [t for t in current_yt if t not in to_remove]

                if not truly_new and not deleted_from_spotify:
                    send_log("[✓] Изменений в Spotify нет. Плейлист актуален!", "success")
                    return

                if truly_new:
                    send_log(f"[+] Обнаружено {len(truly_new)} свежих новинок!", "info")

                selected_tracks = truly_new
                all_queries = [t["query"].lower() for t in current_sp]
                atomic_json_save(all_queries, SNAPSHOT_FILE)

            lost = []
            if os.path.exists(LOST_FILE):
                try:
                    with open(LOST_FILE, "r", encoding="utf-8") as f:
                        lost = json.load(f)
                except Exception:
                    pass

            tracks_to_search = []
            if selected_tracks:
                for sp_t in selected_tracks:
                    already_in_yt = any(
                        is_track_similar(sp_t['title'], sp_t['artist'], t.get('title', ''), " ".join([a.get('name', '') for a in t.get('artists', [])]))
                        for t in current_yt
                    )
                    if not already_in_yt:
                        tracks_to_search.append(sp_t)
                    else:
                        if manual and verbose:
                            send_log(f"  • Уже есть: {sp_t['display']}")

            to_add_ids = []
            total_search = len(tracks_to_search)

            if total_search > 0:
                send_log(f"[*] Турбо-поиск в {workers} потоков ({total_search} треков)...", "info")
                send_progress(5, f"Поиск: 0/{total_search}")

                from concurrent.futures import ThreadPoolExecutor, as_completed
                completed = 0
                with ThreadPoolExecutor(max_workers=workers) as executor:
                    futures = [executor.submit(resolve_single_track, yt, t) for t in tracks_to_search]
                    for fut in as_completed(futures):
                        if self._cancel_requested:
                            send_log("[!] Операция отменена пользователем.", "warn")
                            send_progress(-1)
                            return

                        sp_t, vid = fut.result()
                        completed += 1
                        pct = int((completed / total_search) * 70) + 5
                        send_progress(pct, f"Поиск: {completed}/{total_search}")

                        if vid:
                            to_add_ids.append(vid)
                            if verbose:
                                send_log(f"  [+] Найден ID: {vid} ({sp_t['title']})")
                        else:
                            send_log(f"  [?] Не найдено: {sp_t['query']}", "warn")
                            if not any(lt.get("query") == sp_t["query"] for lt in lost):
                                lost.append(sp_t)
                                atomic_json_save(lost, LOST_FILE)

                search_cache.save()

            if to_add_ids:
                total_batches = (len(to_add_ids) + batch_size - 1) // batch_size
                send_log(f"[*] Заливка {len(to_add_ids)} треков пакетами ({total_batches} шт.)...", "info")
                
                for b_idx, i in enumerate(range(0, len(to_add_ids), batch_size), 1):
                    if self._cancel_requested:
                        send_log("[!] Заливка остановлена.", "warn")
                        break
                    batch = to_add_ids[i:i + batch_size]
                    yt.add_playlist_items(ytm_pid, batch)
                    pct = 75 + int((b_idx / total_batches) * 25)
                    send_progress(pct, f"Пакет {b_idx}/{total_batches}")
                    send_log(f"[✓] Залит пакет: {len(batch)} треков", "success")
                    time.sleep(0.3)

            send_progress(100, "Готово!")
            time.sleep(0.4)
            send_progress(-1)

            send_log(f"[✓] Синхронизация завершена! Добавлено: {len(to_add_ids)}", "success")
            send_toast("Syncify Studio", f"Синхронизация завершена! Добавлено: {len(to_add_ids)} треков.")
            if main_window:
                main_window.evaluate_js("updateStatus()")
        except Exception as e:
            send_progress(-1)
            send_log(f"[-] Ошибка: {e}", "error")
        finally:
            self._is_syncing = False

    def dedup(self):
        if self._is_syncing:
            send_log("[!] Подождите окончания текущей операции...", "warn")
            return
        threading.Thread(target=self._run_dedup_worker, daemon=True).start()

    def _run_dedup_worker(self):
        self._is_syncing = True
        try:
            cfg = get_config()
            ytm_pid = parse_playlist_id(cfg.get("ytm_url", ""), r"list=([a-zA-Z0-9_-]+)")
            if not ytm_pid or not os.path.exists(AUTH_FILE):
                send_log("[-] Укажите плейлист YouTube Music и авторизуйтесь!", "error")
                return

            repair_browser_json()
            send_log("[~] Поиск дубликатов в YouTube Music...", "info")
            yt = YTMusic(AUTH_FILE)
            pl = yt.get_playlist(ytm_pid, limit=None)
            tracks = pl.get('tracks', [])

            seen = set()
            duplicates = []
            for t in tracks:
                vid = t.get('videoId')
                title = t.get('title', '').strip().lower()
                artists = " ".join([a.get('name', '').lower() for a in t.get('artists', [])])
                key = vid if vid else f"{title} - {artists}"
                if key in seen:
                    duplicates.append(t)
                else:
                    seen.add(key)

            if not duplicates:
                send_log("[✓] Дубликатов не найдено. Плейлист чист!", "success")
            else:
                yt.remove_playlist_items(ytm_pid, duplicates)
                send_log(f"[✓] Успешно удалено {len(duplicates)} дубликатов!", "success")
                send_toast("Syncify Studio", f"Удалено {len(duplicates)} дубликатов!")
        except Exception as e:
            send_log(f"[-] Ошибка дедупликации: {e}", "error")
        finally:
            self._is_syncing = False

    def download_mp3(self, tracks):
        if self._is_syncing:
            send_log("[!] Подождите окончания текущей операции...", "warn")
            return

        folder = None
        if main_window:
            try:
                folder = main_window.create_file_dialog(webview.FOLDER_DIALOG)
            except Exception:
                pass

        if not folder:
            try:
                from tkinter import filedialog
                import tkinter as tk
                root = tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                res = filedialog.askdirectory(title="Выберите папку для сохранения MP3")
                root.destroy()
                if res:
                    folder = (res,)
            except Exception:
                pass

        if not folder or not folder[0]:
            return

        save_dir = folder[0]
        threading.Thread(target=self._run_download_worker, args=(tracks, save_dir), daemon=True).start()

    def _run_download_worker(self, tracks, save_dir):
        try:
            import yt_dlp
        except ImportError:
            send_log("[-] Модуль yt-dlp не установлен: pip install yt-dlp", "error")
            return

        self._is_syncing = True
        self._cancel_requested = False
        send_log(f"[↓] Скачивание {len(tracks)} треков в: {save_dir}", "info")
        success = 0
        total = len(tracks)

        for idx, t in enumerate(tracks, 1):
            if self._cancel_requested:
                send_log("[!] Скачивание прервано пользователем.", "warn")
                break

            pct = int((idx / total) * 100)
            send_progress(pct, f"Скачано {idx}/{total}")

            q = t.get("query", "")
            send_log(f"[{idx}/{total}] Скачиваем: {t.get('display', q)}")
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(save_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'default_search': 'ytsearch1',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([q])
                success += 1
            except Exception:
                try:
                    fallback = {'format': 'bestaudio/best', 'outtmpl': os.path.join(save_dir, '%(title)s.%(ext)s'), 'quiet': True, 'default_search': 'ytsearch1'}
                    with yt_dlp.YoutubeDL(fallback) as ydl:
                        ydl.download([q])
                    success += 1
                except Exception as err:
                    send_log(f"  [-] Пропуск: {err}", "warn")

        send_progress(-1)
        send_log(f"[✓] Скачивание завершено: {success} из {total} сохранено!", "success")
        send_toast("Syncify Studio", f"Скачано {success} треков в MP3!")
        self._is_syncing = False

    def force_snapshot(self):
        cfg = get_config()
        sp_url = cfg.get("sp_url", "")
        if not sp_url:
            send_log("[-] Укажите ссылку на Spotify!", "error")
            return
        try:
            tracks = fetch_all_spotify(sp_url)
            queries = [t["query"].lower() for t in tracks]
            atomic_json_save(queries, SNAPSHOT_FILE)
            send_log(f"[✓] База зафиксирована: {len(tracks)} треков запомнено.", "success")
            if main_window:
                main_window.evaluate_js("updateStatus()")
        except Exception as e:
            send_log(f"[-] Ошибка: {e}", "error")

    def get_lost(self):
        if os.path.exists(LOST_FILE):
            try:
                with open(LOST_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def clear_lost(self):
        if os.path.exists(LOST_FILE):
            try:
                os.remove(LOST_FILE)
            except Exception:
                pass
        send_log("[✓] Список потеряшек очищен.", "success")
        if main_window:
            main_window.evaluate_js("updateStatus()")

    def toggle_auto_sync(self, active):
        self._auto_sync_active = bool(active)
        if self._auto_sync_active:
            cfg = get_config()
            interval = cfg.get("auto_sync_interval", 24)
            msg = f"[i] Фоновый мониторинг ВКЛЮЧЕН ({interval}ч)."
            send_log(msg, "info")
            threading.Thread(target=self._auto_sync_loop, daemon=True).start()
        else:
            send_log("[i] Фоновый мониторинг ВЫКЛЮЧЕН.", "info")

    def _auto_sync_loop(self):
        while self._auto_sync_active:
            cfg = get_config()
            interval_hours = int(cfg.get("auto_sync_interval", 24))
            total_seconds = interval_hours * 3600
            
            for _ in range(total_seconds // 10):
                if not self._auto_sync_active:
                    return
                time.sleep(10)
            if self._auto_sync_active:
                send_log("[⏰] Сработал суточный таймер синхрона...", "info")
                self._run_sync_worker(None, False)


def on_window_closing():
    cfg = get_config()
    if cfg.get("close_to_tray", 0) == 1 and tray_icon_instance:
        threading.Timer(0.05, lambda: main_window.hide()).start()
        return False
    exit_app_clean()


if __name__ == "__main__":
    try:
        api = AppApi()
        main_window = webview.create_window(
            title="Syncify Studio",
            html=HTML_UI,
            js_api=api,
            width=980,
            height=860,
            min_size=(740, 600),
            background_color="#090A0E"
        )
        main_window.events.closing += on_window_closing
        setup_tray(api)
        webview.start(debug=False)
    except Exception as e:
        import traceback
        with open("crash.log", "w", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, f"Ошибка:\n{e}", "Syncify Studio", 0x10)
        except Exception:
            pass