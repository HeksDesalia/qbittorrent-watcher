# 🧩 qBittorrent Watcher

**qBittorrent Watcher** is a lightweight Python service designed to automatically monitor completed torrents via the **qBittorrent API** and copy downloaded files or folders to specific destinations based on their **category**.

It includes a **little cache** to prevent duplicate processing and is fully configurable through **Docker environment variables**.

---

## 🚀 Features

✅ Monitors completed torrents using the qBittorrent Web API  
✅ Automatically copies finished downloads based on assigned tags  
✅ Handles both **single-file** and **multi-file** torrents  
✅ Little persistent cache with corruption handling (JSON file)
✅ Fully dynamic configuration via environment variables  
✅ Built-in scheduler (no cron required)  
✅ Compatible with **Python 3.12** and **Docker**

---

## 🐳 Docker Compose Deployment

### Example `docker-compose.yml`

```yaml
services:
  qbittorrent-watcher:
    build: ./qbittorrent-watcher
    container_name: qbittorrent-watcher
    environment:
      QBITTORRENT_URL: "http://qbittorrent:8080"
      QBITTORRENT_API_KEY: "your_api_key"
      DEST_BASE: "/output"
      CHECK_INTERVAL: "300"
      CACHE_FILE: "/data/cache.json"
      TAG_DEST_MAP: "anime:/output/anime,movies:/output/movies"
    volumes:
      - ./downloads:/downloads:ro
      - ./output:/output
      - ./cache:/data
    restart: unless-stopped
```

---

## ⚙️ Environment Variables

| Name                     | Description                                  | Example                                     |
| ------------------------ | -------------------------------------------- | ------------------------------------------- |
| **QBITTORRENT_URL**      | URL of the qBittorrent Web API               | `http://qbittorrent:8080`                   |
| **QBITTORRENT_USERNAME** | Login for authentication                     | `admin`                                     |
| **QBITTORRENT_PASSWORD** | Password for authentication                  | `password`                                  |
| **DEST_BASE**            | Base directory where files will be copied    | `/output`                                   |
| **CHECK_INTERVAL**       | Interval between each API check (in seconds) | `300`                                       |
| **CACHE_FILE**           | Path to the persistent cache file            | `/data/cache.json`                          |
| **TAG_DEST_MAP**         | Categies → destination directory mapping     | `anime:/output/anime,movies:/output/movies` |

> ⚠️ Each category defined in qBittorrent must appear in `TAG_DEST_MAP`; otherwise, it will be ignored.

---

## 📂 Volume Structure

| Volume                      | Content                                              | Access     |
| --------------------------- | ---------------------------------------------------- | ---------- |
| `./downloads:/downloads:ro` | The folder where qBittorrent stores downloaded files | Read-only  |
| `./output:/output`          | Destination folder where files will be copied        | Read/Write |
| `./cache:/data`             | Folder containing the persistent cache file          | Read/Write |

---

## 🧠 How It Works

1. The watcher queries qBittorrent every `CHECK_INTERVAL` seconds using its Web API.
2. It lists all **completed torrents** (`filter=completed`).
3. For each torrent, it checks the cache to avoid duplicates.
4. It reads the **category** assigned to each torrent and looks for a match in `TAG_DEST_MAP`.
5. Depending on the category, it copies the corresponding **file** or **folder** to the destination.
6. The torrent hash is then stored in the cache once successfully processed.

---

## 🧰 Build the Image Manually

```bash
docker build -t qbittorrent-watcher .
```

Then run it:

```bash
docker run --rm   -e QBITTORRENT_URL=http://qbittorrent:8080   -e QBITTORRENT_API_KEY=your_api_key   -e DEST_BASE=/output   -e CHECK_INTERVAL=300   -e CACHE_FILE=/data/cache.json   -e TAG_DEST_MAP="anime:/output/anime,movies:/output/movies"   -v ./downloads:/downloads:ro   -v ./output:/output   -v ./cache:/data   qbittorrent-watcher
```

---

## ⚠️ Important Notes

- The `/downloads` volume **must match** qBittorrent’s download directory.
- The mount is read-only (`:ro`) to prevent accidental file modifications.
- The cache file persists between container restarts to avoid reprocessing torrents.

---

## 🧱 License

**MIT License** — free to use and modify, even for commercial purposes.
