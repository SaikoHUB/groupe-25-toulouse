# 🏥 Phi-3 Medical Chatbot

Fine-tuning Microsoft Phi-3.5-mini-instruct pour créer un chatbot médical intelligent avec 257k conversations réelles patient-docteur.

## ✨ Fonctionnalités

- ✅ **Pas de login HuggingFace** requis pour le dataset public
- ✅ **Support Mac Silicon** (M1/M2/M3) avec MPS
- ✅ **Auto-détection GPU** (CUDA/MPS/CPU)
- ✅ **QLoRA 4-bit** sur NVIDIA GPU
- ✅ **Dataset médical** 257k conversations pré-configuré
- ✅ **Architecture modulaire** et professionnelle
- ✅ **Configuration flexible** avec dataclasses

## 📁 Structure du Projet

```
phi3_medical_chatbot/
├── config/                 # Configuration
│   ├── __init__.py
│   └── training_config.py  # TrainingConfig, ModelConfig, DataConfig
├── src/                    # Code source
│   ├── data/              # Chargement des données
│   ├── model/             # Chargement du modèle
│   ├── training/          # Logique d'entraînement
│   └── utils/             # Utilitaires (device detection, etc.)
├── scripts/               # Scripts exécutables
│   ├── train.py          # Entraînement principal
│   ├── inference.py      # Inférence/chat
│   └── setup_check.py    # Vérification environnement
├── docs/                  # Documentation
├── requirements.txt       # Dépendances
└── README.md             # Ce fichier
```

## 🚀 Quick Start

### 1. Installation

```bash
# Créer environnement virtuel
python3 -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows

# Installer PyTorch
# Pour NVIDIA GPU:
pip install torch --index-url https://download.pytorch.org/whl/cu121

# Pour Mac Silicon (automatique):
pip install torch

# Installer dépendances
pip install -r requirements.txt
```

### 2. Vérifier l'environnement

```bash
python scripts/setup_check.py
```

### 3. Entraînement

```bash
# Entraînement complet (257k exemples)
python scripts/train.py

# Test rapide (5000 exemples, 1 époque)
python scripts/train.py --max-samples 5000 --epochs 1

# Custom dataset
python scripts/train.py --dataset your/dataset --output ./my-output
```

### 4. Inférence

```bash
# Mode interactif
python scripts/inference.py --model ./medical-phi3-model

# Prompt unique
python scripts/inference.py --model ./medical-phi3-model --prompt "What are the symptoms of diabetes?"
```

## 💻 Configuration Matérielle

### NVIDIA GPU (Recommandé)
- **GPU**: 8GB+ VRAM (RTX 3060+)
- **Avantages**: QLoRA 4-bit, entraînement rapide
- **Temps**: ~24-30h (RTX 3060, 3 époques)

### Mac Silicon (M1/M2/M3)
- **RAM**: 16GB+ recommandé (32GB idéal)
- **Limitations**: Pas de QLoRA 4-bit, plus lent
- **Temps**: ~36-48h (M1, 3 époques)
- **Doc**: Voir `docs/MAC_SILICON.md`

### CPU
- Non recommandé (très lent)
- Uniquement pour tests

## 📊 Dataset

**ruslanmv/ai-medical-chatbot**
- 257,000 conversations patient-docteur
- Questions médicales réelles
- Réponses professionnelles
- Téléchargement automatique (142 MB)
- Pas de login requis

## ⚙️ Configuration

Toutes les configurations sont dans `config/training_config.py`:

```python
# Ajuster ces paramètres selon votre GPU
TrainingConfig(
    per_device_train_batch_size=2,  # 1 pour Mac/GPU limité
    num_train_epochs=3,              # 1 pour test
    learning_rate=2e-4,
    # ... autres paramètres
)
```

Les configurations s'ajustent automatiquement selon le device détecté.

## 🎯 Exemples d'utilisation

### Entraînement personnalisé

```python
from config import TrainingConfig, ModelConfig, DataConfig
from src.data import MedicalDatasetLoader
from src.model import ModelLoader
from src.training import MedicalChatbotTrainer

# Configuration
model_config = ModelConfig(lora_r=32)  # Augmenter rank
data_config = DataConfig(max_samples=10000)  # Limiter dataset
training_config = TrainingConfig(num_train_epochs=1)

# Charger dataset
loader = MedicalDatasetLoader(**data_config.__dict__)
dataset = loader.load()

# Charger modèle
model_loader = ModelLoader(**model_config.__dict__)
model, tokenizer = model_loader.load()

# Entraîner
trainer = MedicalChatbotTrainer(
    model, tokenizer, dataset["train"], dataset["validation"], training_config
)
trainer.train()
```

### Inférence programmatique

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer
import torch

model = AutoPeftModelForCausalLM.from_pretrained("./medical-phi3-model")
tokenizer = AutoTokenizer.from_pretrained("./medical-phi3-model")

prompt = "I have a persistent cough. What should I do?"
inputs = tokenizer(f"<|user|>\n{prompt}<|end|>\n<|assistant|>\n", return_tensors="pt")

outputs = model.generate(**inputs, max_new_tokens=256)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)
```

## 🦙 Export vers Ollama

Vous pouvez exporter votre modèle vers Ollama pour une utilisation locale simple:

```bash
# Export du modèle
python scripts/export_to_ollama.py --model ./medical-phi3-model

# Import dans Ollama
cd ollama-export
./import_to_ollama.sh

# Utilisation
ollama run medical-phi3
```

Voir `docs/OLLAMA_EXPORT.md` pour le guide complet.

## 📈 Surveillance

### TensorBoard

```bash
tensorboard --logdir ./output/logs
```

Ouvrir http://localhost:6006

### Métriques

- Training loss
- Validation loss
- Learning rate
- Gradient norm

## 🐛 Troubleshooting

### Out of Memory

```bash
# Réduire batch size et sequence length
python scripts/train.py --batch-size 1 --max-samples 10000
```

Ou éditer `config/training_config.py`:
```python
per_device_train_batch_size = 1
max_seq_length = 512
gradient_accumulation_steps = 16
```

### Dataset non trouvé

Le dataset est public et ne nécessite pas de login. Si erreur:
- Vérifier connexion internet
- Vérifier nom du dataset
- Essayer avec un VPN si CDN lent

### Mac Silicon lent

C'est normal sans quantification 4-bit. Pour accélérer:
- Réduire `--max-samples`
- Utiliser `--epochs 1`
- Augmenter RAM disponible

## ⚠️ Disclaimer Médical

Ce chatbot est à des fins **éducatives uniquement**:

- ❌ NE PAS utiliser pour diagnostics réels
- ❌ NE PAS remplacer consultation médicale
- ❌ NE PAS suivre ses conseils sans avis médical
- ✅ TOUJOURS consulter un professionnel de santé

## 📚 Documentation

- `docs/QUICKSTART.md` - Guide de démarrage rapide
- `docs/MAC_SILICON.md` - Guide Mac Silicon
- `docs/ARCHITECTURE.md` - Architecture du code
- `docs/OLLAMA_EXPORT.md` - Export vers Ollama 🦙

## 🤝 Contribution

Contributions bienvenues! Ouvrir une issue ou PR.

## 📄 Licence

MIT License

## 🔗 Ressources

- [Dataset](https://huggingface.co/datasets/ruslanmv/ai-medical-chatbot)
- [Phi-3.5](https://huggingface.co/microsoft/Phi-3.5-mini-instruct)
- [PEFT/LoRA](https://huggingface.co/docs/peft)
- [TRL](https://huggingface.co/docs/trl)
