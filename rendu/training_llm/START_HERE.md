# 🎯 START HERE

Bienvenue dans **Phi-3 Medical Chatbot** - Version structurée et professionnelle!

## ✨ Nouveautés de cette version

- 🏗️ **Architecture modulaire** - Code organisé et maintenable
- 🔧 **Configuration centralisée** - Tout dans `config/`
- 🍎 **Support Mac Silicon** - Auto-détection MPS
- ⚡ **Pas de login HuggingFace** - Fonctionne direct
- 📦 **Installation simple** - `pip install -r requirements.txt`
- 🎯 **Scripts CLI** - `python scripts/train.py`

## 🚀 Démarrage en 3 étapes

### 1️⃣ Installation (2 min)

```bash
cd phi3_medical_chatbot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Mac Silicon?** C'est automatique!
**NVIDIA GPU?** Voir `INSTALL.md` pour CUDA.

### 2️⃣ Vérification (30 sec)

```bash
python scripts/setup_check.py
```

Doit afficher "✅ ENVIRONNEMENT PRÊT!"

### 3️⃣ Entraînement

**Test rapide** (recommandé, 2-3h):
```bash
python scripts/train.py --max-samples 5000 --epochs 1
```

**Complet** (24-48h):
```bash
python scripts/train.py
```

## 📁 Structure du projet

```
phi3_medical_chatbot/
├── config/           # ⚙️  Configuration
├── src/             # 📦 Code source
│   ├── data/       # 📊 Chargement données
│   ├── model/      # 🤖 Chargement modèle
│   ├── training/   # 🏋️  Entraînement
│   └── utils/      # 🔧 Utilitaires
├── scripts/         # 🎯 Scripts CLI
│   ├── train.py    # Entraînement
│   ├── inference.py # Test/Chat
│   └── setup_check.py # Vérification
└── docs/           # 📚 Documentation
```

## 📚 Documentation

| Fichier | Description |
|---------|-------------|
| **START_HERE.md** | ⭐ Ce fichier |
| `docs/QUICKSTART.md` | Guide rapide 5 min |
| `docs/MAC_SILICON.md` | Guide Mac M1/M2/M3 |
| `docs/ARCHITECTURE.md` | Architecture code |
| `INSTALL.md` | Installation détaillée |
| `README.md` | Documentation complète |

## 🎓 Exemples d'utilisation

### Entraînement basique

```bash
python scripts/train.py
```

### Entraînement personnalisé

```bash
python scripts/train.py \
  --max-samples 10000 \
  --epochs 5 \
  --batch-size 2 \
  --learning-rate 1e-4 \
  --output ./my-output
```

### Inférence interactive

```bash
python scripts/inference.py --model ./medical-phi3-model
```

### Prompt unique

```bash
python scripts/inference.py \
  --model ./medical-phi3-model \
  --prompt "What are the symptoms of diabetes?"
```

### Export vers Ollama 🦙

```bash
# Export
python scripts/export_to_ollama.py --model ./medical-phi3-model

# Import et utilisation
cd ollama-export
./import_to_ollama.sh
ollama run medical-phi3
```

### TensorBoard

```bash
tensorboard --logdir ./output/logs
```

## 🍎 Mac Silicon?

Lisez **`docs/MAC_SILICON.md`** pour:
- Optimisations spécifiques
- Gestion mémoire
- Durées estimées
- Troubleshooting

## 🐛 Problèmes?

### Out of Memory

```bash
python scripts/train.py --batch-size 1 --max-samples 10000
```

### Dataset non trouvé

Vérifier connexion internet (dataset public, pas de login requis)

### Mac lent

C'est normal sans QLoRA. Essayer:
```bash
python scripts/train.py --max-samples 5000 --epochs 1
```

## 💡 Conseils

1. **Testez d'abord** - 5000 exemples, 1 époque
2. **Surveillez** - TensorBoard pour voir la progression
3. **Sauvegardez** - Modèle sauvegardé automatiquement
4. **Patience** - Mac Silicon plus lent, c'est normal
5. **Documentation** - Lisez les docs/ pour plus d'infos

## 🎯 Workflow complet

```bash
# 1. Vérifier environnement
python scripts/setup_check.py

# 2. Test rapide
python scripts/train.py --max-samples 5000 --epochs 1

# 3. Tester le modèle
python scripts/inference.py --model ./medical-phi3-model

# 4. Si satisfait, entraînement complet
python scripts/train.py

# 5. Surveiller
tensorboard --logdir ./output/logs
```

## ⚠️ Important

Ce chatbot est **éducatif uniquement**:
- ❌ Pas de diagnostics réels
- ❌ Pas de remplacement médical
- ✅ Consulter un professionnel

## 🆘 Besoin d'aide?

1. Lire `docs/QUICKSTART.md`
2. Lire `README.md`
3. Vérifier les erreurs dans Terminal
4. Mac Silicon: `docs/MAC_SILICON.md`

## ✅ Checklist

- [ ] Installation terminée
- [ ] `setup_check.py` ✅
- [ ] GPU/MPS détecté
- [ ] Test rapide réussi
- [ ] TensorBoard fonctionne
- [ ] Documentation lue

## 🎉 Prêt!

Vous êtes prêt à entraîner votre chatbot médical!

```bash
python scripts/train.py
```

Bon entraînement! 🚀🏥
