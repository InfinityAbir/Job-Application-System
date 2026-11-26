# profile/

Your private data lives here. Everything except the `*.example.*` files and this README is git-ignored.

| File | What | Tracked in git |
|---|---|---|
| `master_profile.md` | Source of truth about you (copy from `master_profile.example.md`) | no |
| `stories.md` | STAR interview stories (copy from `stories.example.md`) | no |
| `links.txt` | Live demo links to wake before interviews (copy from `links.example.txt`) | no |
| `base_cv.docx` | Your Word CV, used as the template for every tailored CV | no |

## Requirements for `base_cv.docx`

`scripts/build_cv.py` edits a copy of this document, so it must be structured like this:

- Section headings as their own paragraphs, exactly: `PROFESSIONAL SUMMARY`, `TECHNICAL SKILLS`, `EXPERIENCE`, `EDUCATION`, `MAJOR PROJECTS`, `PUBLICATIONS`, `LEADERSHIP & ACTIVITIES`, `LANGUAGES`, `REFERENCES`
- Summary: one paragraph under its heading
- Skills: one paragraph per category, a bold label then the values (`Languages: C#, Python`)
- Projects: a header paragraph starting with the project name, bullet paragraphs (List Paragraph style), then an optional links paragraph
- Project names are mapped to ids in `PROJECT_KEYS` at the top of `scripts/build_cv.py`. Edit that map to match your own projects.

Use any layout, fonts and photo you like; formatting, links and images are preserved because the script only changes text and reorders or removes whole blocks.
