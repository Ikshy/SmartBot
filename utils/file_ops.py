import os, shutil, json
from datetime import datetime
from pathlib import Path
from utils.logger import get_logger, log_action

logger = get_logger(__name__)
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "config.json")

def _load_file_types():
    with open(_CONFIG_PATH) as f:
        return json.load(f)["file_types"]

FILE_TYPES = _load_file_types()

def _resolve_conflict(dest_path):
    if not os.path.exists(dest_path):
        return dest_path
    base, ext = os.path.splitext(dest_path)
    return f"{base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"

def _get_category(filename):
    ext = Path(filename).suffix.lower()
    for category, extensions in FILE_TYPES.items():
        if ext in extensions:
            return category
    return "misc"

def move_file(src, dest_dir):
    try:
        os.makedirs(dest_dir, exist_ok=True)
        dest = _resolve_conflict(os.path.join(dest_dir, os.path.basename(src)))
        shutil.move(src, dest)
        log_action("file_ops", "MOVE", f"{src} → {dest}")
        return dest
    except Exception as e:
        logger.error(f"Move failed {src}: {e}")
        return None

def copy_file(src, dest_dir):
    try:
        os.makedirs(dest_dir, exist_ok=True)
        dest = _resolve_conflict(os.path.join(dest_dir, os.path.basename(src)))
        shutil.copy2(src, dest)
        log_action("file_ops", "COPY", f"{src} → {dest}")
        return dest
    except Exception as e:
        logger.error(f"Copy failed {src}: {e}")
        return None

def delete_file(path):
    try:
        os.remove(path)
        log_action("file_ops", "DELETE", path)
        return True
    except Exception as e:
        logger.error(f"Delete failed {path}: {e}")
        return False

def rename_file(src, new_name):
    try:
        dest = _resolve_conflict(os.path.join(os.path.dirname(src), new_name))
        os.rename(src, dest)
        log_action("file_ops", "RENAME", f"{src} → {dest}")
        return dest
    except Exception as e:
        logger.error(f"Rename failed {src}: {e}")
        return None

def organize_folder(source_dir, target_dir):
    source_dir = os.path.expanduser(source_dir)
    target_dir = os.path.expanduser(target_dir)
    summary = {}
    if not os.path.isdir(source_dir):
        logger.warning(f"Source not found: {source_dir}")
        return summary
    for filename in os.listdir(source_dir):
        filepath = os.path.join(source_dir, filename)
        if os.path.isdir(filepath) or filename.startswith("."):
            continue
        category = _get_category(filename)
        result = move_file(filepath, os.path.join(target_dir, category))
        if result:
            summary.setdefault(category, []).append(filename)
    return summary

def list_files(directory, recursive=False):
    directory = os.path.expanduser(directory)
    if not os.path.isdir(directory):
        return []
    if recursive:
        return [str(p) for p in Path(directory).rglob("*") if p.is_file()]
    return [os.path.join(directory, f) for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))]