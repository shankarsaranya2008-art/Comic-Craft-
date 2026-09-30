# ComicCraft


## Local testing without Gemini

This corrected build includes a real local AI provider switch.

`.env` defaults to:

```env
AI_PROVIDER=mock
IMAGE_PROVIDER=placeholder
```

In this mode ComicCraft does not call Gemini or Hugging Face. It generates a deterministic five-panel story and placeholder artwork so the complete UI, routes, layout, and PDF workflow can be tested.

Start on Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

When Google Gemini access is restored, change:

```env
AI_PROVIDER=gemini
```

and provide `GEMINI_API_KEY`.

Do not commit `.env` or API keys.
