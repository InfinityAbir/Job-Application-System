# Workflow: Prep (interview invitation to preparation guide)

Input: company name (and website), role, interview date/time/place, any details from the invitation (format, interviewers, what to bring). If a job folder exists in `jobs/`, reuse its `01_job-description.md`, `02_analysis.md`, `03_cv/` (the CV that was actually sent), and `04_email/`.

## Steps
1. **Locate or create the job folder.** Look in `jobs/` (match by company). If none exists, create it: `python scripts/new_job.py "<Company>" "<Role>" --source "<source>"`. Read `01_job-description.md` and `02_analysis.md` if filled; if missing, ask Abir to paste the JD (or work from the role title). Update status: `python scripts/track.py status "<Company>" interview --note "<date, time, place>"` and the folder `README.md` (Status, Next action).
2. **Verify the invitation** quickly: sender domain matches the company site; phone number and address match official sources. If anything differs (it has happened), tell him to confirm via the official number.
3. **Research the company** (public info only; no personal data in queries). Sources: company website (home, about, case studies, careers), LinkedIn page, news, Facebook page, Bdjobs/Clutch listings, GitHub. Treat aggregator figures (employee counts, revenue) as unreliable and say so. Capture:
   - What they do, products, key clients, industries, size, founding year, leadership.
   - Tech stack (website, job posts, GitHub).
   - Recent news, projects, culture signals, how they work (agile, sprints).
   - Likely interview style for a company this size.
4. **Re-read his CV and profile as an interviewer would.** List every claim a sharp interviewer could probe, with the depth needed (architecture, trade-offs, what he personally did). Pull from `profile/stories.md`; ask him for missing story details and save them there.
5. **Map JD to him**: strengths to lead with; gaps with a prepared honest answer (e.g., stack mismatch).
6. **Save the research** to `05_prep/company_research.md` (facts with source URLs, unreliable figures flagged), then **write `05_prep/prep.md`** with these sections:
   1. Logistics (date, place, route tips, what to bring, verification note)
   2. Company brief (one page) and "why this company" talking points
   3. 60-second pitch tailored to this company
   4. CV deep-dive: probable questions per project/experience with answer outlines
   5. Technical question bank drawn from the JD stack (fundamentals + stack-specific + 5 to 8 live-coding or SQL tasks with solutions or hints)
   6. Gap questions and honest answers
   7. Business/scenario questions relevant to what the company sells
   8. Behavioural questions mapped to his STAR stories
   9. Salary: research market range for the role in Dhaka, his floor/target/stretch, and how to answer if asked early (use `profile/master_profile.md` preferences; ask if TODO)
   10. Smart questions to ask them (4 to 6)
   11. Hour-by-hour or day-by-day plan until the interview, using the real time left
   12. Day-of checklist and what to do in the last 30 minutes
7. **Run `python scripts/check_links.py`** if demos will be shown; report any failing links.
8. **Offer a mock interview** (`workflows/mock.md`) and a thank-you email afterwards (`workflows/followup.md`).
9. **Report to Abir**: the 5 most important things, the file path, and time left.

## Quality bar
- Specific to this company and this CV; no generic advice filler.
- Every technical answer outline must be correct; flag uncertainty instead of guessing.
- Keep it scannable: headings, short bullets, checklists.
