#!/usr/bin/env python3
import os
import re
import json
import csv
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PET_MNI_DIR = "PET_MNI"
PET_SPACE_DIR = "PET_Space"
EXAMPLE_DIR = "Example"
NOTES_CSV = "notes.csv"
CENTILOIDS_CSV = "Cohort_Centiloids.csv"
NOTES_FIELDS = [
    "ID",
    "IN_Notes",
    "IN_Case_Status",
    "IN_Flag_For_Review",
    "IN_Needs_Processing_QC",
]
VALID_CASE_STATUSES = {"", "Positive", "Negative", "Borderline"}

PET_MNI_ID_RE = re.compile(r"^w(\d+)_PET_3D\.nii(?:\.gz)?$", re.IGNORECASE)
PET_SPACE_ID_RE = re.compile(r"^(\d+)_PET_3D\.nii(?:\.gz)?$", re.IGNORECASE)
VALID_EXT = (".nii", ".nii.gz")


def _is_better_file(candidate, current):
    if current is None:
        return True
    candidate_key = (0 if candidate.lower().endswith(".nii") else 1, candidate)
    current_key = (0 if current.lower().endswith(".nii") else 1, current)
    return candidate_key < current_key


def _resolve_data_dir(preferred_rel, fallback_rel):
    preferred_abs = os.path.join(BASE_DIR, preferred_rel)
    if os.path.isdir(preferred_abs):
        return preferred_rel, preferred_abs

    fallback_abs = os.path.join(BASE_DIR, fallback_rel)
    return fallback_rel, fallback_abs


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
    pet_mni_rel, pet_mni_abs = _resolve_data_dir(PET_MNI_DIR, os.path.join(EXAMPLE_DIR, PET_MNI_DIR))
    pet_space_rel, pet_space_abs = _resolve_data_dir(PET_SPACE_DIR, os.path.join(EXAMPLE_DIR, PET_SPACE_DIR))

    full_files = _index_pet_files(pet_mni_abs, PET_MNI_ID_RE)
    pet_space_files = _index_pet_files(pet_space_abs, PET_SPACE_ID_RE)
    subjects = []
    for sid, full_fn in full_files.items():
        pet_space_fn = pet_space_files.get(sid)
        subjects.append({
            "id": sid,
            "full_path": f"{pet_mni_rel}/{full_fn}",
            "pet_space_path": f"{pet_space_rel}/{pet_space_fn}" if pet_space_fn else None,
        })

    subjects.sort(key=lambda x: (int(x["id"]), x["id"]))
    return subjects


def _subject_sort_key(sid):
    try:
        return (0, int(sid), sid)
    except ValueError:
        return (1, sid)


def _parse_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    return str(value or "").strip().lower() in {"true", "1", "yes", "y"}


def _csv_bool(value):
    return "TRUE" if _parse_bool(value) else "FALSE"


def _normalize_review(value):
    if not isinstance(value, dict):
        value = {}
    case_status = str(value.get("case_status") or value.get("IN_Case_Status") or "").strip()
    if case_status not in VALID_CASE_STATUSES:
        case_status = ""
    return {
        "case_status": case_status,
        "flag_for_review": _parse_bool(value.get("flag_for_review", value.get("IN_Flag_For_Review"))),
        "needs_processing_qc": _parse_bool(value.get("needs_processing_qc", value.get("IN_Needs_Processing_QC"))),
    }


def read_notes_csv():
    notes = {}
    review = {}
    if not os.path.isfile(NOTES_CSV):
        return notes, review
    try:
        with open(NOTES_CSV, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sid = (row.get("ID") or "").strip()
                txt = row.get("IN_Notes") or ""
                if sid:
                    notes[sid] = txt
                    review[sid] = _normalize_review(row)
    except Exception:
        return {}, {}
    return notes, review


def read_centiloids_csv():
    centiloids = {}
    if not os.path.isfile(CENTILOIDS_CSV):
        return centiloids
    try:
        with open(CENTILOIDS_CSV, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or "Subject" not in reader.fieldnames or "CL" not in reader.fieldnames:
                return {}
            for row in reader:
                sid = (row.get("Subject") or "").strip()
                cl = (row.get("CL") or "").strip()
                if sid and cl:
                    centiloids[sid] = cl
    except Exception:
        return {}
    return centiloids


def write_notes_csv(notes_map, review_map=None, subject_ids=None):
    review_map = review_map or {}
    rows = []
    if subject_ids:
        row_ids = subject_ids
    else:
        row_ids = sorted(set(notes_map.keys()) | set(review_map.keys()), key=_subject_sort_key)

    for sid in row_ids:
        review = _normalize_review(review_map.get(sid))
        rows.append({
            "ID": sid,
            "IN_Notes": notes_map.get(sid, ""),
            "IN_Case_Status": review["case_status"],
            "IN_Flag_For_Review": _csv_bool(review["flag_for_review"]),
            "IN_Needs_Processing_QC": _csv_bool(review["needs_processing_qc"]),
        })

    with open(NOTES_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=NOTES_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    return sum(1 for r in rows if r["IN_Notes"] or r["IN_Case_Status"] or r["IN_Flag_For_Review"] == "TRUE" or r["IN_Needs_Processing_QC"] == "TRUE")


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def _send_json(self, obj, status=200):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/subjects":
            subs = list_subjects()
            return self._send_json({"subjects": subs})

        if parsed.path == "/api/notes":
            notes, review = read_notes_csv()
            return self._send_json({"notes": notes, "review": review})

        if parsed.path == "/api/centiloids":
            centiloids = read_centiloids_csv()
            return self._send_json({"centiloids": centiloids})

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

            review_map = payload.get("review", {})
            if not isinstance(review_map, dict):
                return self._send_json({"ok": False, "error": "review must be an object/dict"}, status=400)

            subjects = list_subjects()
            subject_ids = [s["id"] for s in subjects]
            subject_id_set = set(subject_ids)

            cleaned = {}
            for k, v in notes_map.items():
                sid = str(k).strip()
                if sid not in subject_id_set:
                    continue
                cleaned[sid] = "" if v is None else str(v)

            cleaned_review = {}
            for k, v in review_map.items():
                sid = str(k).strip()
                if sid not in subject_id_set:
                    continue
                cleaned_review[sid] = _normalize_review(v)

            count = write_notes_csv(cleaned, cleaned_review, subject_ids=subject_ids)

            return self._send_json({"ok": True, "written": NOTES_CSV, "count": count})

        except Exception as e:
            return self._send_json({"ok": False, "error": str(e)}, status=500)


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Serving on http://127.0.0.1:{PORT}/viewer.html")
    httpd.serve_forever()
