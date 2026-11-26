# Workflow: Apply (job description to tailored CV + email)

Input: a job description (pasted text, screenshot, or URL), optionally the company name, source (LinkedIn, Bdjobs, email), and deadline.

## Steps
0. **If a job folder already exists** (the user added the job in the web UI, or passed a `jobs/...` path), reuse it, read the JD from `01_job-description.md`, and skip to step 2.
1. **Create the job folder with the scaffolder** (never make folders by hand):
   `python scripts/new_job.py "<Company short name>" "<Role>" --url <url> --source <source> --deadline <YYYY-MM-DD>`
   It creates `jobs/<date>_<company>_<role>/` with the standard layout (`README.md`, `01_job-description.md`, `02_analysis.md`, `03_cv/`, `04_email/`, `05_prep/`, `06_followups/`) and logs the tracker entry. Use the brand name (e.g., "BSD"), not the full legal name. The last line it prints is the folder path; use it below. Save the JD verbatim into `01_job-description.md` (below the divider).
2. **Read** `profile/master_profile.md` and `profile/stories.md`.
3. **Legitimacy check** (2 minutes): company website/LinkedIn exists, contact domain matches the company, no upfront fees, salary/role sensible. Note result in `02_analysis.md`. If suspicious, stop and tell Abir before producing documents.
4. **Analyse the JD** and write `02_analysis.md` with:
   - Role summary in 2 lines; seniority; stack; domain.
   - **Must-have vs nice-to-have** requirements.
   - **Match table**: each requirement mapped to evidence in the profile (strong / partial / gap).
   - **Fit score** out of 100 and one-line verdict (apply / apply with effort / skip). Be honest.
   - **Gaps and how to address** (truthful framing, quick-learn plan, what to say in interview).
   - **ATS keywords** from the JD that genuinely apply to him.
   - **Projects to feature** (2 to 4) and which to drop to keep the page count.
   - **Open questions** for Abir (salary expectation, availability) if the application asks.
5. **Write `03_cv/cv_spec.json`** following the schema in the docstring of `scripts/build_cv.py`:
   - `summary`: 3 sentences, mirrors the role's language, leads with strongest matching evidence.
   - `skills`: reorder categories so the JD's stack comes first; only list skills he has.
   - `projects`: pick and order by relevance; reword bullets to emphasise matching tech/outcomes; keep facts unchanged.
   - `experience_bullets.intern`: reorder/reword for relevance.
   - `sections`: drop or keep Publications/Leadership/Mentor depending on relevance (research-heavy or ML roles: keep publications prominent; plain web roles: keep, but they may be shortened).
   - Optional `title_line` matching the role (e.g., ".NET Full-Stack Engineer").
6. **Build**: `python scripts/build_cv.py jobs/<folder>`. Output goes to `03_cv/`. The base CV is 2 pages; keep tailored CVs at 2 pages (the script prints the page count). If longer, trim bullets or projects and rebuild.
7. **Review the PDF visually if possible** (render pages to images, e.g. with `pymupdf`, and look). Verify: no broken layout, no empty headings, links intact, no invented facts. The file to upload is `03_cv/Abir_Hasan_CV.pdf`; if a portal wants a specific name, make a copy named `Abir_Hasan_<Company>.pdf` in the same folder.
8. **Write `04_email/application_email.txt`**: subject line + body, 120 to 170 words:
   - Subject: `Application for <Role> - Abir Hasan`.
   - Greeting to named person if known, else "Dear Hiring Team".
   - Para 1: role + where he found it + one-line positioning.
   - Para 2: two or three specific proofs mapped to their needs (real project/internship facts, one live link).
   - Para 3: honest, brief fit/interest statement about the company's actual work; availability.
   - Close, name, phone, LinkedIn, GitHub. Mention the CV is attached.
   - Also write a 40-word LinkedIn/recruiter DM to `04_email/linkedin_dm.txt`.
   - Add `04_email/cover_letter.md` only if the posting asks for one (formal, specific to the company, under one page).
9. **Update the job `README.md`**: fill Fit score and Next action ("review and send email by <date>"), add a log line. The tracker entry was created by `new_job.py` (follow-up date set to +7 days).
10. **Report to Abir** (short): fit score and verdict, top 3 gaps, files created with paths, the follow-up date, and the reminder that he reviews and sends the email himself.

## Quality bar
- Every bullet traceable to the master profile.
- Summary and top third of page 1 should make the match obvious in 10 seconds.
- Email sounds like a person, not a template; no "I am writing to express my keen interest".
