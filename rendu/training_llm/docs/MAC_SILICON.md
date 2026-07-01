# 🍎 Mac Silicon Guide

Guide complet pour entraîner sur Mac M1/M2/M3.

## ✅ Supporté

- Apple M1, M1 Pro, M1 Max
- Apple M2, M2 Pro, M2 Max
- Apple M3, M3 Pro, M3 Max
- MPS (Metal Performance Shaders)
- LoRA complet
- Pas de login HuggingFace

## ❌ Limitations

- Pas de quantification 4-bit (bitsandbytes)
- Pas de bfloat16 (utilise fp16)
- Plus de RAM nécessaire
- Entraînement plus lent

## 💻 Configuration recommandée

- **RAM**: 16GB minimum, 32GB idéal
- **Espace**: 20GB libre
- **macOS**: 12.3+ (Monterey+)

## ⚡ Installation

```bash
cd phi3_medical_chatbot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

MPS est automatiquement détecté par PyTorch.

## 🏋️ Entraînement

### Configuration automatique

Le script détecte Mac Silicon et ajuste:
- Batch size: 1
- Sequence length: 1024
- Optimizer: adamw_torch
- Precision: fp16
- Gradient accumulation: 8

### Test rapide (2-3h)

```bash
python scripts/train.py --max-samples 5000 --epochs 1
```

### Entraînement complet (36-48h)

```bash
python scripts/train.py
```

## ⏱️ Durée estimée

| Mac | RAM | Temps (3 époques) |
|-----|-----|-------------------|
| M1 8-core | 16GB | ~36-48h |
| M1 Pro | 16GB | ~30-36h |
| M1 Max | 32GB | ~24-30h |
| M2 | 16GB | ~30-36h |
| M2 Max | 32GB | ~18-24h |
| M3 Max | 36GB | ~15-21h |

## 💾 Gestion mémoire

### Si Out of Memory

Éditer `config/training_config.py`:

```python
# Réduire ces valeurs
per_device_train_batch_size = 1  # déjà à 1
gradient_accumulation_steps = 16  # augmenter de 8
max_seq_length = 512  # réduire de 1024
```

Ou limiter le dataset:
```bash
python scripts/train.py --max-samples 10000
```

### Vérifier utilisation RAM

Moniteur d'activité > Onglet Mémoire

## 🌡️ Gestion chaleur

### Recommandations:
- Utiliser sur surface plane
- Ne pas bloquer ventilation
- Entraîner la nuit (plus frais)
- Fermer autres applications
- Brancher sur secteur

### Si surchauffe:
- Réduire batch size
- Réduire sequence length
- Faire des pauses entre époques

## 🔧 Optimisations

### Avec 32GB+ RAM

```python
# Dans config/training_config.py
per_device_train_batch_size = 2  # au lieu de 1
max_seq_length = 1536  # au lieu de 1024
gradient_accumulation_steps = 4  # au lieu de 8
```

### Mode économie

```python
per_device_train_batch_size = 1
max_seq_length = 256
gradient_accumulation_steps = 32
num_train_epochs = 1  # Test uniquement
```

## 📊 Comparaison GPU

| Feature | Mac M1 Max | RTX 3060 | RTX 4090 |
|---------|------------|----------|----------|
| Quantification | ❌ | ✅ 4-bit | ✅ 4-bit |
| bfloat16 | ❌ | ✅ | ✅ |
| Vitesse | 1.0x | 1.5x | 4x |
| Consommation | 50W | 170W | 450W |
| Bruit | Silencieux | Moyen | Fort |

## 💡 Conseils

1. **Testez d'abord**: 5000 exemples, 1 époque
2. **La nuit**: Lancez entraînement long la nuit
3. **Surveillez**: Moniteur d'activité ouvert
4. **Alimentation**: Toujours branché
5. **Patience**: C'est plus lent, c'est normal

## 🆘 Troubleshooting

### MPS non détecté

```bash
python3 -c "import torch; print(torch.backends.mps.is_available())"
```

Si False:
- macOS 12.3+ requis
- Réinstaller PyTorch

### Crash mémoire

```bash
# Réduire drastiquement
python scripts/train.py --max-samples 5000 --epochs 1
```

### Lent

- Fermer toutes les apps
- Redémarrer le Mac
- Vérifier Activity Monitor (GPU usage)

Bon entraînement sur votre Mac! 🍎🚀
