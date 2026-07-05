Write-Host "=== OASIS SYSTEM CORE — Local Launcher ===" -ForegroundColor Cyan

# Enable local SQLite database fallback mode
$env:USE_SQLITE="true"

# Start App-Tier Backend in a new window
Write-Host "Starting App-Tier Backend on http://127.0.0.1:8080..." -ForegroundColor Green
Start-Process -FilePath "app-tier/.venv/Scripts/python.exe" -ArgumentList "-m uvicorn src.main:app --host 127.0.0.1 --port 8080 --reload" -WorkingDirectory "app-tier" -WindowStyle Normal

# Start Mock Server in a new window
Write-Host "Starting Mock Server on http://127.0.0.1:8000..." -ForegroundColor Green
Start-Process -FilePath "app-tier/.venv/Scripts/python.exe" -ArgumentList "mock-server/server.py" -WorkingDirectory "." -WindowStyle Normal

Write-Host "`nLaunch complete!" -ForegroundColor Cyan
Write-Host "--------------------------------------------------------" -ForegroundColor Gray
Write-Host "Access the Event Dashboard at: http://127.0.0.1:8000/dashboard.html" -ForegroundColor Yellow
Write-Host "Access the Main Landing Page at: http://127.0.0.1:8000/index.html" -ForegroundColor Yellow
Write-Host "--------------------------------------------------------" -ForegroundColor Gray
Write-Host "Close the spawned terminal windows to stop the servers." -ForegroundColor Gray
