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

SUBPETS_ID_RE = re.compile(r"^w(\d+)_PET_3D\.nii(?:\.gz)?$", re.IGNORECASE)
PET_SPACE_ID_RE = re.compile(r"^(\d+)_PET_3D\.nii(?:\.gz)?$", re.IGNORECASE)
VALID_EXT = (".nii", ".nii.gz")


def _is_better_file(candidate, current):
    if current is None:
        return True
    candidate_key = (0 if candidate.lower().endswith(".nii") else 1, candidate)
    current_key = (0 if current.lower().endswith(".nii") else 1, current)
    return candidate_key < current_key


def _index_pet_files(folder, pattern):
    indexed = {}
    if not os.path.isdir(folder):
        return indexed

    for entry in os.scandir(folder):
        if not entry.is_file():
            continue
        lower = entry.name.lower()
        if not lower.endswith(VALID_EXT):
            continue
        match = pattern.match(entry.name)
        if not match:
            continue
        sid = match.group(1)
        current = indexed.get(sid)
        if _is_better_file(entry.name, current):
            indexed[sid] = entry.name
    return indexed


def list_subjects():
    full_files = _index_pet_files(SUBPETS_DIR, SUBPETS_ID_RE)
    pet_space_files = _index_pet_files(PET_SPACE_DIR, PET_SPACE_ID_RE)
    subjects = []
    for sid, full_fn in full_files.items():
        pet_space_fn = pet_space_files.get(sid)
        subjects.append({
            "id": sid,
            "full_path": f"{SUBPETS_DIR}/{full_fn}",
            "pet_space_path": f"{PET_SPACE_DIR}/{pet_space_fn}" if pet_space_fn else None,
        })

    subjects.sort(key=lambda x: (int(x["id"]), x["id"]))
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
        for sid in sorted(notes_map.keys(), key=lambda x: (int(x), x)):
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

            subjects = list_subjects()
            subject_ids = [s["id"] for s in subjects]
            subject_id_set = set(subject_ids)

            cleaned = {}
            for k, v in notes_map.items():
                sid = str(k).strip()
                if sid not in subject_id_set:
                    continue
                cleaned[sid] = "" if v is None else str(v)

            write_notes_csv(cleaned, subject_ids=subject_ids)

            return self._send_json({"ok": True, "written": NOTES_CSV, "count": len(cleaned)})

        except Exception as e:
            return self._send_json({"ok": False, "error": str(e)}, status=500)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Serving on http://127.0.0.1:{PORT}/viewer.html")
    httpd.serve_forever()
