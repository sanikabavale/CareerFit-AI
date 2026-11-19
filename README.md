# CareerFit AI
**AI-Powered Resume Analysis & Job Recommendation System**  
*Discover Your Skills. Find Your Fit.*

## Features in this starter build
- Account registration with admin approval; pending users cannot log in.
- Secure password hashing using PBKDF2-HMAC-SHA256.
- Admin bootstrap script and basic user approval panel.
- PDF/DOCX resume text extraction.
- Keyword skill extraction, TF-IDF/cosine similarity and role ranking.
- Skill gap view, simple learning checklist, candidate profile preview.
- SQLite analysis history and downloadable PDF report.
- Analytics chart and local mock-interview question bank.

## Requirements
- Python 3.10–3.12 recommended.
- Internet is required once to install Python packages. The app itself does not require a paid AI API.

## Windows setup (PowerShell)
```powershell
cd CareerFit_AI
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts\create_admin.py
streamlit run app.py
```
If `py -3.11` is unavailable, use `python -m venv .venv` with an installed supported Python version.

## First login
1. Run `python scripts\create_admin.py` once to create the first administrator.
2. Log in with that admin account.
3. Create a normal account using the Create account tab.
4. Open Admin Panel and approve the pending account.
5. The user can now log in.

## Data and privacy
The SQLite database is created at `runtime/careerfit_ai.db`. It contains account and analysis data. Keep the `runtime` folder private and do not upload it to a public Git repository. Do not upload resumes containing information you do not want processed.

## Current limitations
- This is a runnable MVP foundation, not a production-certified hiring system.
- Scanned/image-only PDFs need OCR; this build reports when selectable text is missing.
- Career Assistant is a rule-based placeholder and does not call an LLM.
- Mock interview currently uses a small local question bank.
- Roadmap checkboxes are session UI state in this initial build; persistent roadmap progress is a planned extension.
- Admin panel includes basic approval and system counts; advanced job/skill administration and audit views are planned extensions.
- Match percentages are estimates, not hiring probabilities.
- Validate locally with your own sample documents and Python environment before submission.
