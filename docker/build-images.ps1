# Build TermGame Docker images
# Run this script to build custom images with all tools pre-installed

Write-Host "Building TermGame Ubuntu Full Image..." -ForegroundColor Cyan

# Build the Ubuntu full image
docker build -f Dockerfile.ubuntu-full -t termgame/ubuntu-full:latest .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Successfully built termgame/ubuntu-full:latest" -ForegroundColor Green
    Write-Host ""
    Write-Host "Image includes:" -ForegroundColor Yellow
    Write-Host "  • Man pages and documentation"
    Write-Host "  • Common utilities (vim, nano, tree, git)"
    Write-Host "  • Network tools (ping, curl, wget)"
    Write-Host "  • Python 3"
    Write-Host "  • Build tools (gcc, make)"
    Write-Host ""
    Write-Host "Use this image in scenarios by setting:" -ForegroundColor Cyan
    Write-Host '  image: "termgame/ubuntu-full:latest"'
} else {
    Write-Host "✗ Build failed" -ForegroundColor Red
    exit 1
}
