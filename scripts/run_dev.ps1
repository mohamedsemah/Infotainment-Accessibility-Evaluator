# PowerShell script to run development environment on Windows

Write-Host "Starting Infotainment Accessibility Evaluator Development Environment" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found. Copying from env.example..." -ForegroundColor Yellow
    Copy-Item "env.example" ".env"
    Write-Host "Please edit .env and add your API keys before running the development environment." -ForegroundColor Red
    exit 1
}

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found. Please install Python 3.9+ and add it to PATH." -ForegroundColor Red
    exit 1
}

# Check if Node.js is available
try {
    $nodeVersion = node --version 2>&1
    Write-Host "Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Node.js not found. Please install Node.js 18+ and add it to PATH." -ForegroundColor Red
    exit 1
}

# Install backend dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
Set-Location backend
pip install -e .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install backend dependencies." -ForegroundColor Red
    exit 1
}
Set-Location ..

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install frontend dependencies." -ForegroundColor Red
    exit 1
}
Set-Location ..

Write-Host "Starting development servers..." -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop all servers." -ForegroundColor Yellow

# Start backend server
Write-Host "Starting backend server..." -ForegroundColor Yellow
Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" -WorkingDirectory "backend" -WindowStyle Hidden

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend server
Write-Host "Starting frontend server..." -ForegroundColor Yellow
Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory "frontend" -WindowStyle Hidden

Write-Host "Development servers started successfully!" -ForegroundColor Green
Write-Host "You can now access the application at http://localhost:5173" -ForegroundColor Cyan

# Keep script running
Write-Host "Press any key to stop the development servers..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Stop processes
Write-Host "Stopping development servers..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -eq "python" -or $_.ProcessName -eq "node"} | Stop-Process -Force

Write-Host "Development servers stopped." -ForegroundColor Green
