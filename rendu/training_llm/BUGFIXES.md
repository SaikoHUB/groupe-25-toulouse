# 🐛 Bug Fixes & Updates

## Version 1.0.3 (2026-07-01)

### Fixed: TypeError sur SFTTrainer - API TRL 0.7+ complète

**Problèmes:**
```
TypeError: __init__() got an unexpected keyword argument 'tokenizer'
TypeError: __init__() got an unexpected keyword argument 'dataset_text_field'
TypeError: __init__() got an unexpected keyword argument 'max_seq_length'
```

**Cause:**
L'API de `SFTTrainer` dans TRL 0.7+ a complètement changé:
- Ancien: paramètres dans `SFTTrainer.__init__()`
- Nouveau: paramètres dans `SFTConfig`, API minimale pour `SFTTrainer`

**Solution:**
- `tokenizer` → `processing_class` dans SFTTrainer
- `dataset_text_field` → supprimé (détection auto)
- `max_seq_length` → retiré complètement, configuré via `tokenizer.model_max_length`
- API minimale pour SFTTrainer: model, args, datasets, processing_class
- Callbacks ajoutés via `.add_callback()`
- Max sequence length géré par le tokenizer directement

**Fichiers modifiés:**
- `src/training/trainer.py`

**Commit:** e5b7c2d

---

## Version 1.0.2 (2026-07-01)

### Fixed: TypeError sur SFTConfig max_seq_length

**Problème:**
```
TypeError: __init__() got an unexpected keyword argument 'max_seq_length'
```

**Cause:**
`max_seq_length` était passé à `SFTConfig.__init__()` mais ce paramètre doit être passé directement au `SFTTrainer`, pas au `SFTConfig`.

**Solution:**
- Retiré `max_seq_length` de `SFTConfig()`
- Ajouté `max_seq_length` comme paramètre du `SFTTrainer()`

**Fichiers modifiés:**
- `src/training/trainer.py`

**Commit:** b9e4f7a

---

## Version 1.0.1 (2026-07-01)

### Fixed: AttributeError sur max_seq_length

**Problème:**
```
AttributeError: 'TrainingConfig' object has no attribute 'max_seq_length'
```

**Cause:**
Le paramètre `max_seq_length` était défini dans `DataConfig` mais utilisé dans `TrainingConfig`.

**Solution:**
- Déplacé `max_seq_length` de `DataConfig` vers `TrainingConfig`
- Ajusté automatiquement dans `adjust_for_device()`:
  - MPS (Mac Silicon): 1024
  - CPU: 512
  - CUDA: 2048 (défaut)

**Fichiers modifiés:**
- `config/training_config.py`

**Commit:** a7f8c3d

---

## Changelog

### [1.0.4] - 2026-07-01

#### Fixed
- fp16 ValueError sur Mac Silicon (MPS)
- Accelerate ne reconnaît pas MPS comme GPU pour fp16

#### Changed
- Mac Silicon utilise maintenant full precision (fp32) pour training
- Modèle reste en fp16 pour économie mémoire
- Config: `fp16=False, bf16=False` pour MPS

### [1.0.3] - 2026-07-01

#### Fixed
- SFTTrainer API compatibility complète avec TRL 0.7+
- `tokenizer` remplacé par `processing_class`
- `dataset_text_field` supprimé (détection auto)
- `max_seq_length` retiré de SFTConfig (non supporté)
- Ordre des paramètres corrigé

#### Changed
- API SFTTrainer entièrement mise à jour pour TRL 0.7+
- Dataset text field détecté automatiquement
- `max_seq_length` configuré via `tokenizer.model_max_length`
- Callbacks ajoutés via `add_callback()`

### [1.0.2] - 2026-07-01

#### Fixed
- `max_seq_length` TypeError avec SFTConfig
- Paramètre passé correctement au SFTTrainer

#### Changed
- `max_seq_length` passé à `SFTTrainer()` au lieu de `SFTConfig()`

### [1.0.1] - 2026-07-01

#### Fixed
- `max_seq_length` AttributeError lors de l'entraînement
- Configuration correcte pour Mac Silicon

#### Changed
- `max_seq_length` maintenant dans `TrainingConfig` au lieu de `DataConfig`

---

### [1.0.0] - 2026-07-01

#### Added
- Architecture modulaire complète
- Support Mac Silicon (MPS)
- Export vers Ollama
- Configuration centralisée avec dataclasses
- Documentation complète
- Scripts CLI (train, inference, export)
- Auto-détection GPU/CPU
- Pas de login HuggingFace requis

#### Features
- Dataset médical 257k conversations
- QLoRA 4-bit (CUDA)
- LoRA complet (Mac/CPU)
- TensorBoard integration
- Multiple documentation files

---

## Known Issues

Aucun problème connu actuellement.

## Reporting Bugs

Si vous trouvez un bug:
1. Vérifier `BUGFIXES.md` pour voir s'il est déjà corrigé
2. Vérifier la documentation
3. Ouvrir une issue avec:
   - Message d'erreur complet
   - Commande exécutée
   - Environnement (OS, Python version, GPU)
   - Logs pertinents

## Testing

Pour vérifier que tout fonctionne:

```bash
# Vérifier configuration
python scripts/setup_check.py

# Test rapide
python scripts/train.py --max-samples 100 --epochs 1

# Si succès, tout fonctionne!
```
