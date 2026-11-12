# LAB03S03 - Inicializador Windows. PowerShell na raiz do projeto:
# powershell -ExecutionPolicy Bypass -File .\iniciar_windows.ps1
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    py -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Nao foi possivel criar o ambiente Python. Verifique a instalacao do Python.' }
}
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Falha na instalacao das dependencias.' }
Write-Host 'Para preparar contas ficticias: .\.venv\Scripts\python.exe -m scripts.preparar_demo' -ForegroundColor Yellow
Write-Host 'Acesse http://127.0.0.1:8000 (API: /docs).' -ForegroundColor Green
& '.\.venv\Scripts\python.exe' run.py
