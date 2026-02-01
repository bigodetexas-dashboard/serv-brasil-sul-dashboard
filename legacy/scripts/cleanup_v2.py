import os
import shutil

# Root directory
root = r"d:\dayz xbox\BigodeBot"
legacy_dir = os.path.join(root, "legacy")

# Files to KEEP in root
keep_files = {
    ".editorconfig",
    ".env",
    ".env.configured",
    ".env.example",
    ".gitignore",
    "BigodeTexas Launcher.lnk",
    "Procfile",
    "README.md",
    "abrir_dashboard.bat",
    "ai_integration.py",
    "analytics.py",
    "banner_bigode_texas.png",
    "bigode_unified.db",
    "bot_avatar.png",
    "bot_main.py",
    "bot_state.json",
    "bot_wrapper.py",
    "cfggameplay.json",
    "config.json",
    "database_schema.sql",
    "delivery_processor.py",
    "discord_oauth.py",
    "gameplay_editor.py",
    "health_check.py",
    "heatmap.png",
    "init.c",
    "init_sqlite_db.py",
    "launcher.bat",
    "launcher_icon.ico",
    "logo_texas.png",
    "missions.json",
    "push_notifications.py",
    "pvp_events.db",
    "requirements.txt",
    "restart_manager.py",
    "run_bot.bat",
    "run_dashboard.bat",
    "run_killfeed.bat",
    "runtime.txt",
    "security.py",
    "spawn_system.py",
    "spawn_queue.json",
    "start_bot.py",
    "verify_project.py",
    "verification_report.json",
    "HOSTING_GUIDE.md",
    "DEPLOY.md",
    "SETUP_GUIDE.md",
}
# Removed web_dashboard.py from keep_files

# Directories to KEEP
keep_dirs = {
    ".git",
    ".ruff_cache",
    ".vscode",
    "__pycache__",
    "backups",
    "cogs",
    "logs",
    "new_dashboard",
    "reports",
    "repositories",
    "static",
    "templates",
    "utils",
    "legacy",
}

if not os.path.exists(legacy_dir):
    os.makedirs(legacy_dir)

# Subdirectories in legacy
legacy_scripts = os.path.join(legacy_dir, "scripts")
legacy_docs = os.path.join(legacy_dir, "docs")
legacy_tests = os.path.join(legacy_dir, "tests")

for d in [legacy_scripts, legacy_docs, legacy_tests]:
    if not os.path.exists(d):
        os.makedirs(d)

files_moved = 0

for item in os.listdir(root):
    if item == "cleanup_v1.py" or item == "cleanup_v2.py":  # Skip ourselves
        continue

    item_path = os.path.join(root, item)

    # Check for archive folders first
    if os.path.isdir(item_path) and item.endswith("_archive"):
        print(f"Moving archive folder: {item}")
        try:
            shutil.move(item_path, os.path.join(legacy_dir, item))
            files_moved += 1
        except Exception as e:
            print(f"Error moving folder {item}: {e}")
        continue

    # Skip directories we want to keep
    if os.path.isdir(item_path):
        if item in keep_dirs:
            continue
        # For other non-essential dirs, maybe move them?
        # But let's be conservative with unknown dirs.
        continue

    # Skip files we want to keep
    if item in keep_files:
        continue

    # Move files based on type
    target = legacy_scripts
    if item.endswith(".md"):
        target = legacy_docs
    elif item.startswith("test_") or "test" in item.lower():
        target = legacy_tests
    elif item.endswith(".txt") or item.endswith(".log"):
        target = legacy_scripts

    try:
        shutil.move(item_path, os.path.join(target, item))
        print(f"Moved: {item} -> {target}")
        files_moved += 1
    except Exception as e:
        print(f"Error moving {item}: {e}")

print(f"\nTotal items moved to legacy: {files_moved}")
