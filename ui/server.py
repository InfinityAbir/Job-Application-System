"""Local dashboard for the Job Application System.

    python ui/server.py            # then open http://127.0.0.1:8765
    python ui/server.py --no-open  # do not open the browser
    python ui/server.py --demo     # fictional sample data, read-only (safe to show or host)

Standard library only. Binds to 127.0.0.1 and refuses foreign Host headers and cross-site POSTs.
The server never calls an AI model; AI steps are done by whichever AI coding agent you use, with the prompts the UI gives you.
"""
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
UI = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
import track  # noqa: E402

PORT = int(os.environ.get("PORT", 8765))
DEMO = "--demo" in sys.argv
if DEMO:  # fictional, read-only data; real files are never touched or served
    ROOT = UI / "demo"
    track.FILE = ROOT / "applications.csv"
# Only the fictional read-only demo may listen publicly (hosting platforms set PORT). The real dashboard is localhost-only, always.
HOST = "0.0.0.0" if (DEMO and os.environ.get("PORT")) else "127.0.0.1"
if not DEMO:
    PORT = 8765
STATUSES = ["applied", "interview", "offer", "rejected", "ghosted"]
VIEW_EXT = {".md", ".txt", ".json", ".csv", ".pdf"}
EDIT_EXT = {".md", ".txt", ".json"}
OPEN_EXT = {".pdf", ".docx", ".md", ".txt", ".json"}


def safe_path(rel: str, roots=("jobs", "profile")) -> Path:
    p = (ROOT / rel).resolve()
    for r in roots:
        try:
            p.relative_to((ROOT / r).resolve())
            return p
        except ValueError:
            continue
    raise PermissionError("path not allowed")


def job_folders():
    d = ROOT / "jobs"
    return sorted([x for x in d.iterdir() if x.is_dir() and not x.name.startswith("_")], reverse=True) if d.exists() else []


def trash_dir() -> Path:
    return (ROOT / "jobs" / "_trash").resolve()


def trash_entry(name: str) -> Path:
    """Validated path of one entry inside jobs/_trash. Never anything outside it."""
    if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9._-]*", name or ""):
        raise ValueError("bad trash name")
    p = (trash_dir() / name).resolve()
    if p.parent != trash_dir() or not p.is_dir():
        raise PermissionError("not a trash entry")
    return p


