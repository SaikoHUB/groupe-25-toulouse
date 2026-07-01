# Rapport d'audit de sécurité — Serveur d'inférence (INFRA)

**Périmètre :** `rendu/infra/` uniquement  
**Date :** 1er juillet 2026  
**Auditeur :** Filière CYBER  
**Fichiers analysés :** `docker-compose.yml`, `setup-model.sh`, `setup-model.ps1`, `benchmark.py`, `README.md`, `DEPLOIEMENT.md`, `BENCHMARK.md`

**Dépendance de déploiement référencée :** `ollama_server/Modelfile` (monté en lecture seule par `docker-compose.yml`, hors dossier `rendu/infra/`)

---

## 1. Résumé exécutif

Le livrable INFRA déploie un serveur **Ollama** (modèle `phi35-financial`) via Docker ou scripts natifs. Il n'y a **pas d'authentification**, **pas de base de données** et **pas de backend applicatif custom** — l'API REST d'Ollama est exposée directement.

| Niveau | Nombre | Verdict global |
|--------|--------|----------------|
| Critique | 0 | — |
| Élevé | 1 | Image Docker non épinglée (`latest`) |
| Moyen | 2 | Exposition réseau documentée, dépendance Modelfile externe |
| Faible | 2 | Bonnes pratiques complémentaires |
| Hors scope | 2 | Choix d'architecture volontaires |
| Positif | 5 | Décisions de sécurité déjà prises |

**Conclusion :** Le déploiement est **conforme au brief** pour un usage local / démonstration. L'équipe INFRA a pris des **décisions de sécurité pertinentes** (modèle officiel, adapter LoRA hérité non utilisé, Modelfile relu, avertissements réseau documentés). Les points d'attention restants concernent surtout la **reproductibilité** (tag `latest`) et l'**exposition du port 11434** si le mode réseau est activé.

---

## 2. Architecture et surface d'attaque

```
setup-model.sh / setup-model.ps1          docker-compose.yml
        │                                        │
        │  ollama pull phi3.5 (registre officiel)│
        │  ollama create phi35-financial         │
        ▼                                        ▼
              Serveur Ollama (:11434)
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   GET /api/tags   POST /api/chat   ollama run (CLI)
        │               │
        ▼               ▼
   Front DEV WEB    benchmark.py (localhost)
```

**Constat clé :** l'INFRA ne développe pas de couche applicative. La sécurité repose sur :
1. L'intégrité du modèle déployé (source, Modelfile).
2. La configuration réseau (localhost vs LAN).
3. Le comportement natif d'Ollama (pas d'auth intégrée).

### Choix d'architecture (hors périmètre d'audit comme vulnérabilités)

| Élément | État | Commentaire |
|---------|------|-------------|
| Authentification | Absente | Ollama n'en fournit pas — conforme au brief hackathon |
| Base de données | Absente | Modèles stockés dans un volume Docker ou le cache Ollama local |
| Backend custom | Absent | API REST Ollama utilisée telle quelle |

---

## 3. Findings détaillés

### INFRA-01 — Image Docker `ollama/ollama:latest` non épinglée

| | |
|---|---|
| **Criticité** | Élevée (supply chain) / Faible (demo locale) |
| **Fichier** | `docker-compose.yml` L4, L24 |
| **Type** | Dépendance non reproductible |

**Description :** Les deux services utilisent `ollama/ollama:latest` sans digest SHA256. Une mise à jour upstream peut modifier le comportement ou introduire une régression sans changement de code dans le repo.

**Preuve :**

```4:4:rendu/infra/docker-compose.yml
    image: ollama/ollama:latest
```

**Recommandation :** Épingler une version explicite, par ex. `ollama/ollama:0.5.4` (ou digest SHA256), pour garantir la reproductibilité lors de la correction.

---

### INFRA-02 — Port 11434 publié sur toutes les interfaces (mode Docker)

| | |
|---|---|
| **Criticité** | Moyenne (si LAN) / Faible (localhost seul) |
| **Fichier** | `docker-compose.yml` L6-7, `README.md` L82-87 |
| **Type** | Exposition réseau |

