# INFRA — Serveur d'inference Phi-3.5-Financial

Deploiement du serveur d'inference pour l'assistant financier TechCorp, via **Ollama**.
Le modele est construit a partir de `ollama_server/Modelfile` (system prompt finance + parametres d'inference).

Deux modes de lancement au choix : **Docker** (recommande, portable) ou **natif** (Ollama installe sur la machine).

---

## Option 1 — Docker (recommande)

Prerequis : **Docker Desktop** (https://www.docker.com/products/docker-desktop/). Rien d'autre a installer.

Depuis le dossier `rendu/infra/` :

```bash
docker compose up -d
```

Ce qui se passe :
1. Le conteneur `techcorp-ollama` demarre le serveur sur `http://localhost:11434`.
2. Le conteneur `techcorp-model-init` attend le serveur, `pull` `phi3.5`, puis `create` le modele **`phi35-financial`** depuis le Modelfile, et s'arrete.

Suivre la construction du modele :
```bash
docker compose logs -f model-init
```
Quand tu vois `Modele pret :` suivi de la liste des modeles, c'est operationnel.

Arreter / nettoyer :
```bash
docker compose down       # arrete les conteneurs
docker compose down -v    # + supprime le volume (modeles telecharges)
```

---

## Option 2 — Natif (sans Docker)

Prerequis : **Ollama** installe (https://ollama.com/download), service demarre.

Depuis le dossier `rendu/infra/` :

**Windows (PowerShell)**
```powershell
.\setup-model.ps1
```

**Linux / macOS**
```bash
chmod +x setup-model.sh
./setup-model.sh
```

Le script verifie Ollama, `pull` `phi3.5`, `create` `phi35-financial`, puis verifie l'API.

---

## Connexion du front (DEV WEB)

Une fois le serveur operationnel (Docker ou natif), dans l'interface web :

| Champ    | Valeur                     |
|----------|----------------------------|
| Serveur  | `http://localhost:11434`   |
| Modele   | `phi35-financial`          |

## Verification manuelle

```bash
curl http://localhost:11434/api/tags          # doit lister phi35-financial
ollama run phi35-financial "Explique l'EBITDA simplement."   # (mode natif)
```

## Benchmark

Mesure de performances (latence, tokens/sec) + generation automatique de `BENCHMARK.md` :
```bash
python benchmark.py
```

## Optionnel — exposer sur le reseau

- **Docker** : le port `11434` est deja publie sur toutes les interfaces, accessible via `http://<IP_LAN>:11434`.
- **Natif** : `OLLAMA_HOST=0.0.0.0:11434 ollama serve` puis donner `http://<IP_LAN>:11434` au front.

A ne pas exposer publiquement sans filtrage (Ollama n'a pas d'authentification). Ouvrir le port au pare-feu si necessaire.
