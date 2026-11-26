# Workflow: Follow-up, thank-you, offers, rejections

Run `python scripts/track.py due` or `list` first when the request is vague. Never send; save drafts as text in `jobs/<folder>/06_followups/` (`followup_YYYY-MM-DD.txt`, `thank_you.txt`, `debrief.md`, `offer_notes.md`). After each action, add a dated line to the job folder's `README.md` log and update its Status/Next action.

## A. Follow-up after applying (no reply, 5 to 7 days)
- 60 to 90 words. Reference the role and date applied, restate one concrete reason he fits, ask about status politely, attach nothing new. Optional shorter LinkedIn version.
- Then set the next follow-up (+7 days) once; after two follow-ups mark `ghosted` with `track.py status`.

## B. Thank-you after an interview (same day)
- Ask Abir what was discussed (topics, interviewer names, anything he stumbled on). 90 to 130 words.
- Thank them, reference one specific topic from the conversation, address any weak answer briefly with a better one-line answer, restate interest, ask about next steps.
- Record the interview in `jobs/<folder>/06_followups/debrief.md`: questions asked, how he answered, what to improve. Feed repeated question types into `profile/stories.md`.

## C. Offer
- Do NOT advise accepting or rejecting for him on financial grounds beyond general information; lay out the factors.
- Help him compare: salary, bonus, probation terms, notice, working hours, tech stack, learning, mentor, company stability, commute, bond/contract clauses (flag service bonds and unusual clauses).
- Draft a polite negotiation or clarification email if he wants: thank, express enthusiasm, ask for specific terms with a reasoned range from market research. Update tracker to `offer`.
- Reminder: verify the offer letter is from the real company before any payment or document sharing. Real employers never ask candidates for money.

## D. Rejection / no
- Draft a short gracious reply asking for brief feedback and to keep his CV for future roles. Update tracker to `rejected`. Add a lesson line in `debrief.md`.

## E. Weekly review (on request)
- Summarise tracker counts, response rate, which job types respond, which keywords/skills appear most in JDs he saw (from `jobs/*/02_analysis.md`), and recommend what to learn or change next.
