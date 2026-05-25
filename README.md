# J3P Leadership Advisory Assistant (Railway)

Self-contained Flask app — HTML is inlined in `app.py`, no `templates/` folder
needed. This version avoids template-loading issues on deploy.

## Setup

1. Replace the placeholder in `system_prompt.py` with your full system prompt.
2. Push to GitHub, deploy on Railway, set env vars:
   - `ANTHROPIC_API_KEY` = your Anthropic API key
   - `FLASK_SECRET_KEY` = any long random string

## Files

- `app.py` — Flask server with inlined HTML
- `system_prompt.py` — Your system prompt
- `requirements.txt`, `Procfile`, `railway.json`, `runtime.txt` — Deploy config

## Quick deploy

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<user>/<repo>.git
git push -u origin main
```

Then in Railway: New Project → Deploy from GitHub → add env vars → Generate Domain.