**Description :** Le mapping `"11434:11434"` expose Ollama sur `0.0.0.0` par défaut. Toute machine du réseau local peut appeler l'API sans authentification.

**Preuve :**

```6:7:rendu/infra/docker-compose.yml
    ports:
      - "11434:11434"
```

**Verdict :** Le risque est **documenté explicitement** dans `README.md` et `DEPLOIEMENT.md` :

> *« A ne pas exposer publiquement sans filtrage (Ollama n'a pas d'authentification). »*

**Recommandation :** Pour un usage strictement local, binder sur `127.0.0.1:11434:11434`. Le mode réseau LAN reste un choix conscient, déjà averti.

---

### INFRA-03 — Modelfile externe monté au runtime

| | |
|---|---|
| **Criticité** | Moyenne (si Modelfile compromis) / Mitigé (état actuel) |
| **Fichier** | `docker-compose.yml` L31, `setup-model.sh` L6, `DEPLOIEMENT.md` L69-74 |
| **Type** | Chaîne d'approvisionnement du modèle |

**Description :** Le modèle custom est construit depuis `../../ollama_server/Modelfile`, fichier hors du dossier `rendu/infra/`. Si ce fichier était altéré, le comportement du modèle changerait au prochain `docker compose up` ou `setup-model.sh`.

**Mitigations déjà en place (documentées) :**

```69:74:rendu/infra/DEPLOIEMENT.md
Le brief simule une reprise de projet potentiellement compromis. Cote infra :
- Le modele de base est tire du **registre officiel Ollama**, pas d'un binaire fourni par l'equipe precedente.
- L'adapter LoRA herite (`models/phi3_financial/adapter_model.safetensors`) n'est **pas** utilise
- Le `Modelfile` a ete relu : uniquement un `FROM`, un `SYSTEM` et des `PARAMETER`
```

**Verdict :** Le Modelfile référencé ne contient que `FROM phi3.5`, un `SYSTEM` et des `PARAMETER` — **aucune commande suspecte**. Le montage est en **lecture seule** (`:ro`), ce qui est une bonne pratique.

**Recommandation :** Conserver la revue du Modelfile à chaque mise à jour ; ne jamais utiliser l'adapter LoRA hérité sans audit complet.

---

### INFRA-04 — Communications en HTTP (localhost)

| | |
|---|---|
| **Criticité** | Faible |
| **Fichiers** | `setup-model.sh`, `benchmark.py`, `README.md` |
| **Type** | Pas de chiffrement en transit |

**Description :** Tous les appels ciblent `http://localhost:11434`. Normal pour une démo locale ; le trafic ne quitte pas la machine en mode correction.

**Verdict :** **Acceptable** dans le contexte du challenge.

---

### INFRA-05 — Pas de rate limiting sur l'API Ollama

| | |
|---|---|
| **Criticité** | Faible |
| **Fichiers** | `docker-compose.yml`, scripts de setup |
| **Type** | Abus de ressources |

**Description :** Aucune limitation de débit configurée. Un client peut saturer le serveur via `/api/chat`.

**Verdict :** Limitation inhérente à Ollama en mode démo. Acceptable pour le périmètre hackathon.

---

## 4. Points positifs

### ✅ Adapter LoRA hérité volontairement non déployé

L'équipe INFRA a explicitement **refusé** d'utiliser `models/phi3_financial/adapter_model.safetensors`, potentiellement compromis selon le scénario du brief. Le déploiement repose sur le modèle de base officiel + system prompt propre.

### ✅ Modèle de base tiré du registre officiel Ollama

```37:37:rendu/infra/docker-compose.yml
       ollama pull phi3.5;
```

Pas de binaire custom fourni par l'équipe précédente.

### ✅ Prompt système côté serveur (Modelfile), pas côté client

Contrairement au front DEV WEB, le system prompt est défini dans le `Modelfile` au moment du `ollama create`. Il est **plus difficile à contourner** qu'un prompt injecté depuis le JavaScript du navigateur (bien qu'un appelant direct à l'API puisse toujours envoyer ses propres messages `system`).

