# 🦙 Export vers Ollama

Guide complet pour exporter votre modèle Phi-3 fine-tuné vers Ollama.

## 🎯 Qu'est-ce qu'Ollama?

**Ollama** est un outil qui permet d'exécuter des modèles de langage localement, de manière simple et efficace. C'est comme Docker pour les LLMs!

Avantages:
- ✅ Exécution locale (pas besoin d'internet)
- ✅ Interface simple (CLI et API)
- ✅ Optimisé pour performance
- ✅ Support GPU et CPU
- ✅ Compatible Mac Silicon

## 📋 Prérequis

### 1. Modèle entraîné

Vous devez d'abord avoir entraîné votre modèle:
```bash
python scripts/train.py
```

Cela créera `./medical-phi3-model/` avec vos poids LoRA.

### 2. Ollama installé

Télécharger depuis: https://ollama.ai/download

Installation:
- **Mac**: `.dmg` à installer
- **Linux**: `curl https://ollama.ai/install.sh | sh`
- **Windows**: `.exe` à installer

Vérifier:
```bash
ollama --version
```

## 🚀 Export en 3 étapes

### Étape 1: Fusionner les poids LoRA

```bash
python scripts/export_to_ollama.py --model ./medical-phi3-model
```

Ce script:
1. Charge votre modèle LoRA
2. Fusionne les poids avec le modèle de base
3. Sauvegarde le modèle complet
4. Crée un `Modelfile` pour Ollama
5. Crée un script d'import

**Durée**: 2-5 minutes

### Étape 2: Importer dans Ollama

```bash
cd ollama-export
./import_to_ollama.sh
```

Ou manuellement:
```bash
ollama create medical-phi3 -f ollama-export/Modelfile
```

### Étape 3: Utiliser le modèle

```bash
ollama run medical-phi3
```

## 💬 Utilisation

### Mode interactif

```bash
ollama run medical-phi3
```

Puis posez vos questions:
```
>>> What are the symptoms of diabetes?
>>> I have a persistent cough. Should I be worried?
>>> quit
```

### Prompt unique

```bash
ollama run medical-phi3 "What causes high blood pressure?"
```

### Via API

```python
import requests

response = requests.post('http://localhost:11434/api/generate', 
    json={
        'model': 'medical-phi3',
        'prompt': 'What are the symptoms of diabetes?'
    }
)
```

### Intégration dans une app

```python
import ollama

response = ollama.chat(model='medical-phi3', messages=[
    {
        'role': 'user',
        'content': 'What causes fever?',
    },
])
print(response['message']['content'])
```

## ⚙️ Options avancées

### Export avec nom personnalisé

```bash
python scripts/export_to_ollama.py \
  --model ./medical-phi3-model \
  --name my-medical-bot \
  --output ./my-export
```

### Modifier le Modelfile

Éditez `ollama-export/Modelfile`:

```dockerfile
# Température (créativité)
PARAMETER temperature 0.8  # Plus haut = plus créatif

# Longueur de réponse
PARAMETER num_ctx 4096  # Contexte plus long

# Stop tokens personnalisés
PARAMETER stop "END"

# System prompt personnalisé
SYSTEM "Your custom instructions..."
```

Puis recréer le modèle:
```bash
ollama create medical-phi3 -f ollama-export/Modelfile
```

## 📊 Taille du modèle

Après fusion, le modèle complet fait environ:
- **Phi-3.5-mini**: ~7-8 GB
- **Quantifié (optionnel)**: ~4-5 GB

Ollama peut quantifier automatiquement pour réduire la taille.

## 🔧 Commandes Ollama utiles

### Lister les modèles

```bash
ollama list
```

### Supprimer un modèle

```bash
ollama rm medical-phi3
```

### Voir les détails

```bash
ollama show medical-phi3
```

### Copier un modèle

```bash
ollama cp medical-phi3 medical-phi3-backup
```

### Mettre à jour

```bash
ollama pull medical-phi3
```

## 🚦 Performance

### GPU vs CPU

Ollama utilise automatiquement:
- **NVIDIA GPU** (CUDA)
- **Mac Silicon** (Metal)
- **CPU** (fallback)

### Vitesse attendue

| Matériel | Tokens/seconde |
|----------|----------------|
| RTX 4090 | ~150-200 |
| RTX 3060 | ~50-80 |
| Mac M1 Max | ~40-60 |
| Mac M1 | ~20-30 |
| CPU (i7) | ~5-10 |

## 🔄 Workflow complet

```bash
# 1. Entraîner le modèle
python scripts/train.py

# 2. Exporter vers Ollama
python scripts/export_to_ollama.py --model ./medical-phi3-model

# 3. Importer dans Ollama
cd ollama-export
./import_to_ollama.sh

# 4. Tester
ollama run medical-phi3

# 5. (Optionnel) Serveur API
ollama serve

# 6. Utiliser via API
curl http://localhost:11434/api/generate -d '{
  "model": "medical-phi3",
  "prompt": "What causes fever?"
}'
```

## 🌐 Déploiement

### Serveur API local

```bash
# Démarrer serveur
ollama serve

# Accessible sur http://localhost:11434
```

### Docker

```dockerfile
FROM ollama/ollama

COPY ollama-export/Modelfile /modelfile
RUN ollama create medical-phi3 -f /modelfile

CMD ["serve"]
```

### Cloud

Vous pouvez déployer Ollama sur:
- VPS (OVH, Hetzner, etc.)
- AWS EC2
- Google Cloud
- Azure

## 💡 Conseils

### 1. Optimiser la vitesse

```bash
# Activer GPU
export OLLAMA_GPU=1

# Augmenter threads CPU
export OLLAMA_NUM_THREAD=8
```

### 2. Limiter la mémoire

```bash
# Limiter à 8GB
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_MAX_QUEUE=1
```

### 3. Personnaliser les réponses

Modifiez le `SYSTEM` prompt dans le Modelfile pour:
- Changer le ton
- Ajouter des contraintes
- Spécialiser le domaine
- Ajouter un disclaimer

## 🐛 Troubleshooting

### Ollama ne démarre pas

```bash
# Vérifier le service
ollama list

# Redémarrer
killall ollama
ollama serve
```

### Modèle trop grand

```bash
# Quantifier en 4-bit
ollama create medical-phi3:q4_0 -f Modelfile
```

### Réponses lentes

- Vérifier GPU utilisé: `ollama ps`
- Réduire `num_ctx` dans Modelfile
- Fermer autres applications

### Import échoue

```bash
# Vérifier le Modelfile
cat ollama-export/Modelfile

# Recréer manuellement
ollama create medical-phi3 -f ollama-export/Modelfile
```

## 🔗 Intégration

### Avec Python

```bash
pip install ollama
```

```python
import ollama

response = ollama.chat(
    model='medical-phi3',
    messages=[{'role': 'user', 'content': 'Hello!'}]
)
```

### Avec JavaScript

```bash
npm install ollama
```

```javascript
import ollama from 'ollama'

const response = await ollama.chat({
  model: 'medical-phi3',
  messages: [{ role: 'user', content: 'Hello!' }],
})
```

### Avec cURL

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "medical-phi3",
  "messages": [
    {"role": "user", "content": "What causes fever?"}
  ]
}'
```

## ⚠️ Important

### Disclaimer médical

Toujours inclure un disclaimer:

```
⚠️ Ce chatbot est à usage éducatif uniquement.
Consultez toujours un professionnel de santé qualifié
pour des conseils médicaux, diagnostics ou traitements.
```

Ajoutez-le dans le `SYSTEM` prompt du Modelfile.

## 📚 Ressources

- [Ollama Documentation](https://ollama.ai/docs)
- [Ollama GitHub](https://github.com/ollama/ollama)
- [Modelfile Reference](https://github.com/ollama/ollama/blob/main/docs/modelfile.md)
- [API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)

## ✅ Checklist

- [ ] Modèle entraîné
- [ ] Ollama installé
- [ ] Export réussi
- [ ] Import dans Ollama
- [ ] Test de base réussi
- [ ] Disclaimer ajouté
- [ ] Performance acceptable

## 🎉 Succès!

Votre modèle médical est maintenant disponible localement via Ollama!

```bash
ollama run medical-phi3 "What are the symptoms of diabetes?"
```

Bon chatting! 🦙🏥
