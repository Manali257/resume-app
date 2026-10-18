# Resume Tailor – Manali Jiwane

A Streamlit app for JD matching, tailored resume generation, and job tracking.

## Files

| File | Purpose |
|------|---------|
| `app.py` | Main app |
| `requirements.txt` | Dependencies |
| `tracker.json` | Job applications (auto-created) |

## Before deploying – privacy

Open `app.py` and replace these placeholders with real values:

```
[your-email@example.com]
[your-phone]
[your-id]          ← LinkedIn profile ID
[Current Company]
[University], [Year]
```

Or leave them blank for a public demo and fill in manually each session.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at http://localhost:8501

## Deploy to Streamlit Community Cloud (free)

1. Push this folder to a **public or private** GitHub repo.
2. Go to https://share.streamlit.io → New app.
3. Point to `resume_app/app.py` (or `app.py` if repo root).
4. Click Deploy.

The app gets a public URL like `https://your-app.streamlit.app`.

## Features (v1)

- **JD Matcher** – paste any JD, get a skill match % and project suggestions
- **Generate Resume** – tailored plain-text resume, download as `.txt`
- **Job Tracker** – log applications with status, location, notes