def trash_entries():
    out = []
    t = trash_dir()
    if t.exists():
        for d in sorted((x for x in t.iterdir() if x.is_dir()), key=lambda x: x.name, reverse=True):
            meta = {}
            try:
                meta = json.loads((d / ".row.json").read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                pass
            files = sum(1 for p in d.rglob("*") if p.is_file() and p.name != ".row.json")
            out.append({"name": d.name, "company": meta.get("company", d.name), "role": meta.get("role", ""),
                        "status": meta.get("status", ""), "deleted": meta.get("_deleted", ""), "files": files})
    return out


def list_files(folder: Path):
    out = []
    for p in sorted(folder.rglob("*")):
        if p.is_file():
            out.append({"path": p.relative_to(ROOT).as_posix(), "name": p.relative_to(folder).as_posix(), "size": p.stat().st_size})
    return out


def state():
    rows = track.load()
    for i, r in enumerate(rows):
        r["idx"] = i
        f = (r.get("folder") or "").rstrip("/")
        r["folder"] = f
        r["exists"] = bool(f) and (ROOT / f).is_dir()
    jobs = {f.relative_to(ROOT).as_posix(): list_files(f) for f in job_folders()}
    todos = 0
    for p in ("profile/master_profile.md", "profile/stories.md"):
        fp = ROOT / p
        if fp.exists():
            t = fp.read_text(encoding="utf-8", errors="replace")
            todos += t.count("TODO") + t.count("[FILL IN")
    return {"demo": DEMO, "todos": todos, "trash": trash_entries(), "rows": rows, "files": jobs, "statuses": STATUSES, "today": __import__("datetime").date.today().isoformat(),
            "profile": [p for p in ["profile/master_profile.md", "profile/stories.md"] if (ROOT / p).exists()]}


def run(cmd, timeout=240):
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
    return (r.stdout + r.stderr).strip(), r.returncode


def set_readme_status(folder: Path, status: str, note: str = ""):
    rd = folder / "README.md"
    if not rd.exists():
        return
    t = rd.read_text(encoding="utf-8")
    t = re.sub(r"(\| Status \| ).*?( \|)", lambda m: f"{m.group(1)}{status}{m.group(2)}", t, count=1)
    from datetime import date
    t = t.rstrip("\n") + f"\n- {date.today().isoformat()}: status set to {status}" + (f" ({note})" if note else "") + "\n"
    rd.write_text(t, encoding="utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "JobSys/1.0"

    def log_message(self, fmt, *args):
        pass

    # ---- helpers
    def host_ok(self):
        if DEMO and HOST == "0.0.0.0":  # hosted read-only demo: any host allowed, nothing sensitive is served
            return True
        return (self.headers.get("Host") or "") in (f"127.0.0.1:{PORT}", f"localhost:{PORT}")

    def send_json(self, obj, code=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def fail(self, code, msg):
        self.send_json({"error": msg}, code)

    # ---- GET
    def do_GET(self):
        if not self.host_ok():
            return self.fail(403, "bad host")
        u = urlparse(self.path)
        try:
            if u.path in ("/", "/index.html"):
                body = (UI / "index.html").read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
            elif u.path == "/favicon.ico":
                self.send_response(204)
                self.end_headers()
            elif u.path == "/api/state":
                self.send_json(state())
            elif u.path == "/api/file":
                p = safe_path(parse_qs(u.query)["path"][0])
                if p.suffix.lower() not in VIEW_EXT or not p.is_file():
                    return self.fail(404, "not viewable")
                data = p.read_bytes()
                ctype = mimetypes.guess_type(str(p))[0] or "text/plain"
                if p.suffix.lower() != ".pdf":
                    ctype += "; charset=utf-8"
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(data)
            else:
                self.fail(404, "not found")
        except PermissionError as e:
            self.fail(403, str(e))
        except Exception as e:  # noqa: BLE001
            self.fail(500, f"{type(e).__name__}: {e}")

    # ---- POST
    def do_POST(self):
        if not self.host_ok():
            return self.fail(403, "bad host")
        if DEMO:
            return self.fail(403, "Demo mode is read-only")
        if self.headers.get("X-Requested-With") != "jobsys" or "application/json" not in (self.headers.get("Content-Type") or ""):
            return self.fail(403, "bad request origin")
        try:
            n = int(self.headers.get("Content-Length") or 0)
            if n > 2_000_000:
                return self.fail(413, "too large")
            data = json.loads(self.rfile.read(n) or b"{}")
            route = urlparse(self.path).path.removeprefix("/api/").replace("-", "_")
            fn = getattr(self, "api_" + route, None) if re.fullmatch(r"[a-z_]+", route) else None
            if not fn:
                return self.fail(404, "unknown route")
            self.send_json(fn(data))
        except PermissionError as e:
            self.fail(403, str(e))
        except Exception as e:  # noqa: BLE001
            self.fail(500, f"{type(e).__name__}: {e}")

    # ---- API handlers
    def api_add(self, d):
        company, role = (d.get("company") or "").strip(), (d.get("role") or "").strip()
        if not company or not role:
            raise ValueError("company and role are required")
        cmd = [sys.executable, "scripts/new_job.py", company, role]
        for flag, key in (("--url", "url"), ("--source", "source"), ("--deadline", "deadline")):
            if (d.get(key) or "").strip():
                cmd += [flag, d[key].strip()]
        out, code = run(cmd)
        if code:
            raise RuntimeError(out)
        folder = Path(out.splitlines()[-1].strip())
        jd = (d.get("jd") or "").strip()
        if jd:
            f = folder / "01_job-description.md"
            head = f.read_text(encoding="utf-8").split("---", 1)[0] if f.exists() else ""
            f.write_text(head + "---\n\n" + jd + "\n", encoding="utf-8")
        return {"folder": folder.relative_to(ROOT).as_posix()}

    def api_update(self, d):
        rows = track.load()
        r = rows[int(d["idx"])]
        if "status" in d:
            if d["status"] not in STATUSES:
                raise ValueError("bad status")
            r["status"] = d["status"]
            if d["status"] in ("rejected", "offer", "ghosted"):
                r["follow_up"] = ""
        for k in ("follow_up", "note", "company", "role", "url"):
            if k in d:
                v = str(d[k]).strip() if k in ("company", "role", "url") else str(d[k])
                if k in ("company", "role") and not v:
                    raise ValueError(f"{k} cannot be empty")
                r[k] = v
        track.save(rows)
        f = (r.get("folder") or "").rstrip("/")
        if ("company" in d or "role" in d) and f and (ROOT / f).is_dir():
            rd = safe_path(f, ("jobs",)) / "README.md"
            if rd.exists():
                lines = rd.read_text(encoding="utf-8").split("\n")
                if lines and lines[0].startswith("# "):
                    lines[0] = f"# {r['company']}: {r['role']}"
                    rd.write_text("\n".join(lines), encoding="utf-8")
        if "status" in d and f and (ROOT / f).is_dir():
            set_readme_status(safe_path(f, ("jobs",)), d["status"], d.get("note", ""))
        return {"ok": True}

    def api_delete(self, d):
        """Move a job to jobs/_trash (recoverable) and remove it from the tracker."""
        rows = track.load()
        i = int(d["idx"])
        r = rows[i]
        folder = (r.get("folder") or "").rstrip("/")
        base = Path(folder).name if folder else (re.sub(r"[^A-Za-z0-9]+", "-", r["company"]).strip("-") or "job")
        dest = trash_dir() / f"{base}__{time.strftime('%Y%m%d-%H%M%S')}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        src = safe_path(folder, ("jobs",)) if folder else None
        if src is not None and "_trash" in src.parts:
            raise PermissionError("already in trash")
        if src is not None and src.is_dir():
            shutil.move(str(src), str(dest))
        else:
            dest.mkdir()
        meta = dict(r)
        meta["_deleted"] = time.strftime("%Y-%m-%d %H:%M")
        (dest / ".row.json").write_text(json.dumps(meta), encoding="utf-8")
        del rows[i]
        track.save(rows)
        return {"trash": dest.name}

    def api_restore(self, d):
        src = trash_entry(d["name"])
        meta = json.loads((src / ".row.json").read_text(encoding="utf-8"))
        folder = (meta.get("folder") or "").rstrip("/")
        (src / ".row.json").unlink()
        if folder:
            dest = safe_path(folder, ("jobs",))
            if dest.exists():
                (src / ".row.json").write_text(json.dumps(meta), encoding="utf-8")
                raise ValueError("A job folder with that name already exists")
            shutil.move(str(src), str(dest))
        else:
            src.rmdir()
        meta.pop("_deleted", None)
        rows = track.load()
        rows.append({k: meta.get(k, "") for k in track.FIELDS})
        track.save(rows)
        return {"ok": True}

    def api_purge(self, d):
        """Permanently delete one trash entry. Only ever inside jobs/_trash."""
        shutil.rmtree(trash_entry(d["name"]))
        return {"ok": True}

    def api_save(self, d):
        p = safe_path(d["path"])
        if p.suffix.lower() not in EDIT_EXT:
            raise PermissionError("file type not editable")
        p.write_text(d["content"], encoding="utf-8")
        return {"ok": True}

    def api_build(self, d):
        folder = safe_path(d["folder"], ("jobs",))
        out, code = run([sys.executable, "scripts/build_cv.py", str(folder)], timeout=240)
        return {"output": out, "ok": code == 0}

    def api_open(self, d):
        p = safe_path(d["path"])
        if p.is_file() and p.suffix.lower() not in OPEN_EXT:
            raise PermissionError("file type not allowed")
        os.startfile(str(p))  # noqa: S606  (local machine, path validated)
        return {"ok": True}

    def api_links(self, d):
        out, code = run([sys.executable, "scripts/check_links.py"], timeout=420)
        return {"output": out, "ok": code == 0}


def main():
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://127.0.0.1:{PORT}"
    print(f"Job Application System dashboard{' (DEMO, read-only)' if DEMO else ''}: {url}  (Ctrl+C to stop)")
    if "--no-open" not in sys.argv and HOST == "127.0.0.1":
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
