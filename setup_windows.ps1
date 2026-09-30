$ErrorActionPreference = "Stop"

Write-Host "ComicCraft setup"
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

Write-Host ""
Write-Host "Setup complete."
Write-Host "Current mode: AI_PROVIDER=mock, IMAGE_PROVIDER=placeholder"
Write-Host ""
Write-Host "Start with:"
Write-Host ".\.venv\Scripts\python.exe -m uvicorn app.main:app --reload"
