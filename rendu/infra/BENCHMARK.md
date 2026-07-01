# Benchmark du serveur d'inference (INFRA)

- **Modele** : `phi35-financial`
- **Serveur** : Ollama (http://localhost:11434)
- **Machine** : Windows 11 (AMD64)
- **Processeur** : Intel64 Family 6 Model 151 Stepping 5, GenuineIntel
- **Python** : 3.14.4
- **Date** : 2026-07-01 14:27

## Methodologie

5 questions finance envoyees au modele via l'API `/api/chat` (mode non-stream). Un appel de warm-up (chargement du modele en memoire) precede les mesures et n'est pas compte. Les metriques de timing proviennent directement d'Ollama (`eval_count`, `eval_duration`, `total_duration`).

## Resultats par question

| # | Question | Tokens generes | Duree (s) | Debit (tok/s) |
|---|----------|----------------|-----------|---------------|
| 1 | Explique l'EBITDA simplement. | 512 | 10.23 | 85.5 |
| 2 | Compare une action et une obligation en 5 ... | 512 | 6.26 | 83.3 |
| 3 | Quels indicateurs regarder avant d'investi... | 512 | 5.76 | 91.0 |
| 4 | Qu'est-ce que l'interet compose ? | 512 | 5.80 | 90.2 |
| 5 | Definis le ratio dette/capitaux propres. | 362 | 4.07 | 91.8 |

## Synthese

- **Debit moyen** : 88.4 tokens/sec
- **Latence moyenne** : 6.43 s / reponse
- **Debit min / max** : 83.3 / 91.8 tok/s

## Interpretation

Le modele `phi3.5` est quantise en Q4 (~2.2 Go), ce qui permet ce debit sur CPU sans GPU dedie. Les parametres d'inference (temperature 0.3, num_predict 512) bornent la longueur des reponses et stabilisent la latence, adaptes a un usage d'assistant financier ou la justesse prime sur la creativite. Pour augmenter le debit : GPU, ou un modele plus leger (ex. `qwen2.5:3b`, `tinyllama`) au prix de la qualite.
