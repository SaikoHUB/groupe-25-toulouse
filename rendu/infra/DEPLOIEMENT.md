# Documentation de deploiement — INFRA

Projet : assistant financier **Phi-3.5-Financial** (TechCorp Industries).
Filiere : INFRA — deploiement du serveur d'inference.

---

## 1. Choix technique : Ollama

Trois options etaient proposees : Ollama, Triton Inference Server, ou serveur maison (FastAPI / vLLM / llama.cpp).

**Retenu : Ollama.**

| Critere                     | Ollama                          | Triton                              | Serveur maison            |
|-----------------------------|---------------------------------|-------------------------------------|---------------------------|
| Mise en place               | Une commande (`ollama create`)  | Backend Python a ecrire + config    | Tout a coder              |
| Quantization                | Q4 par defaut, automatique      | Manuelle                            | Manuelle                  |
| API                         | REST prete (`/api/chat`)        | REST/gRPC a exposer                 | A implementer             |
| Adapte a un hackathon 7h    | Oui                             | Overkill                            | Chronophage               |
| GPU non requis              | Oui (CPU ok pour la demo)       | Oriente GPU                         | Variable                  |

Triton est pertinent pour de la prod haute charge avec GPU, mais son cout de configuration n'est pas justifie sur le perimetre et le temps imparti. Ollama couvre exactement le besoin : exposer le modele via une API REST consommee par le front.

## 2. Construction du modele

Le modele `phi35-financial` est construit depuis `ollama_server/Modelfile` :

- **Base** : `phi3.5` (Phi-3.5-mini-instruct de Microsoft, tire du registre officiel Ollama).
- **System prompt** : specialise l'assistant sur la finance/investissement/budget/trading (herite de l'equipe precedente, verifie).
- **Parametres d'inference** ajoutes :

| Parametre        | Valeur | Justification                                                        |
|------------------|--------|----------------------------------------------------------------------|
| `temperature`    | 0.3    | Reponses factuelles et stables, adaptees au contexte financier.      |
| `top_p`          | 0.9    | Nucleus sampling, ecarte la longue traine improbable.                |
| `top_k`          | 40     | Limite le choix aux 40 tokens les plus probables.                    |
| `num_predict`    | 512    | Longueur de reponse raisonnable (aligne sur le config Triton herite).|
| `num_ctx`        | 4096   | Contexte suffisant pour l'historique de conversation du front.       |
| `repeat_penalty` | 1.1    | Limite les repetitions sur les reponses longues.                     |

## 3. Deploiement : Docker (principal) + natif (fallback)

Deux modes sont fournis, decrits dans le README.

### Docker (recommande) — portabilite maximale
Un `docker-compose.yml` monte deux services :
- `techcorp-ollama` : le serveur d'inference (image officielle `ollama/ollama`), port 11434, volume persistant pour les modeles.
- `techcorp-model-init` : attend le serveur, `pull phi3.5`, `create phi35-financial` depuis le Modelfile monte en lecture seule, puis s'arrete.

Interet : le correcteur n'installe que Docker Desktop. Aucune installation d'Ollama, aucune commande manuelle, le modele est construit automatiquement au premier `docker compose up`. L'environnement est identique quelle que soit la machine.

### Natif (fallback) — sans Docker
Scripts `setup-model.ps1` (Windows) et `setup-model.sh` (Linux/macOS) : verifient Ollama, pull la base, buildent le modele custom, verifient l'API. Utile si Docker n'est pas disponible.

## 4. Quantization

Le modele `phi3.5` distribue par Ollama est deja quantise en **Q4_0** (~2.2 Go), ce qui permet de tourner sur CPU ou petit GPU sans perte notable de qualite sur ce cas d'usage.
Une variante Q8 existe (`phi3.5:3.8b-mini-instruct-q8_0`) si plus de VRAM est disponible. Q4 est retenu par defaut pour la portabilite.

## 5. Performances

Sur machine de test equipee d'un GPU NVIDIA (CUDA), Ollama bascule automatiquement l'inference sur le GPU (detecte au demarrage : `inference compute ... library=CUDA`). Un script `benchmark.py` mesure la latence et le debit (tokens/sec) sur un jeu de questions finance et genere `BENCHMARK.md`. Voir ce rapport pour les chiffres mesures.

## 6. Accessibilite

- **Mode correction (par defaut)** : deploiement 100 % local. Serveur d'inference (`:11434`) et front (`:5173`) sur la meme machine. Aucune dependance a une infra distante, aucun point de defaillance reseau.
- **Mode reseau (optionnel)** : le port 11434 est expose sur toutes les interfaces (publie par Docker, ou `OLLAMA_HOST=0.0.0.0:11434` en natif). Le front d'une autre machine du LAN pointe sur `http://<IP_LAN>:11434`. A ne pas exposer publiquement sans filtrage : Ollama n'embarque pas d'authentification ; un reverse proxy (nginx + basic auth) ou une restriction firewall par IP est necessaire pour un usage ouvert.

## 7. Note integrite (scenario "code compromis")

Le brief simule une reprise de projet potentiellement compromis. Cote infra :
- Le modele de base est tire du **registre officiel Ollama**, pas d'un binaire fourni par l'equipe precedente.
- L'adapter LoRA herite (`models/phi3_financial/adapter_model.safetensors`) n'est **pas** utilise : le deploiement sert le modele de base propre + system prompt, pas l'adapter potentiellement piege (audit du ressort de la filiere CYBER).
- Le `Modelfile` a ete relu : uniquement un `FROM`, un `SYSTEM` et des `PARAMETER` — aucune commande ni source non fiable.

## 8. Reproduction

**Docker :**
```bash
cd rendu/infra
docker compose up -d
docker compose logs -f model-init
```

**Natif :**
```bash
cd rendu/infra
./setup-model.sh        # ou .\setup-model.ps1 sous Windows
```

Puis front → Serveur `http://localhost:11434`, Modele `phi35-financial`.
