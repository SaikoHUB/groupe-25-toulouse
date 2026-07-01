# 🏗️ Architecture

Guide de l'architecture du code.

## 📦 Structure modulaire

```
phi3_medical_chatbot/
├── config/                 # Configuration centralisée
│   ├── __init__.py
│   └── training_config.py  # Dataclasses pour config
│
├── src/                    # Code source
│   ├── data/              # Gestion des données
│   │   ├── __init__.py
│   │   └── dataset_loader.py
│   │
│   ├── model/             # Gestion du modèle
│   │   ├── __init__.py
│   │   └── model_loader.py
│   │
│   ├── training/          # Logique d'entraînement
│   │   ├── __init__.py
│   │   └── trainer.py
│   │
│   └── utils/             # Utilitaires
│       ├── __init__.py
│       └── device.py
│
├── scripts/               # Scripts exécutables
│   ├── train.py
│   ├── inference.py
│   └── setup_check.py
│
└── docs/                  # Documentation
    ├── QUICKSTART.md
    ├── MAC_SILICON.md
    └── ARCHITECTURE.md
```

## 🎯 Principes de conception

### 1. Séparation des responsabilités

Chaque module a une responsabilité unique:
- **config/**: Configuration uniquement
- **data/**: Chargement et préparation des données
- **model/**: Chargement et configuration du modèle
- **training/**: Logique d'entraînement
- **utils/**: Fonctions utilitaires

### 2. Configuration centralisée

Toutes les configurations sont des dataclasses dans `config/`:

```python
@dataclass
class TrainingConfig:
    output_dir: str = "./output"
    per_device_train_batch_size: int = 2
    # ...
```

Avantages:
- Type hints
- Valeurs par défaut
- Auto-documentation
- Facile à modifier

### 3. Auto-détection du device

Le module `utils/device.py` détecte automatiquement:
- CUDA (NVIDIA GPU)
- MPS (Mac Silicon)
- CPU

Et ajuste la configuration en conséquence.

### 4. Pas de dépendances hard-coded

`bitsandbytes` est optionnel et importé dynamiquement:

```python
try:
    from transformers import BitsAndBytesConfig
    HAS_BITSANDBYTES = True
except ImportError:
    HAS_BITSANDBYTES = False
```

## 🔧 Composants clés

### 1. DataLoader (`src/data/dataset_loader.py`)

```python
loader = MedicalDatasetLoader(
    dataset_name="ruslanmv/ai-medical-chatbot",
    train_split=0.95,
    max_samples=None
)
dataset = loader.load()
```

Responsabilités:
- Télécharger le dataset
- Formater pour Phi-3
- Créer splits train/val
- Filtrer données invalides

### 2. ModelLoader (`src/model/model_loader.py`)

```python
loader = ModelLoader(
    model_id="microsoft/Phi-3.5-mini-instruct",
    lora_r=16,
    lora_alpha=32
)
model, tokenizer = loader.load()
```

Responsabilités:
- Charger modèle et tokenizer
- Appliquer quantification (si disponible)
- Configurer LoRA
- Optimiser pour le device

### 3. Trainer (`src/training/trainer.py`)

```python
trainer = MedicalChatbotTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    config=training_config
)
trainer.train()
```

Responsabilités:
- Ajuster config selon device
- Créer SFTConfig
- Gérer l'entraînement
- Sauvegarder le modèle

## 🔄 Flux d'exécution

### Training Flow

```
1. scripts/train.py
   ↓
2. Charger configs (config/)
   ↓
3. Détecter device (utils/)
   ↓
4. Charger dataset (data/)
   ↓
5. Charger modèle (model/)
   ↓
6. Créer trainer (training/)
   ↓
7. Ajuster config pour device
   ↓
8. Entraîner
   ↓
9. Sauvegarder modèle
```

### Device Detection Flow

```
1. detect_device()
   ↓
2. Check CUDA available? → Yes → "cuda"
   ↓ No
3. Check MPS available? → Yes → "mps"
   ↓ No
4. Return "cpu"
```

### Config Adjustment Flow

```
1. TrainingConfig créé avec valeurs par défaut
   ↓
2. Device détecté
   ↓
3. adjust_for_device(device_type) appelé
   ↓
4. Si MPS:
   - batch_size = 1
   - fp16 = True
   - bf16 = False
   - optimizer = "adamw_torch"
   ↓
5. Config ajusté utilisé pour training
```

## 🧩 Extension

### Ajouter un nouveau dataset

Créer une méthode dans `MedicalDatasetLoader`:

```python
def _load_my_dataset(self) -> Dataset:
    dataset = load_dataset(self.dataset_name)
    # Format selon Phi-3
    dataset = dataset.map(my_format_function)
    return dataset
```

### Ajouter une nouvelle config

Dans `config/training_config.py`:

```python
@dataclass
class MyNewConfig:
    param1: str = "default"
    param2: int = 10
```

### Ajouter un callback

Dans `src/training/trainer.py`:

```python
class MyCallback(TrainerCallback):
    def on_step_end(self, args, state, control, **kwargs):
        # Votre logique
        pass
```

## 🎨 Design Patterns

### 1. Factory Pattern

`ModelLoader` et `DatasetLoader` agissent comme des factories:
- Encapsulent la création d'objets complexes
- Gèrent les variations de configuration
- Masquent la complexité

### 2. Strategy Pattern

Device detection et configuration:
- Différentes stratégies selon device
- Sélection automatique
- Transparent pour l'utilisateur

### 3. Dependency Injection

Les composants reçoivent leurs dépendances:

```python
trainer = MedicalChatbotTrainer(
    model=model,        # Injecté
    tokenizer=tokenizer, # Injecté
    config=config       # Injecté
)
```

## 📝 Bonnes pratiques

### 1. Type Hints partout

```python
def load(self) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
    # ...
```

### 2. Docstrings claires

```python
def format_medical_conversation(example: Dict) -> Dict:
    """
    Format medical conversation for Phi-3.5 training
    
    Args:
        example: Dict with 'Patient' and 'Doctor' keys
    
    Returns:
        Dict with formatted 'text' field
    """
```

### 3. Gestion d'erreurs

```python
try:
    dataset = load_dataset(self.dataset_name)
except Exception as e:
    print(f"❌ Erreur: {e}")
    print("💡 Suggestions...")
    raise
```

### 4. Configuration flexible

Utiliser des dataclasses avec valeurs par défaut:
- Facile à modifier
- Auto-documenté
- Type-safe

## 🧪 Tests

Structure pour tests (à implémenter):

```
tests/
├── test_data_loader.py
├── test_model_loader.py
├── test_device_detection.py
└── test_training.py
```

## 📚 Ressources

- [Python Dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [HuggingFace Transformers](https://huggingface.co/docs/transformers)
- [PEFT Documentation](https://huggingface.co/docs/peft)
