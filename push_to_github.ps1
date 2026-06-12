# push_to_github.ps1
# Execute este script na pasta do projeto para subir tudo ao GitHub.
# Pre-requisito: git instalado e autenticacao GitHub configurada (PAT ou SSH).

$repo   = "https://github.com/admbrazil/Projeto-SaaS.git"
$branch = "main"

Write-Host "=== Inicializando repositório local ===" -ForegroundColor Cyan
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

if (-not (Test-Path ".git")) {
    git init
    Write-Host "Repositório git inicializado." -ForegroundColor Green
} else {
    Write-Host "Repositório git ja existe." -ForegroundColor Yellow
}

git remote remove origin 2>$null
git remote add origin $repo
Write-Host "Remote configurado: $repo" -ForegroundColor Green

New-Item -ItemType Directory -Force -Path "logs"  | Out-Null
New-Item -ItemType File      -Force -Path "logs/.gitkeep" | Out-Null
New-Item -ItemType Directory -Force -Path "media" | Out-Null
New-Item -ItemType File      -Force -Path "media/.gitkeep" | Out-Null

git add -A
Write-Host "Arquivos adicionados ao stage." -ForegroundColor Green

$commitMsg = "feat: reimplementacao Django com melhorias LGPD"
git commit -m $commitMsg
Write-Host "Commit criado." -ForegroundColor Green

Write-Host "=== Enviando para GitHub ===" -ForegroundColor Cyan
git push -u origin $branch

if ($LASTEXITCODE -eq 0) {
    Write-Host "Push concluido com sucesso!" -ForegroundColor Green
} else {
    Write-Host "Falha no push. Verifique autenticacao GitHub." -ForegroundColor Red
}
