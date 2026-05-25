# J3P Leadership Advisory Assistant

A web-based chatbot powered by Claude (Anthropic API), deployable to Railway.

## Local development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your API key:
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   ```

3. Add your system prompt to `system_prompt.py` (replace the placeholder).

4. Run:
   ```bash
   python app.py
   ```

5. Open http://localhost:8080

## Deploy to Railway

### 1. Push to GitHub

```bash
cd j3p-railway
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

### 2. Deploy on Railway

1. Go to https://railway.app and sign in.
2. Click **New Project** → **Deploy from GitHub repo** → pick your repo.
3. Railway will auto-detect Python and start building.
4. In the project's **Variables** tab, add:
   - `ANTHROPIC_API_KEY` = your Anthropic API key
   - `FLASK_SECRET_KEY` = any long random string (e.g. `openssl rand -hex 32`)
5. Under **Settings** → **Networking**, click **Generate Domain** to get a public URL.

That's it. Visit the generated URL and start chatting.

## File overview

| File | Purpose |
|---|---|
| `app.py` | Flask web server with `/chat`, `/reset`, `/health` endpoints |
| `system_prompt.py` | Holds the J3P system prompt (paste yours here) |
| `templates/index.html` | Chat UI |
| `requirements.txt` | Python dependencies |
| `Procfile` | Start command (gunicorn) |
| `railway.json` | Railway build/deploy config |
| `runtime.txt` | Python version pin |

## Notes

- The system prompt is cached via `cache_control: {"type": "ephemeral"}` to reduce per-request cost.
- Conversation history is stored in the Flask session (cookie-based, per-browser).
- Click **New conversation** in the header to reset history.
- Model: `claude-sonnet-4-6` — change in `app.py` if needed.