### ✅ Montage Modelfile en lecture seule

```31:31:rendu/infra/docker-compose.yml
      - ../../ollama_server/Modelfile:/Modelfile:ro
```

Le conteneur `model-init` ne peut pas modifier le Modelfile source.

### ✅ Scripts de setup sans secrets ni entrées utilisateur

`setup-model.sh` et `setup-model.ps1` exécutent uniquement des commandes `ollama` avec des chemins fixes. Pas d'`eval` sur des données externes, pas de credentials.

### ✅ `benchmark.py` — surface minimale

- Bibliothèque standard Python uniquement (pas de dépendances pip).
- Cible `localhost` uniquement.
- Pas de secrets, pas d'exécution de code distant.

### ✅ Documentation de sécurité réseau présente

`README.md` et `DEPLOIEMENT.md` avertissent clairement sur l'absence d'authentification Ollama et les risques d'exposition LAN/Internet.

### ✅ Paramètres d'inférence conservateurs

`temperature 0.3`, `num_predict 512`, `repeat_penalty 1.1` — réduisent les réponses erratiques ou excessivement longues (cf. `DEPLOIEMENT.md`).

---

## 5. Matrice de risques

| ID | Finding | Criticité | Effort correctif |
|----|---------|-----------|------------------|
| INFRA-01 | Image `latest` non épinglée | Élevée | Faible |
| INFRA-02 | Port 11434 sur 0.0.0.0 | Moyenne (LAN) | Faible |
| INFRA-03 | Modelfile externe | Mitigé | Revue continue |
| INFRA-04 | HTTP localhost | Faible (attendu) | — |
| INFRA-05 | Pas de rate limiting | Faible | — |
| — | Pas d'authentification | Hors scope | — |
| — | Pas de base de données | Hors scope | — |

---

## 6. Plan de remédiation (dans le périmètre INFRA)

### Correctifs recommandés

1. **Épingler la version** de l'image Docker Ollama (remplacer `latest` par un tag ou digest fixe).
2. **Binder sur localhost** si le mode réseau n'est pas nécessaire : `127.0.0.1:11434:11434`.
3. **Conserver l'interdiction** d'utiliser l'adapter LoRA hérité sans audit CYBER complet.

### Actions déjà conformes — ne pas modifier

4. Pas d'authentification sur Ollama — attendu pour le challenge.
5. Pas de base de données — le volume Docker suffit pour la persistance des modèles.
6. System prompt dans le Modelfile — bon placement pour ce niveau d'architecture.

---

## 7. Verdict de déploiement

| Contexte | Verdict |
|----------|---------|
| Démo locale (localhost, mode correction) | ✅ **Conforme** |
| Usage prévu du challenge (test Phi-3.5-Financial) | ✅ **Conforme** |
| Exposition LAN (option documentée) | ⚠️ **Acceptable** avec firewall / réseau de confiance |
| Exposition Internet publique | ❌ **Non recommandé** sans reverse proxy + auth |

---

## 8. Comparaison DEV WEB vs INFRA

| Aspect | DEV WEB | INFRA |
|--------|---------|-------|
| Authentification | Absente (volontaire) | Absente (volontaire) |
| Base de données | Absente (`localStorage` côté navigateur) | Absente (volume Docker) |
| System prompt | Côté client (`app.js`) — contournable | Côté serveur (`Modelfile`) — plus robuste |
| Modèle compromis | N/A | Adapter LoRA hérité **non utilisé** ✅ |
| Documentation des risques | Partielle | **Explicite** (README + DEPLOIEMENT) |

---

## 9. Méthodologie

- Revue statique des 7 fichiers du dossier `rendu/infra/`.
- Vérification du `Modelfile` monté (dépendance de déploiement référencée dans `docker-compose.yml`).
- Analyse de la chaîne de déploiement : source du modèle, intégrité, exposition réseau.
- **Hors périmètre :** audit du contenu de `models/phi3_financial/`, datasets, logs équipe précédente, tests de prompt injection sur le modèle en production.
