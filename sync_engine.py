import os
import re
import json
import time
import difflib
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from ytmusicapi import YTMusic
from config import AUTH_FILE, SNAPSHOT_FILE, LOST_FILE, CACHE_FILE, atomic_json_save, get_config
from auth import repair_browser_json


class SearchCache:
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = self._load()
        self._lock = threading.Lock()

    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def get(self, query):
        with self._lock:
            return self.data.get(query.lower())

    def set(self, query, video_id):
        with self._lock:
            self.data[query.lower()] = video_id

    def save(self):
        with self._lock:
            atomic_json_save(self.data, self.filepath)

    def clear(self):
        with self._lock:
            self.data = {}
            if os.path.exists(self.filepath):
                try:
                    os.remove(self.filepath)
                except Exception:
                    pass

    def count(self):
        with self._lock:
            return len(self.data)


search_cache = SearchCache(CACHE_FILE)


def normalize_title(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[\(\[\{].*?(official|video|audio|remaster|lyrics|4k|hd|feat|ft\.).*?[\)\]\}]", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    return " ".join(text.split())


def is_track_similar(title1: str, artist1: str, title2: str, artist2: str, threshold: float = 0.78) -> bool:
    n1 = normalize_title(title1)
    n2 = normalize_title(title2)
    if n1 == n2 or n1 in n2 or n2 in n1:
        return True
    ratio_t = difflib.SequenceMatcher(None, n1, n2).ratio()
    ratio_a = difflib.SequenceMatcher(None, artist1.lower(), artist2.lower()).ratio()
    return ratio_t >= threshold and (ratio_a >= 0.6 or artist1.lower() in artist2.lower() or artist2.lower() in artist1.lower())


def parse_playlist_id(url: str, pattern: str) -> str:
    m = re.search(pattern, url)
    return m.group(1) if m else url.strip()


def fetch_all_spotify(sp_url: str):
    from spotify_scraper import SpotifyClient
    pid = parse_playlist_id(sp_url, r"playlist[/:]([a-zA-Z0-9]+)")
    clean_url = f"https://open.spotify.com/playlist/{pid}"
    with SpotifyClient() as client:
        pl = client.get_playlist(clean_url, max_tracks=2000)
        tracks = []
        for item in pl.tracks:
            t_obj = getattr(item, "track", item)
            if hasattr(t_obj, "to_dict"):
                d = t_obj.to_dict().get("track", t_obj.to_dict())
                title = d.get("name") or "Unknown"
                artists = ", ".join([a.get("name", "") if isinstance(a, dict) else str(a) for a in d.get("artists", [])])
            else:
                title = getattr(t_obj, "name", None) or "Unknown"
                artists = ", ".join([getattr(a, "name", None) or str(a) for a in getattr(t_obj, "artists", [])])
            artists = artists or "Unknown Artist"
            tracks.append({
                "query": f"{artists} - {title}".strip(" -"),
                "artist": artists,
                "title": title,
                "display": f"{artists} — {title}"
            })
        return tracks


def calculate_playlist_insights(tracks):
    if not tracks:
        return None
    artists = [t["artist"] for t in tracks]
    unique_artists = len(set(artists))
    most_common = Counter(artists).most_common(3)
    top_artists_str = ", ".join([f"{a} ({cnt})" for a, cnt in most_common])
    return {
        "total_tracks": len(tracks),
        "unique_artists": unique_artists,
        "top_artists": top_artists_str
    }


def resolve_single_track(yt, sp_t):
    query = sp_t['query']
    cached_id = search_cache.get(query)
    if cached_id:
        return sp_t, cached_id
    try:
        s_res = yt.search(query, filter="songs") or yt.search(query, filter="videos")
        if s_res:
            vid = s_res[0]['videoId']
            search_cache.set(query, vid)
            return sp_t, vid
    except Exception:
        pass
    return sp_t, None