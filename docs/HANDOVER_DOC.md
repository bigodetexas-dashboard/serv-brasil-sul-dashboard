# 📂 BigodeTexas Project - Handover Documentation

**Date:** 30/01/2026
**Status:** Stable (Auto-Healing Active)

## 🌟 Project Overview

BigodeTexas is a comprehensive management system for a DayZ Xbox server. It consists of a **Discord Bot** and a **Web Dashboard** integrated via a shared SQLite database.

### 🏗 Architecture

- **Backend:** Python (Flask for Web, discord.py for Bot).
- **Database:** SQLite (`bigode_unified.db`).
- **Frontend:** HTML5/CSS3 (Glassmorphism Design), Vanilla JS.
- **Hosting:** Runs locally on Windows (`d:\dayz xbox\BigodeBot`).

---

## 🚀 Recent Implementations (The "Auto-Gravity" Update)

### 1. Auto-Healing System (Resilience)

- **`guard_dog.py`**: The new entry point. Monitors the bot process, handles crashes, and prevents infinite restart loops (max 5 restarts/10min).
- **`doctor.py`**: Called after a crash. Performs diagnostics:
  - **DB Check:** Runs `PRAGMA integrity_check`. Restores from `backups/` if corrupt.
  - **Dependencies:** Checks/installs `requirements.txt`.
  - **Port Killer:** Forcefully frees port 5001/3000 if stuck (Zombie processes).

### 2. Feature Activation (Backend -> Frontend)

- **Shop (`/api/shop`)**: Now fetches items from the `shop_items` SQL table using `ItemRepository`. Replaced legacy JSON.
- **Clan Wars (`/api/wars`)**: Added "Declare War" button and backend logic.

### 3. Base Permissions System

- **Repository**: `repositories/player_base_repository.py` handles Bases and Permissions.
- **Database**: Added `bases_v2` and `base_permissions` tables.
- **UI**: New "Manage Bases" interface in `base.html` with tabs and permission modals.

### 4. Real-Time Dashboard (WebSockets)

- **Engine**: `Flask-SocketIO` running with `eventlet` (production-ready).
- **Database**: Created `dashboard_events` table and `EventsRepository`.
- **Flow**: Bot POSTs to `/api/events/emit` -> Server broadcasts via WebSocket -> Frontend (`realtime.js`) updates Killfeed/Status.
- **Frontend**: Killfeed updates instantly without page refresh.

### 5. Bot Integration (New!)

- **Helper**: `utils/dashboard_api.py` sends async POST requests.
- **Bot (`bot_main.py`)**: Updated `parse_log_line` (Killfeed) and `restart_server` to call the dashboard API.
- **Status**: Code implemented. Requires Bot Restart.
- **CRITICAL FIX**: Fixed `on_ready()` to properly start background loops (`killfeed_loop`, `backup_loop`, `raid_scheduler`) which were previously disconnected.

---

## 📝 Critical Files

| File | Purpose |
|------|---------|
| `launcher.bat` | **START HERE**. Runs `guard_dog.py`. |
| `guard_dog.py` | Process monitor and supervisor. |
| `doctor.py` | Diagnostic and repair tool. |
| `web_dashboard.py` (app.py) | Flask App + SocketIO + API. |
| `repositories/events_repository.py` | Handles logging of real-time events. |
| `new_dashboard/static/js/realtime.js`| WebSocket Client logic. |
| `bot_main.py` | Discord Bot (Updated with API calls). |
| `bot_main.py` | Discord Bot (Updated with API calls). |
| `utils/dashboard_api.py` | Helper for Bot -> Dashboard communication. |

---

## 🔍 Verification Log (31/01/2026)

1. **Pen Drive Analysis**: Found version `10.1` (outdated). Current local version is superior. No action needed.
2. **Nitrado Integration**: Confirmed Hybrid System.
    - **API**: Used for Restart, Stop, Ban, and Status checks.
    - **FTP**: Used for Killfeed (logs) and complete player lists.
3. **FTP Optimization**: Implemented `REST` command in `bot_main.py`. Killfeed now downloads only *new bytes* (Incremental) instead of the full file, reducing latency and bandwidth.
4. **Critical Fix**: Patched `bot_main.py` to auto-start background loops (`killfeed_loop`, etc.) upon startup.
5. **Domain Configuration**:
    - **Cloudflare**: Configured `bigodetexas.com` and `www` to point to `serv-brasil-sul-dashboard.onrender.com`.
    - **CORS**: Updated `app.py` to allow traffic from `bigodetexas.com`.
    - **Status**: Propagation active.

---

## ⏳ Pending / Next Steps

### 1. Final Validation

- **Action:** Restart both the Dashboard (`launcher.bat`) and the Bot (`start_bot.bat`).
- **Test:** Perform an action in-game or simulate a restart and check if the Dashboard Killfeed updates.

### 2. Validation & Stress Testing

- Monitor memory usage of `eventlet` loop.
- Verify `shop_items` table migration on production (if not done yet).

---

## 🔧 How to Run

1. Open Terminal/CMD.
2. Run `launcher.bat`.
3. Access Dashboard: `http://127.0.0.1:5001`.

## 📂 Key Artifacts (Created/Modified)

- `HANDOVER_DOC.md`: This file.
- `repositories/player_base_repository.py`
- `new_dashboard/static/js/shop.js`
- `new_dashboard/static/js/realtime.js`
- `tests/test_realtime.py`

---
*Last Updated: 2026-01-31 by Antigravity Assistant.*
