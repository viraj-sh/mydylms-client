import argparse
import hashlib
import json
import re
from pathlib import Path

MAP_FILE = ".asset_hash_map.json"
JS_DIR = Path("js")
CSS_DIR = Path("css")
PROJECT_ROOT = Path(".")
HTML_EXTS = {".html", ".htm"}
HASH_LEN = 8  # characters from sha256


def compute_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()[:HASH_LEN]


def find_files(dir_path: Path, ext: str):
    if not dir_path.exists():
        return []
    return [p for p in dir_path.iterdir() if p.is_file() and p.suffix == ext]


def find_html_files():
    return [
        p
        for p in PROJECT_ROOT.rglob("*")
        if p.is_file() and p.suffix.lower() in HTML_EXTS
    ]


def load_map():
    if Path(MAP_FILE).exists():
        return json.loads(Path(MAP_FILE).read_text())
    return {}


def save_map(m):
    Path(MAP_FILE).write_text(json.dumps(m, indent=2))


def apply_hashes():
    assets = {"js": find_files(JS_DIR, ".js"), "css": find_files(CSS_DIR, ".css")}

    if not any(assets.values()):
        print("No JS or CSS files found.")
        return

    existing_map = load_map()
    if existing_map:
        print(
            "Existing mapping found. To start fresh, run `python3 hash.py unhash` first."
        )

    mapping = {}

    for asset_type, files in assets.items():
        for p in files:
            orig_name = p.name
            if re.match(r"^(.+?)\.[0-9a-f]{6,}\.(js|css)$", orig_name):
                print(f"Skipping already-hashed file: {orig_name}")
                continue
            h = compute_hash(p)
            new_name = f"{p.stem}.{h}{p.suffix}"
            print(f"Renaming {orig_name} -> {new_name}")
            p.rename(p.with_name(new_name))
            mapping[orig_name] = new_name

    if not mapping:
        print("No files were renamed.")
        return

    html_files = find_html_files()
    for hf in html_files:
        s = hf.read_text()
        orig_s = s
        for orig, new in mapping.items():
            s = re.sub(rf"(/js/{orig}|js/{orig})", f"/js/{new}", s)
            s = re.sub(rf"(/static/css/{orig}|css/{orig})", f"/static/css/{new}", s)
        if s != orig_s:
            hf.write_text(s)
            print(f"Updated HTML references in {hf}")

    saved_map = load_map()
    saved_map.update(mapping)
    save_map(saved_map)
    print(f"Saved mapping to {MAP_FILE}")


def infer_mapping_from_filenames():
    mapping = {}
    for p in find_files(JS_DIR, ".js") + find_files(CSS_DIR, ".css"):
        m = re.match(r"^(.+?)\.([0-9a-f]{6,})\.(js|css)$", p.name)
        if m:
            base = m.group(1) + "." + m.group(3)
            mapping[base] = p.name
    return mapping


def remove_hashes():
    mapping = load_map()
    inferred = False
    if not mapping:
        print("No mapping file found; attempting to infer from filenames...")
        mapping = infer_mapping_from_filenames()
        inferred = True

    if not mapping:
        print("No hashed files found to unhash.")
        return

    rev = {v: k for k, v in mapping.items()}

    for hashed, orig in rev.items():
        dir_path = JS_DIR if hashed.endswith(".js") else CSS_DIR
        hashed_path = dir_path / hashed
        orig_path = dir_path / orig
        if not hashed_path.exists():
            print(f"Hashed file not found (skipping): {hashed}")
            continue
        if orig_path.exists():
            backup = orig_path.with_suffix(orig_path.suffix + ".bak")
            print(f"Conflict: {orig} exists. Moving existing to {backup}")
            orig_path.rename(backup)
        print(f"Restoring {hashed} -> {orig}")
        hashed_path.rename(orig_path)

    html_files = find_html_files()
    for hf in html_files:
        s = hf.read_text()
        orig_s = s
        for orig, new in mapping.items():
            s = re.sub(rf"(/js/{new}|js/{new})", f"/js/{orig}", s)
            s = re.sub(rf"(/static/css/{new}|css/{new})", f"/static/css/{orig}", s)
        if s != orig_s:
            hf.write_text(s)
            print(f"Updated HTML references in {hf}")

    if Path(MAP_FILE).exists() and not inferred:
        print(f"Removing mapping file {MAP_FILE}")
        Path(MAP_FILE).unlink()
    elif inferred:
        print("Inferred mapping was used; no mapping file removed.")

    print("Unhashing complete.")


def main():
    parser = argparse.ArgumentParser(
        description="Hash/unhash JS and CSS files and update HTML references"
    )
    parser.add_argument("action", choices=["hash", "unhash"])
    args = parser.parse_args()

    if args.action == "hash":
        apply_hashes()
    else:
        remove_hashes()


if __name__ == "__main__":
    main()
