# ============================================================
# push_to_github.ps1
# Run this script ONCE to push the project to GitHub.
# Usage: .\push_to_github.ps1 -RepoUrl "https://github.com/YOUR_USERNAME/YOUR_REPO.git"
# ============================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$RepoUrl,

    [string]$GitName  = "",
    [string]$GitEmail = ""
)

$ErrorActionPreference = "Stop"

# Add Git to PATH
$env:PATH = "C:\Program Files\Git\bin;" + $env:PATH
$env:PATH = "C:\Program Files\Git\cmd;" + $env:PATH

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI News Aggregator — GitHub Push Tool" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check git
try {
    $gitVersion = git --version
    Write-Host "✅ Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git not found. Please install from https://git-scm.com/download/win" -ForegroundColor Red
    exit 1
}

# Set git identity if provided
if ($GitName)  { git config --global user.name  $GitName  }
if ($GitEmail) { git config --global user.email $GitEmail }

$name  = git config user.name
$email = git config user.email

if (-not $name -or -not $email) {
    Write-Host ""
    Write-Host "⚠️  Git user not configured. Please enter your details:" -ForegroundColor Yellow
    $name  = Read-Host "  Your name (e.g. John Doe)"
    $email = Read-Host "  Your email (e.g. john@example.com)"
    git config --global user.name  $name
    git config --global user.email $email
}

Write-Host "👤 Git user: $name <$email>" -ForegroundColor Green
Write-Host ""

# Navigate to project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "📁 Working directory: $(Get-Location)" -ForegroundColor Gray

# Initialize git repo if needed
if (-not (Test-Path ".git")) {
    Write-Host "🔧 Initializing git repository..." -ForegroundColor Yellow
    git init
    git branch -M main
} else {
    Write-Host "✅ Git repository already initialized" -ForegroundColor Green
}

# Ensure .gitignore is correct
Write-Host "📝 Verifying .gitignore..." -ForegroundColor Yellow
$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*.pyo
venv/
.env
faiss_index/
*.egg-info/
dist/
build/

# Node
node_modules/
.next/
.env.local
.env.*.local
npm-debug.log*

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp

# Secrets — never commit these
backend/.env
frontend/.env.local
"@
Set-Content -Path ".gitignore" -Value $gitignoreContent -Encoding UTF8
Write-Host "✅ .gitignore updated" -ForegroundColor Green

# Stage all files
Write-Host ""
Write-Host "📦 Staging files..." -ForegroundColor Yellow
git add .

# Show what will be committed
$status = git status --short
Write-Host ""
Write-Host "Files to commit:" -ForegroundColor Cyan
Write-Host $status
Write-Host ""

# Commit
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
$commitMsg = "feat: AI News Aggregator with RAG + MCP tools ($timestamp)"
git commit -m $commitMsg
Write-Host "✅ Committed: $commitMsg" -ForegroundColor Green

# Add remote
Write-Host ""
Write-Host "🔗 Setting remote origin to: $RepoUrl" -ForegroundColor Yellow
$remotes = git remote
if ($remotes -contains "origin") {
    git remote set-url origin $RepoUrl
} else {
    git remote add origin $RepoUrl
}

# Push
Write-Host ""
Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "   (You may be prompted for GitHub credentials)" -ForegroundColor Gray
Write-Host ""

git push -u origin main

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ Successfully pushed to GitHub!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 View your repo: $($RepoUrl -replace '\.git$', '')" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Go to your GitHub repo" -ForegroundColor White
Write-Host "  2. Add a description: 'AI News Aggregator with RAG + MCP tools'" -ForegroundColor White
Write-Host "  3. Add topics: nextjs fastapi langchain rag mcp openai mongodb" -ForegroundColor White
Write-Host "  4. Deploy frontend to Vercel: https://vercel.com/import" -ForegroundColor White
Write-Host "  5. Deploy backend to Render: https://render.com" -ForegroundColor White
Write-Host ""
