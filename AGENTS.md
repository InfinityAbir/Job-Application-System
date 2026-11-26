# AGENTS.md: Job Application System for Abir Hasan

Any AI coding agent (Codex, Cursor, Gemini CLI, Copilot, etc.) working in this folder should read this file first, then the matching file in `workflows/`.

## Purpose
Help Abir Hasan win software jobs in Bangladesh and abroad. He applies to many companies, so the system must be fast and repeatable:
1. **Apply**: he pastes a job description, you produce a tailored CV (PDF), a professional email, and a fit analysis.
2. **Prep**: when he gets an interview call, you research the company and his CV, and produce a preparation guide.
3. **Mock**: you interview him, give feedback.
4. **Follow-up**: follow-up, thank-you, and offer/negotiation messages.
5. **Track**: every application is logged with a follow-up date.

## Map
| Path | What |
|---|---|
| `profile/master_profile.md` | Source of truth about Abir (skills, experience, projects, gaps, preferences) |
| `profile/stories.md` | STAR interview story bank |
| `profile/base_cv.docx` | Word CV template; tailored CVs are edited copies of it |
| `workflows/apply.md` `prep.md` `mock.md` `followup.md` | Step-by-step procedures. Follow them. |
| `scripts/new_job.py` | **Creates the standard job folder** and tracker entry. Always use it. |
| `scripts/build_cv.py` | `03_cv/cv_spec.json` to tailored .docx and .pdf (uses Microsoft Word) |
| `scripts/to_pdf.py` | docx to pdf with page count |
| `scripts/track.py` | Application tracker (`applications.csv`) |
| `scripts/check_links.py` | Wake/check live demo links before interviews |
| `jobs/<date>_<company>_<role>/` | One folder per application, everything for that job lives inside (layout below) |
| `ui/server.py` + `ui/index.html` | Local web dashboard (`python ui/server.py`, http://127.0.0.1:8765): pipeline board, add job, view/edit job files, edit profile. It never calls an AI; it hands Abir ready-made prompts to paste into an agent. |

### Job folder layout (created by `new_job.py`)
```
jobs/2026-11-26_bsd_junior-software-engineer/
  README.md               status card + log (keep updated)
  01_job-description.md   JD verbatim
  02_analysis.md          fit score, gaps, keywords
  03_cv/                  cv_spec.json, Abir_Hasan_CV.docx, Abir_Hasan_CV.pdf  (upload the PDF)
  04_email/               application_email.txt, linkedin_dm.txt, cover_letter.md
  05_prep/                company_research.md, prep.md, mock_<date>.md
  06_followups/           followup_<date>.txt, thank_you.txt, debrief.md, offer_notes.md
```
Never put job files anywhere else; never create ad-hoc folders. The number prefixes follow the application lifecycle.
If a job folder already exists (for example created from the web UI with the JD saved in `01_job-description.md`), reuse it; do not create a second one.

## Routing: what the user says, what you do
- Pastes or links a job description, or says "apply", "tailor my CV": `workflows/apply.md`
- "I got an interview", "prepare me", gives a company/date: `workflows/prep.md`
- "mock interview", "practice", "test me": `workflows/mock.md`
- "follow up", "thank you email", "I got an offer", "rejected": `workflows/followup.md`
- "what's due", "my applications": run `python scripts/track.py due` and `list`, then advise.
- Unsure: ask one short question.

## Hard rules (never break)
1. **No fabrication.** Only use facts in `profile/master_profile.md` or confirmed by Abir in chat. No invented employers, dates, metrics, skills, degrees, certifications. Reword, reorder, select, emphasise: yes. Invent: never.
2. **Be honest about gaps.** If the job needs something he lacks, say so in `analysis.md`, never add it to the CV as a skill. Suggest a truthful framing ("learning", "exposure through X") only if true.
3. **Label publication status exactly** (accepted vs under review).
4. **Never send anything.** Emails and messages are saved as text files for him to review and send. No auto-sending, no form submitting, no logging in for him.
5. **Privacy.** His phone, email, and CV content go only into local files. Do not put them in web searches or third-party tools. Company research queries contain only the company name and public topics.
6. **Check the job is real.** Look for scam signals (asks for money, mismatched domains/phone numbers, no company footprint). Report findings; he decides.
7. **Keep the CV honest and tight**: aim for the same page count as `base_cv.docx` (check `to_pdf.py` output); one idea per bullet; strong verbs; no keyword stuffing of skills he does not have.
8. Ask him for missing facts (e.g., salary range, story details) instead of guessing, and save answers into `profile/`.

## Output language and tone
- CV and emails: professional English, concise, specific, no clichés ("hard-working team player"). If the job post is in Bangla, still write the CV in English unless asked.
- Conversation with Abir: plain, direct, encouraging but honest.

## Environment
- Windows 11, Microsoft Word installed (used for PDF export via COM), Python 3 with `python-docx` and `pywin32`, Node, Pandoc.
- Run scripts from this folder: `python scripts/build_cv.py jobs/<folder>`.

## When you change the system
Keep `AGENTS.md`, `README.md`, and `workflows/` consistent. Workflows are the single source of truth; any agent-specific shortcut (slash commands, rules files) must only point to them, never duplicate them.
