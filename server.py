#!/usr/bin/env python3
import os
import re
import json
import csv
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

PORT = 8000
SUBPETS_DIR = "subPETs"
PET_SPACE_DIR = "PET_Space"
NOTES_CSV = "notes.csv"

ID_RE = re.compile(r"w(\d{6})", re.IGNORECASE)
VALID_EXT = (".nii", ".nii.gz")


def _pick_best_file(folder, sid):
    """
    Choose a PET file for a given ID in a folder.
    Preference: .nii (faster to decode) > .nii.gz
    """
    if not os.path.isdir(folder):
        return None

    candidates = []
    for fn in os.listdir(folder):
        lower = fn.lower()
        if not lower.endswith(VALID_EXT):
            continue
        m = ID_RE.search(fn)
        if not m:
            continue
        if m.group(1) != sid:
            continue
        candidates.append(fn)

    if not candidates:
        return None

    # Prefer .nii over .nii.gz
    candidates.sort(key=lambda x: (0 if x.lower().endswith(".nii") else 1, x))
    return candidates[0]


def list_subjects():
    # Build set of IDs from full-res folder
    ids = set()
    if os.path.isdir(SUBPETS_DIR):
        for fn in os.listdir(SUBPETS_DIR):
            lower = fn.lower()
            if not lower.endswith(VALID_EXT):
                continue
            m = ID_RE.search(fn)
            if m:
                ids.add(m.group(1))

    subjects = []
    for sid in ids:
        full_fn = _pick_best_file(SUBPETS_DIR, sid)
        pet_space_fn = f"{sid}_PET_3D.nii"
        pet_space_abs = os.path.join(PET_SPACE_DIR, pet_space_fn)
        pet_space_path = f"{PET_SPACE_DIR}/{pet_space_fn}" if os.path.isfile(pet_space_abs) else None

        full_path = f"{SUBPETS_DIR}/{full_fn}" if full_fn else None

        if full_path:
            subjects.append({
                "id": sid,
                "full_path": full_path,
                "pet_space_path": pet_space_path,
            })

    subjects.sort(key=lambda x: int(x["id"]))
    return subjects


def read_notes_csv():
    notes = {}
    if not os.path.isfile(NOTES_CSV):
        return notes
    try:
        with open(NOTES_CSV, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sid = (row.get("ID") or "").strip()
                txt = row.get("IN_Notes") or ""
                if sid:
                    notes[sid] = txt
    except Exception:
        return {}
    return notes


def write_notes_csv(notes_map, subject_ids=None):
    rows = []
    if subject_ids:
        for sid in subject_ids:
            rows.append({"ID": sid, "IN_Notes": notes_map.get(sid, "")})
    else:
        for sid in sorted(notes_map.keys(), key=lambda x: int(x)):
            rows.append({"ID": sid, "IN_Notes": notes_map.get(sid, "")})

    with open(NOTES_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ID", "IN_Notes"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


class Handler(SimpleHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/subjects":
            subs = list_subjects()
            return self._send_json({"subjects": subs})

        if parsed.path == "/api/notes":
            notes = read_notes_csv()
            return self._send_json({"notes": notes})

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/notes":
            self.send_error(404, "Not Found")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8", errors="replace")
            payload = json.loads(body) if body else {}

            notes_map = payload.get("notes", {})
            if not isinstance(notes_map, dict):
                return self._send_json({"ok": False, "error": "notes must be an object/dict"}, status=400)

            cleaned = {}
            for k, v in notes_map.items():
                sid = str(k).strip()
                if not re.fullmatch(r"\d{6}", sid):
                    continue
                cleaned[sid] = "" if v is None else str(v)

            subjects = list_subjects()
            subject_ids = [s["id"] for s in subjects]
            write_notes_csv(cleaned, subject_ids=subject_ids)

            return self._send_json({"ok": True, "written": NOTES_CSV, "count": len(cleaned)})

        except Exception as e:
            return self._send_json({"ok": False, "error": str(e)}, status=500)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Serving on http://127.0.0.1:{PORT}/viewer.html")
    httpd.serve_forever()
