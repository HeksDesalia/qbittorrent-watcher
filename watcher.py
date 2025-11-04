#!/usr/bin/env python3
import os
import time
import json
import requests
import shutil
import sys
import logging

# ==========================
# Ensure env variables are present
# ==========================
REQUIRED_ENV_VARS = [
    "QBITTORRENT_URL",
    "QBITTORRENT_USERNAME",
    "QBITTORRENT_PASSWORD",
    "CHECK_INTERVAL",
    "TAG_DEST_MAP",
]

missing = [v for v in REQUIRED_ENV_VARS if not os.getenv(v)]
if missing:
    logging.error(f"Error : missing env variables : {', '.join(missing)}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

QBITTORRENT_URL = os.getenv("QBITTORRENT_URL")
QBITTORRENT_USERNAME = os.getenv("QBITTORRENT_USERNAME")
QBITTORRENT_PASSWORD = os.getenv("QBITTORRENT_PASSWORD")
API_KEY = os.getenv("QBITTORRENT_API_KEY")
DEST_BASE = "/output"
INTERVAL = int(os.getenv("CHECK_INTERVAL"))
CACHE_FILE = "/data/cache.json"
CATEGORY_MAP_RAW = os.getenv("TAG_DEST_MAP")

try:
    CATEGORY_MAP = dict(item.split(":", 1) for item in CATEGORY_MAP_RAW.split(","))
except Exception:
    logging.error("Error: TAG_DEST_MAP is not formatted correctly. Expected example: 'audiobook:/media/audiobooks,movies:/media/movies'")
    sys.exit(1)

# ==========================
# HTTP Session & qBittorrent API connection
# ==========================
session = requests.Session()

def login():
    resp = session.post(f"{QBITTORRENT_URL}/api/v2/auth/login", data={
        "username": QBITTORRENT_USERNAME,
        "password": QBITTORRENT_PASSWORD
    })
    if resp.text != "Ok.":
        raise RuntimeError("Connection to qBittorrent API failed")
    logging.info("Connection to qBittorrent succesful")

# ==========================
# Cache functions
# ==========================
def load_cache():
    if not os.path.exists(CACHE_FILE):
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump([], f)
        return set()

    try:
        with open(CACHE_FILE, "r") as f:
            return set(json.load(f))
    except json.JSONDecodeError:
        with open(CACHE_FILE, "w") as f:
            json.dump([], f)
        return set()

def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(list(cache), f)

# ==========================
# qBittorrent API functions
# ==========================
def get_completed_torrents():
    resp = session.get(f"{QBITTORRENT_URL}/api/v2/torrents/info?filter=completed")
    resp.raise_for_status()
    return resp.json()

def process_torrent(torrent, cache):
    torrent_hash = torrent["hash"]
    name = torrent["name"]
    save_path = torrent["save_path"]
    category = torrent["category"]

    if torrent_hash in cache:
        return

    if not os.path.exists(save_path):
        logging.error(f"[{name}] Unknown path: {save_path}")
        return
    if category in CATEGORY_MAP:
        dest_dir = os.path.join(CATEGORY_MAP[category], name)
        os.makedirs(dest_dir, exist_ok=True)
        try:
            torrent_src = os.path.join(save_path, name)
            if os.path.isfile(torrent_src):
                logging.info(f"[{name}] Copy: {torrent_src} → {dest_dir}")
                shutil.copy2(torrent_src, dest_dir)
            elif os.path.isdir(torrent_src):
                logging.info(f"[{name}] Copy: {torrent_src} → {dest_dir}")
                shutil.copytree(torrent_src, dest_dir,dirs_exist_ok=True)
            logging.info(f"[{name}] Copied")
            cache.add(torrent_hash)
        except OSError as e:
            logging.error(f"[{name}] Error during copy: {e}")

# ==========================
# Main loop
# ==========================
def main():
    logging.info("Watcher started.")
    cache = load_cache()
    login()

    while True:
        try:
            torrents = get_completed_torrents()
            for t in torrents:
                process_torrent(t, cache)
                save_cache(cache)
        except Exception as e:
            logging.error(f"Error: {e}")

        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
