#!/usr/bin/env bash
set -euo pipefail

MODEL_NAME="phi35-financial"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODELFILE="$SCRIPT_DIR/../../ollama_server/Modelfile"

if ! command -v ollama >/dev/null 2>&1; then
  echo "[X] Ollama introuvable. Installe-le : https://ollama.com/download"
  exit 1
fi

echo "[1/3] Pull du modele de base phi3.5..."
ollama pull phi3.5

echo "[2/3] Build du modele $MODEL_NAME depuis le Modelfile..."
ollama create "$MODEL_NAME" -f "$MODELFILE"

echo "[3/3] Verification de l'API Ollama (http://localhost:11434)..."
if curl -s --max-time 5 http://localhost:11434/api/tags | grep -q "$MODEL_NAME"; then
  echo "[OK] Modele $MODEL_NAME pret. Serveur d'inference operationnel."
else
  echo "[!] Ollama ne repond pas sur 11434 ou modele non liste. Lance 'ollama serve' si besoin."
fi

echo ""
echo "=> Front (DEV WEB) : Serveur = http://localhost:11434  |  Modele = $MODEL_NAME"
