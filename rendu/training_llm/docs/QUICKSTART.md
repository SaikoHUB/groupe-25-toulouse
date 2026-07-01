# ⚡ Quick Start Guide

Guide ultra-rapide pour démarrer en 5 minutes.

## 🚀 Installation (2 minutes)

### Mac Silicon

```bash
cd phi3_medical_chatbot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### NVIDIA GPU

```bash
cd phi3_medical_chatbot
python3 -m venv venv
source venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

## ✅ Vérification (30 secondes)

```bash
python scripts/setup_check.py
```

Doit afficher "✅ ENVIRONNEMENT PRÊT!"

## 🏋️ Entraînement

### Test rapide (recommandé, ~2-3h)

```bash
python scripts/train.py --max-samples 5000 --epochs 1
```

### Entraînement complet (24-48h)

```bash
python scripts/train.py
```

## 🧪 Test

```bash
python scripts/inference.py --model ./medical-phi3-model
```

Posez des questions médicales!

## 📊 Surveillance

```bash
tensorboard --logdir ./output/logs
```

http://localhost:6006

## 💡 Commandes utiles

```bash
# Custom dataset
python scripts/train.py --dataset your/dataset

# Ajuster paramètres
python scripts/train.py --epochs 5 --batch-size 4 --learning-rate 1e-4

# Prompt unique
python scripts/inference.py --prompt "What causes fever?"

# Température élevée (plus créatif)
python scripts/inference.py --temperature 0.9
```

## 🆘 Problèmes?

- Out of Memory: `--batch-size 1 --max-samples 10000`
- Mac lent: C'est normal, essayez `--epochs 1`
- Dataset error: Vérifiez connexion internet

C'est tout! 🎉
