# 📦 Installation Guide

Guide d'installation détaillé pour tous les systèmes.

## 🍎 Mac Silicon (M1/M2/M3)

### Installation automatique

```bash
cd phi3_medical_chatbot
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Vérification

```bash
python scripts/setup_check.py
```

Devrait afficher:
```
✅ Apple Silicon (MPS) disponible
✅ Device: Mac M1/M2/M3 GPU
```

## 🖥️ Linux/Windows avec NVIDIA GPU

### Prérequis

- NVIDIA GPU avec 8GB+ VRAM
- CUDA 11.8+ ou 12.1+
- Drivers NVIDIA récents

### Installation

```bash
cd phi3_medical_chatbot
python3 -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate

# Installer PyTorch avec CUDA 12.1
pip install torch --index-url https://download.pytorch.org/whl/cu121

# Ou CUDA 11.8
# pip install torch --index-url https://download.pytorch.org/whl/cu118

# Installer dépendances
pip install -r requirements.txt

# Installer bitsandbytes pour QLoRA
pip install bitsandbytes
```

### Vérification

```bash
python scripts/setup_check.py
```

Devrait afficher:
```
✅ CUDA disponible
✅ GPU: [Votre GPU]
✅ VRAM: XX GB
```

## 🐧 Linux sans GPU

```bash
cd phi3_medical_chatbot
python3 -m venv venv
source venv/bin/activate
pip install torch
pip install -r requirements.txt
```

⚠️ **Warning**: Entraînement TRÈS lent sur CPU.

## 🪟 Windows sans GPU

```bash
cd phi3_medical_chatbot
python -m venv venv
venv\Scripts\activate
pip install torch
pip install -r requirements.txt
```

## 🐳 Docker (Optionnel)

### Avec NVIDIA GPU

```dockerfile
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y python3 python3-pip
WORKDIR /app
COPY requirements.txt .
RUN pip3 install torch --index-url https://download.pytorch.org/whl/cu121
RUN pip3 install -r requirements.txt
COPY . .

CMD ["python3", "scripts/train.py"]
```

Build et run:
```bash
docker build -t phi3-medical .
docker run --gpus all -v $(pwd)/output:/app/output phi3-medical
```

## 📦 Installation via pip (Optionnel)

```bash
# Installation en mode développement
pip install -e .

# Utiliser les commandes
medical-train --help
medical-inference --help
medical-check
```

## 🔧 Dépendances détaillées

### Obligatoires

- `torch>=2.1.0` - PyTorch
- `transformers>=4.36.0` - Transformers
- `peft>=0.7.0` - PEFT/LoRA
- `datasets>=2.16.0` - Datasets
- `trl>=0.7.10` - TRL
- `accelerate>=0.25.0` - Accelerate
- `scipy>=1.11.0` - Scipy
- `tensorboard>=2.15.0` - TensorBoard
- `huggingface-hub>=0.20.0` - HF Hub
- `sentencepiece>=0.1.99` - Tokenizer

### Optionnelles

- `bitsandbytes>=0.41.0` - QLoRA (CUDA uniquement)

## 🐛 Problèmes courants

### PyTorch ne détecte pas CUDA

```bash
# Vérifier installation
python -c "import torch; print(torch.cuda.is_available())"

# Si False, réinstaller
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### bitsandbytes ne compile pas

Sur Mac:
```bash
# Normal, ne pas installer bitsandbytes sur Mac
```

Sur Windows:
```bash
# Utiliser version pre-built
pip install bitsandbytes-windows
```

### Transformers trop ancien

```bash
pip install --upgrade transformers
```

### Out of Memory pendant installation

```bash
# Augmenter swap ou fermer applications
# Ou installer package par package
pip install torch
pip install transformers
# etc.
```

## ✅ Test de l'installation

```bash
# Vérifier tout
python scripts/setup_check.py

# Test rapide du modèle
python -c "
from src.utils.device import print_device_info
print_device_info()
"

# Test import
python -c "
from config import TrainingConfig
from src.data import MedicalDatasetLoader
from src.model import ModelLoader
print('✅ Tous les imports fonctionnent')
"
```

## 🎓 Python version

Minimum: Python 3.9
Recommandé: Python 3.10 ou 3.11

Vérifier:
```bash
python --version
```

Si trop ancien:
- Mac: `brew install python@3.11`
- Ubuntu: `sudo apt install python3.11`
- Windows: Télécharger depuis python.org

## 🚀 Prêt!

Une fois l'installation terminée:

```bash
# Vérifier
python scripts/setup_check.py

# Tester
python scripts/train.py --max-samples 100 --epochs 1

# Go!
python scripts/train.py
```
