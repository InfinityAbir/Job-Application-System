"""Application tracker (applications.csv).

python scripts/track.py add "Company" "Role" "<job_folder>" [--url URL] [--source SRC]
python scripts/track.py status "Company" interview|rejected|offer|applied|ghosted [--note TEXT]
python scripts/track.py list
python scripts/track.py due          # follow-ups due today or overdue
"""
import csv
import sys
from datetime import date, timedelta
from pathlib import Path

FILE = Path(__file__).resolve().parent.parent / "applications.csv"
FIELDS = ["company", "role", "applied", "status", "follow_up", "url", "source", "folder", "note"]


def load():
    if not FILE.exists():
        return []
    with FILE.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def save(rows):
    with FILE.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def opt(args, flag):
    return args[args.index(flag) + 1] if flag in args else ""


def main(argv):
    if len(argv) < 2:
        return print(__doc__)
    cmd, rows = argv[1], load()
    if cmd == "add":
        today = date.today()
        rows.append({"company": argv[2], "role": argv[3], "applied": today.isoformat(), "status": "applied",
                     "follow_up": (today + timedelta(days=7)).isoformat(), "url": opt(argv, "--url"),
                     "source": opt(argv, "--source"), "folder": argv[4] if len(argv) > 4 and not argv[4].startswith("--") else "", "note": ""})
        save(rows)
        print(f"added {argv[2]} - follow up {rows[-1]['follow_up']}")
    elif cmd == "status":
        hit = [r for r in rows if r["company"].lower() == argv[2].lower()]
        if not hit:
            return print("company not found")
        hit[-1]["status"] = argv[3]
        if opt(argv, "--note"):
            hit[-1]["note"] = opt(argv, "--note")
        if argv[3] in ("rejected", "offer", "ghosted"):
            hit[-1]["follow_up"] = ""
        save(rows)
        print("updated")
    elif cmd == "list":
        for r in rows:
            print(f"{r['applied']}  {r['status']:<10} {r['company']} | {r['role']} | follow-up {r['follow_up'] or '-'}")
        counts = {}
        for r in rows:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        print("totals:", counts or "none")
    elif cmd == "due":
        today = date.today().isoformat()
        due = [r for r in rows if r["follow_up"] and r["follow_up"] <= today and r["status"] in ("applied", "interview")]
        for r in due:
            print(f"DUE {r['follow_up']}  {r['company']} | {r['role']} ({r['status']})")
        if not due:
            print("nothing due")


if __name__ == "__main__":
    main(sys.argv)
