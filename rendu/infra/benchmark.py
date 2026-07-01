#!/usr/bin/env python3
"""
Benchmark du serveur d'inference Ollama (INFRA - TechCorp).

Mesure, pour le modele deploye, la latence et le debit de generation
(tokens/sec) sur un jeu de questions finance. Genere un rapport BENCHMARK.md.

Aucune dependance externe : uniquement la bibliotheque standard Python.
Usage :
    python benchmark.py
"""

import json
import platform
import statistics
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

# Force l'UTF-8 en sortie console (evite les soucis d'encodage sous Windows)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# --- Configuration -----------------------------------------------------------
HOST = "http://localhost:11434"
MODEL = "phi35-financial"

PROMPTS = [
    "Explique l'EBITDA simplement.",
    "Compare une action et une obligation en 5 points.",
    "Quels indicateurs regarder avant d'investir dans une entreprise ?",
    "Qu'est-ce que l'interet compose ?",
    "Definis le ratio dette/capitaux propres.",
]

REPORT_PATH = "BENCHMARK.md"
# -----------------------------------------------------------------------------


def call_ollama(prompt: str) -> dict:
    """Envoie une question au modele et renvoie la reponse JSON complete."""
    payload = json.dumps(
        {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        f"{HOST}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read().decode("utf-8"))


def ns_to_s(ns: int) -> float:
    return ns / 1_000_000_000


def run_benchmark():
    print(f"Benchmark modele : {MODEL}")
    print(f"Serveur          : {HOST}\n")

    # Warm-up : le 1er appel charge le modele en memoire (non mesure).
    print("Warm-up (chargement du modele)...")
    try:
        warm = call_ollama("test")
        load_s = ns_to_s(warm.get("load_duration", 0))
        print(f"  -> modele charge en {load_s:.2f}s\n")
    except urllib.error.URLError as e:
        print(f"[X] Impossible de joindre Ollama sur {HOST} : {e}")
        print("    Verifie que le service tourne (ollama serve) et le nom du modele.")
        sys.exit(1)

    results = []
    for i, prompt in enumerate(PROMPTS, 1):
        print(f"[{i}/{len(PROMPTS)}] {prompt}")
        wall_start = time.perf_counter()
        data = call_ollama(prompt)
        wall = time.perf_counter() - wall_start

        eval_count = data.get("eval_count", 0)
        eval_s = ns_to_s(data.get("eval_duration", 1))
        prompt_tokens = data.get("prompt_eval_count", 0)
        total_s = ns_to_s(data.get("total_duration", 0))
        tok_per_s = eval_count / eval_s if eval_s > 0 else 0

        results.append(
            {
                "prompt": prompt,
                "wall": wall,
                "total_s": total_s,
                "prompt_tokens": prompt_tokens,
                "gen_tokens": eval_count,
                "tok_per_s": tok_per_s,
            }
        )
        print(f"      {eval_count} tokens en {total_s:.2f}s  ->  {tok_per_s:.1f} tok/s\n")

    return results


def write_report(results):
    tok_rates = [r["tok_per_s"] for r in results]
    totals = [r["total_s"] for r in results]

    avg_tok = statistics.mean(tok_rates)
    avg_total = statistics.mean(totals)

    machine = f"{platform.system()} {platform.release()} ({platform.machine()})"
    proc = platform.processor() or "n/a"
    py = platform.python_version()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = []
    lines.append("# Benchmark du serveur d'inference (INFRA)\n")
    lines.append(f"- **Modele** : `{MODEL}`")
    lines.append(f"- **Serveur** : Ollama ({HOST})")
    lines.append(f"- **Machine** : {machine}")
    lines.append(f"- **Processeur** : {proc}")
    lines.append(f"- **Python** : {py}")
    lines.append(f"- **Date** : {now}\n")

    lines.append("## Methodologie\n")
    lines.append(
        f"{len(results)} questions finance envoyees au modele via l'API "
        "`/api/chat` (mode non-stream). Un appel de warm-up (chargement du "
        "modele en memoire) precede les mesures et n'est pas compte. Les "
        "metriques de timing proviennent directement d'Ollama "
        "(`eval_count`, `eval_duration`, `total_duration`).\n"
    )

    lines.append("## Resultats par question\n")
    lines.append("| # | Question | Tokens generes | Duree (s) | Debit (tok/s) |")
    lines.append("|---|----------|----------------|-----------|---------------|")
    for i, r in enumerate(results, 1):
        q = r["prompt"] if len(r["prompt"]) <= 45 else r["prompt"][:42] + "..."
        lines.append(
            f"| {i} | {q} | {r['gen_tokens']} | {r['total_s']:.2f} | {r['tok_per_s']:.1f} |"
        )
    lines.append("")

    lines.append("## Synthese\n")
    lines.append(f"- **Debit moyen** : {avg_tok:.1f} tokens/sec")
    lines.append(f"- **Latence moyenne** : {avg_total:.2f} s / reponse")
    lines.append(f"- **Debit min / max** : {min(tok_rates):.1f} / {max(tok_rates):.1f} tok/s\n")

    lines.append("## Interpretation\n")
    lines.append(
        "Le modele `phi3.5` est quantise en Q4 (~2.2 Go), ce qui permet ce "
        "debit sur CPU sans GPU dedie. Les parametres d'inference (temperature "
        "0.3, num_predict 512) bornent la longueur des reponses et stabilisent "
        "la latence, adaptes a un usage d'assistant financier ou la justesse "
        "prime sur la creativite. Pour augmenter le debit : GPU, ou un modele "
        "plus leger (ex. `qwen2.5:3b`, `tinyllama`) au prix de la qualite.\n"
    )

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Rapport ecrit : {REPORT_PATH}")
    print(f"Debit moyen : {avg_tok:.1f} tok/s  |  Latence moyenne : {avg_total:.2f}s")


if __name__ == "__main__":
    res = run_benchmark()
    write_report(res)
