"""Build a tailored CV from profile/base_cv.docx and a JSON spec, then export PDF via Word.

Usage:
    python scripts/build_cv.py <job_folder>            # reads <job_folder>/03_cv/cv_spec.json, writes CV there
    python scripts/build_cv.py <job_folder> --no-pdf   # docx only

Spec (all keys optional):
{
  "summary": "new professional summary text",
  "title_line": "Software Engineer | Full-Stack & Blockchain Development",
  "skills": {"Languages": "C#, Python", "Web Technologies": "...", ...},   # category -> value
  "skill_order": ["Web Technologies", "Languages", ...],                   # reorder/drop categories
  "experience_bullets": {"intern": ["bullet", ...]},                       # replaces bullets of block
  "projects": [                                                            # order = output order, omitted = dropped
      {"id": "recruitment", "bullets": ["optional override", ...]},
      {"id": "omnichannel"}
  ],
  "sections": {"publications": false, "mentor": false, "leadership": true, "languages": true}
}

Rules: never invent facts. Only reword/reorder/select content that exists in profile/master_profile.md.
"""
import copy
import json
import subprocess
import sys
from pathlib import Path

import docx

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "profile" / "base_cv.docx"

PROJECT_KEYS = {
    "pension": "Blockchain Pension",
    "recruitment": "Recruitment Management System",
    "telemed": "TeleMed",
    "omnichannel": "Omnichannel",
    "blood": "Blood Network",
    "noorup": "NoorUp",
    "jobtracker": "Job Tracker",
}
HEADINGS = ["PROFESSIONAL SUMMARY", "TECHNICAL SKILLS", "EXPERIENCE", "EDUCATION", "MAJOR PROJECTS",
            "PUBLICATIONS", "LEADERSHIP & ACTIVITIES", "LANGUAGES", "REFERENCES"]


def is_bullet(p):
    return p.style.name == "List Paragraph"


def heading_index(paras):
    return {p.text.strip(): i for i, p in enumerate(paras) if p.text.strip() in HEADINGS}


def set_text(p, text):
    """Replace paragraph text, keeping first run formatting."""
    if not p.runs:
        p.add_run(text)
        return
    p.runs[0].text = text
    for r in p.runs[1:]:
        r._r.getparent().remove(r._r)


def remove(p):
    p._p.getparent().remove(p._p)


def set_bullets(block, bullets):
    """block = list of paragraphs. Replace the bullet paragraphs with `bullets`."""
    existing = [p for p in block if is_bullet(p)]
    if not existing:
        return
    for i, text in enumerate(bullets):
        if i < len(existing):
            set_text(existing[i], text)
        else:
            clone = copy.deepcopy(existing[-1]._p)
            existing[-1]._p.addnext(clone)
            new_p = docx.text.paragraph.Paragraph(clone, existing[-1]._parent)
            set_text(new_p, text)
            existing.append(new_p)
    for p in existing[len(bullets):]:
        remove(p)


def split_project_blocks(paras, start, end):
    """Split paragraphs in [start, end) into project blocks keyed by PROJECT_KEYS."""
    blocks, cur_key = {}, None
    for p in paras[start:end]:
        if p.runs and not is_bullet(p):
            key = next((k for k, v in PROJECT_KEYS.items() if p.text.startswith(v)), None)
            if key:
                cur_key = key
                blocks[cur_key] = []
        if cur_key:
            blocks[cur_key].append(p)
    return blocks


def build(job_dir: Path, make_pdf=True):
    cv_dir = job_dir / "03_cv"
    cv_dir.mkdir(exist_ok=True)
    spec = json.loads((cv_dir / "cv_spec.json").read_text(encoding="utf-8"))
    d = docx.Document(str(BASE))
    paras = d.paragraphs
    h = heading_index(paras)

    # --- summary
    if "summary" in spec:
        set_text(paras[h["PROFESSIONAL SUMMARY"] + 1], spec["summary"])

    # --- skills
    s0, s1 = h["TECHNICAL SKILLS"] + 1, h["EXPERIENCE"]
    skill_paras = {p.runs[0].text.rstrip(":").strip(): p for p in paras[s0:s1] if len(p.runs) >= 2}
    for cat, val in spec.get("skills", {}).items():
        if cat in skill_paras:
            skill_paras[cat].runs[1].text = " " + val
    if "skill_order" in spec:
        order = spec["skill_order"]
        anchor = paras[s0 - 1]._p
        for cat in order:
            if cat in skill_paras:
                anchor.addnext(skill_paras[cat]._p)
                anchor = skill_paras[cat]._p
        for cat, p in skill_paras.items():
            if cat not in order:
                remove(p)

    # --- experience bullets
    e0, e1 = h["EXPERIENCE"] + 1, h["EDUCATION"]
    exp = paras[e0:e1]
    intern_block = []
    for p in exp:
        if p.text.startswith("Mentor"):
            break
        intern_block.append(p)
    if "intern" in spec.get("experience_bullets", {}):
        set_bullets(intern_block, spec["experience_bullets"]["intern"])

    # --- projects
    p0, p1 = h["MAJOR PROJECTS"] + 1, h["PUBLICATIONS"]
    blocks = split_project_blocks(paras, p0, p1)
    if "projects" in spec:
        wanted = spec["projects"]
        for item in wanted:
            if item.get("bullets"):
                set_bullets(blocks[item["id"]], item["bullets"])
        keep_ids = [w["id"] for w in wanted]
        anchor = paras[p0 - 1]._p
        for pid in keep_ids:
            for p in blocks[pid]:
                anchor.addnext(p._p)
                anchor = p._p
        for pid, plist in blocks.items():
            if pid not in keep_ids:
                for p in plist:
                    remove(p)

    # --- optional sections
    sec = spec.get("sections", {})
    paras = d.paragraphs
    h = heading_index(paras)
    order = HEADINGS
    def drop_section(name):
        i = h.get(name)
        if i is None:
            return
        nxt = [h[x] for x in order if x in h and h[x] > i]
        j = min(nxt) if nxt else len(paras)
        for p in paras[i:j]:
            remove(p)
    if sec.get("publications") is False:
        drop_section("PUBLICATIONS")
    if sec.get("leadership") is False:
        drop_section("LEADERSHIP & ACTIVITIES")
    if sec.get("languages") is False:
        drop_section("LANGUAGES")
    if sec.get("mentor") is False:
        for i, p in enumerate(d.paragraphs):
            if p.text.startswith("Mentor, Programming"):
                nxt = d.paragraphs[i + 1]
                remove(nxt) if is_bullet(nxt) else None
                remove(p)
                break

    # --- title line (inside the header table)
    if "title_line" in spec:
        for t in d.tables:
            for row in t.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        if "Software Engineer" in p.text and "|" in p.text:
                            set_text(p, spec["title_line"])

    out_docx = cv_dir / "Abir_Hasan_CV.docx"
    d.save(str(out_docx))
    print(f"saved {out_docx}")
    if make_pdf:
        subprocess.run([sys.executable, str(ROOT / "scripts" / "to_pdf.py"), str(out_docx)], check=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    build(Path(sys.argv[1]).resolve(), make_pdf="--no-pdf" not in sys.argv)
