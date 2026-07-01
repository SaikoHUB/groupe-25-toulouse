$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$ModelName = "phi35-financial"
$Modelfile = Join-Path $PSScriptRoot "..\..\ollama_server\Modelfile"

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "[X] Ollama introuvable. Installe-le : https://ollama.com/download" -ForegroundColor Red
    exit 1
}

Write-Host "[1/3] Pull du modele de base phi3.5..." -ForegroundColor Cyan
ollama pull phi3.5

Write-Host "[2/3] Build du modele $ModelName depuis le Modelfile..." -ForegroundColor Cyan
ollama create $ModelName -f $Modelfile

Write-Host "[3/3] Verification de l'API Ollama (http://localhost:11434)..." -ForegroundColor Cyan
try {
    $tags = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
    if ($tags.models.name | Where-Object { $_ -like "$ModelName*" }) {
        Write-Host "[OK] Modele $ModelName pret. Serveur d'inference operationnel." -ForegroundColor Green
    } else {
        Write-Host "[!] Modele cree mais non liste, verifie avec 'ollama list'." -ForegroundColor Yellow
    }
} catch {
    Write-Host "[!] Ollama ne repond pas sur 11434. Ouvre un autre terminal et lance 'ollama serve'." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=> Front (DEV WEB) : Serveur = http://localhost:11434  |  Modele = $ModelName" -ForegroundColor Green
