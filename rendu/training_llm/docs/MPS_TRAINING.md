# 🍎 Mac Silicon (MPS) Training Notes

Notes spécifiques pour l'entraînement sur Mac Silicon.

## ⚠️ Limitations MPS

### 1. Precision mixte non supportée

**Problème:**
```
ValueError: fp16 mixed precision requires a GPU (not 'mps').
```

**Cause:**
Accelerate (bibliothèque sous-jacente) ne reconnaît pas MPS comme "vrai GPU" et refuse fp16/bf16.

**Solution:**
- Utiliser **full precision** (fp32) pour le training
- Le modèle reste en fp16 pour économie mémoire
- Configuration automatique: `fp16=False, bf16=False`

### 2. Impact sur performance

| Aspect | fp16 (CUDA) | fp32 (MPS) |
|--------|-------------|------------|
| **Vitesse** | Rapide | Plus lent (~30%) |
| **Mémoire** | Économe | Plus gourmand |
| **Précision** | Suffisante | Meilleure |

### 3. Recommandations RAM

Avec full precision:
- **Minimum**: 16GB RAM
- **Recommandé**: 32GB RAM
- **Idéal**: 64GB RAM

## ✅ Optimisations automatiques

Sur Mac Silicon, le système ajuste automatiquement:

```python
# Config Mac Silicon
batch_size = 1              # Petit batch
gradient_accumulation = 8   # Compense petit batch
max_seq_length = 1024      # Séquences plus courtes
fp16 = False               # Full precision
bf16 = False               # Pas de mixed precision
optimizer = "adamw_torch"  # Optimizer compatible
```

## 💡 Si Out of Memory

### Option 1: Réduire la taille du modèle

```bash
# Encore moins d'exemples
python scripts/train.py --max-samples 1000
```

### Option 2: Réduire batch/sequence

Dans `config/training_config.py`:
```python
# Pour Mac avec 16GB RAM
if device_type == "mps":
    self.per_device_train_batch_size = 1
    self.gradient_accumulation_steps = 16  # au lieu de 8
    self.max_seq_length = 512              # au lieu de 1024
```

### Option 3: Utiliser swap/mémoire virtuelle

macOS gère automatiquement, mais:
- Ralentit encore plus l'entraînement
- Peut user le SSD
- Mieux vaut réduire les paramètres

## 📊 Monitoring

### Activity Monitor

Surveillez:
- **GPU**: Utilisation Metal/MPS
- **Mémoire**: Ne doit pas atteindre 100%
- **Swap**: Doit rester bas (< 1GB)
- **CPU**: Peut être élevé, c'est normal

### Si mémoire pleine

Signes:
- Entraînement très lent
- Swap élevé (> 5GB)
- Ventilateurs à fond
- Système qui lag

**Action**: Tuer l'entraînement (Ctrl+C) et réduire paramètres

## ⚡ Vitesse attendue

Avec full precision sur Mac:

| Mac | RAM | Exemples/sec | Temps (5k, 1 epoch) |
|-----|-----|-------------|---------------------|
| M1 8-core | 16GB | ~0.3-0.5 | ~3-4h |
| M1 Pro | 16GB | ~0.4-0.6 | ~2.5-3h |
| M1 Max | 32GB | ~0.5-0.7 | ~2-2.5h |
| M2 | 16GB | ~0.4-0.6 | ~2.5-3h |
| M2 Max | 32GB | ~0.6-0.8 | ~1.5-2h |
| M3 Max | 36GB | ~0.7-1.0 | ~1.5-2h |

## 🔥 Gestion chaleur

Full precision = plus de chaleur:
- Ventilateurs plus actifs
- Mac plus chaud
- Utiliser sur surface dure
- Bien ventilé

## 🎯 Recommandations finales

### Pour 16GB RAM
```bash
python scripts/train.py --max-samples 5000 --epochs 1
```

### Pour 32GB+ RAM
```bash
python scripts/train.py --max-samples 10000 --epochs 1
```

### Pour production
- Envisager cloud avec GPU NVIDIA (plus rapide)
- Ou laisser tourner Mac plusieurs jours
- Ou utiliser dataset plus petit

## ✅ Avantages Mac Silicon quand même

- ✅ Développement local
- ✅ Pas de coût cloud
- ✅ Privacy (données locales)
- ✅ Pas de login requis
- ✅ Silencieux (comparé aux GPU bruyants)

## 🐛 Troubleshooting

### Erreur: "MPS backend out of memory"

```python
# Réduire davantage
batch_size = 1
max_seq_length = 256
gradient_accumulation = 32
```

### Erreur: "No space left on device"

- Vider le cache: `~/.cache/huggingface/`
- Libérer espace disque
- Besoin de 20GB+ libre

### Training très lent après X steps

Normal avec swap. Options:
1. Continuer (lent mais fonctionne)
2. Réduire paramètres
3. Redémarrer Mac et réessayer

## 📚 Ressources

- [Apple ML Documentation](https://developer.apple.com/metal/)
- [PyTorch MPS](https://pytorch.org/docs/stable/notes/mps.html)
- [Accelerate Issues](https://github.com/huggingface/accelerate/issues)
