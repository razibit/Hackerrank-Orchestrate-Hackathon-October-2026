param(
    [string]$RepoPath = '.\hackerrank-orchestrate-october26'
)
$ErrorActionPreference = 'Stop'
$Kit = $PSScriptRoot
if (-not (Test-Path $RepoPath)) {
    Write-Host 'Cloning official HackerRank repository...'
    git clone https://github.com/interviewstreet/hackerrank-orchestrate-october26.git $RepoPath
}
$Repo = (Resolve-Path $RepoPath).Path
if (-not (Test-Path (Join-Path $Repo 'problem_statement.md'))) {
    throw "Not an official Orchestrate repository: $Repo"
}
New-Item -ItemType Directory -Force -Path (Join-Path $Repo 'code\tools') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Repo 'code\tests') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Repo 'code\evaluation') | Out-Null
Copy-Item -Path (Join-Path $Kit 'code\tools\*.py') -Destination (Join-Path $Repo 'code\tools') -Force
Copy-Item -Path (Join-Path $Kit 'code\tests\*.py') -Destination (Join-Path $Repo 'code\tests') -Force
Copy-Item -Path (Join-Path $Kit 'code\__init__.py') -Destination (Join-Path $Repo 'code\__init__.py') -Force
Copy-Item -Path (Join-Path $Kit 'code\evaluation\*.md') -Destination (Join-Path $Repo 'code\evaluation') -Force
Copy-Item -Path (Join-Path $Kit 'PROMPT_FOR_CODEX.md') -Destination (Join-Path $Repo 'code\PROMPT_FOR_CODEX.md') -Force
Copy-Item -Path (Join-Path $Kit 'ENGINEERING_PLAN.md') -Destination (Join-Path $Repo 'code\ENGINEERING_PLAN.md') -Force
Copy-Item -Path (Join-Path $Kit 'requirements.txt') -Destination (Join-Path $Repo 'requirements.txt') -Force
Write-Host 'Installed starter tools; left organizer AGENTS.md, README.md, problem_statement.md and dataset untouched.'
Write-Host "Project: $Repo"
Write-Host 'Next: cd into project, create .venv, run inspect_dataset.py, then launch Codex at project root.'
