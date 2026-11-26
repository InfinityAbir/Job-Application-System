"""Create the standard folder for one job application and log it in the tracker.

python scripts/new_job.py "Company" "Role" [--url URL] [--source SRC] [--deadline YYYY-MM-DD] [--date YYYY-MM-DD] [--no-track]

Creates jobs/<date>_<company>_<role>/ :
    README.md               one-page status card for this application
    01_job-description.md   the JD, verbatim
    02_analysis.md          fit score, gaps, keywords, projects to feature
    03_cv/                  cv_spec.json, Abir_Hasan_CV.docx, Abir_Hasan_CV.pdf
    04_email/               application_email.txt, linkedin_dm.txt, cover_letter.md (if requested)
    05_prep/                prep.md, company_research.md, mock_<date>.md
    06_followups/           followup_*.txt, thank_you.txt, debrief.md, offer_notes.md
Prints the folder path (last line) so agents can use it.
"""
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUBDIRS = ["03_cv", "04_email", "05_prep", "06_followups"]


def slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:40].strip("-") or "unknown"


def opt(args, flag, default=""):
    return args[args.index(flag) + 1] if flag in args else default


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    company, role = argv[1], argv[2]
    url, source = opt(argv, "--url"), opt(argv, "--source")
    deadline, when = opt(argv, "--deadline"), opt(argv, "--date", date.today().isoformat())
    folder = ROOT / "jobs" / f"{when}_{slug(company)}_{slug(role)}"
    if folder.exists():
        print(f"exists: {folder}")
        print(folder)
        return
    folder.mkdir(parents=True)
    for s in SUBDIRS:
        (folder / s).mkdir()

    (folder / "01_job-description.md").write_text(
        f"# Job description: {role} at {company}\n\nSource: {source or 'n/a'}\nURL: {url or 'n/a'}\nDeadline: {deadline or 'n/a'}\n\n---\n\n(paste the job description verbatim below)\n",
        encoding="utf-8")
    (folder / "02_analysis.md").write_text(
        f"# Fit analysis: {role} at {company}\n\n(to be filled by the /apply workflow)\n", encoding="utf-8")
    (folder / "README.md").write_text(
        f"""# {company}: {role}

| Field | Value |
|---|---|
| Status | applied |
| Created | {when} |
| Deadline | {deadline or 'n/a'} |
| Source | {source or 'n/a'} |
| Job URL | {url or 'n/a'} |
| Fit score | TBD |
| Next action | TBD |

## Contents
- `01_job-description.md`: the job post, verbatim
- `02_analysis.md`: fit score, gaps, ATS keywords, projects to feature
- `03_cv/`: tailored CV (`Abir_Hasan_CV.pdf` is the file to upload) and `cv_spec.json`
- `04_email/`: application email, LinkedIn message, cover letter
- `05_prep/`: interview preparation guide, company research, mock interviews
- `06_followups/`: follow-ups, thank-you, debrief, offer notes

## Log
- {when}: folder created
""", encoding="utf-8")

    if "--no-track" not in argv:
        cmd = [sys.executable, str(ROOT / "scripts" / "track.py"), "add", company, role, str(folder.relative_to(ROOT)).replace("\\", "/")]
        if url:
            cmd += ["--url", url]
        if source:
            cmd += ["--source", source]
        subprocess.run(cmd, check=True)
    print(folder)


if __name__ == "__main__":
    main(sys.argv)
