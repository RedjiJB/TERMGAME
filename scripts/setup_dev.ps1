# Development environment setup script for Windows

Write-Host "Setting up TermGame development environment..." -ForegroundColor Green

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.(1[2-9]|[2-9]\d)") {
    Write-Host "Python version OK: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "ERROR: Python 3.12+ required. Found: $pythonVersion" -ForegroundColor Red
    exit 1
}

# Install uv if not present
Write-Host "Checking for uv package manager..." -ForegroundColor Yellow
if (!(Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Installing uv..." -ForegroundColor Yellow
    irm https://astral.sh/uv/install.ps1 | iex
} else {
    Write-Host "uv already installed" -ForegroundColor Green
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
uv pip install -e ".[dev]"

# Install pre-commit hooks
Write-Host "Installing pre-commit hooks..." -ForegroundColor Yellow
pre-commit install

# Create necessary directories
Write-Host "Creating project directories..." -ForegroundColor Yellow
$dirs = @(
    "scenarios/linux",
    "scenarios/ios",
    "scenarios/powershell",
    "logs",
    "data"
)
foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created: $dir" -ForegroundColor Green
    }
}

Write-Host "`nSetup complete! Run 'pytest' to verify installation." -ForegroundColor Green
