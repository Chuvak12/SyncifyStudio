import os
import re
import time
import hashlib
from http.cookies import SimpleCookie
from config import AUTH_FILE, atomic_json_save


def get_sapisid_hash(cookie_str: str, origin: str = "https://music.youtube.com"):
    if not cookie_str:
        raise ValueError("Строка Cookie пуста.")
    sapisid = None
    try:
        cookie = SimpleCookie()
        cookie.load(cookie_str.replace('"', ''))
        for key in ['__Secure-3PAPISID', 'SAPISID', '__Secure-1PAPISID']:
            if key in cookie:
                sapisid = cookie[key].value
                break
    except Exception:
        pass

    if not sapisid:
        m = re.search(r"(?:__Secure-3PAPISID|SAPISID)=([^;]+)", cookie_str)
        if m:
            sapisid = m.group(1).strip()

    if not sapisid:
        raise ValueError("В Cookie отсутствует SAPISID / __Secure-3PAPISID. Войдите в YouTube Music в браузере.")

    unix_timestamp = str(int(time.time()))
    to_hash = f"{unix_timestamp} {sapisid} {origin}"
    sha1_hash = hashlib.sha1(to_hash.encode("utf-8")).hexdigest()
    return f"SAPISIDHASH {unix_timestamp}_{sha1_hash}"


def save_browser_auth(raw_input):
    cookie_str = ""
    m = re.search(r"Cookie:\s*(.+)", raw_input, re.IGNORECASE)
    if m:
        cookie_str = m.group(1).strip()
    elif "=" in raw_input and ("SID" in raw_input or "SAPISID" in raw_input):
        cookie_str = raw_input.strip()

    if not cookie_str:
        for line in raw_input.splitlines():
            if line.strip().lower().startswith("cookie:"):
                cookie_str = line.strip()[7:].strip()
                break

    if not cookie_str:
        cookie_str = raw_input

    auth_header = get_sapisid_hash(cookie_str)
    creds = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/json",
        "X-Goog-AuthUser": "0",
        "x-origin": "https://music.youtube.com",
        "Cookie": cookie_str,
        "Authorization": auth_header
    }
    atomic_json_save(creds, AUTH_FILE)
    return True


def repair_browser_json():
    if not os.path.exists(AUTH_FILE):
        return
    try:
        import json
        with open(AUTH_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        auth = data.get("Authorization") or data.get("authorization")
        if not auth or "SAPISIDHASH" not in auth:
            cookie = data.get("Cookie") or data.get("cookie", "")
            data["Authorization"] = get_sapisid_hash(cookie)
            data["x-origin"] = "https://music.youtube.com"
            atomic_json_save(data, AUTH_FILE)
    except Exception:
        pass