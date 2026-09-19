"""
Wertet die JFR-Benchmark-Ergebnisse aller neun Optimierungsvarianten aus und schreibt eine
strukturierte Zusammenfassung nach results/evaluation_summary.json.

Nutzung:
    python evaluate_results.py
"""

import json
import os

import compare_experiments as ce

OUT_PATH = os.path.join(ce.RESULTS_DIR, "evaluation_summary.json")

# interner Metrikname (aus compare_experiments) -> Feldname in der Ausgabedatei
METRICS = (
    ("duration_s", "runtime_s"),
    ("max_used_mb", "heap_used_mb"),
    ("max_size_mb", "heap_size_mb"),
)


def build_summary():
    """Baut pro Datensatz zuerst die Baseline-Mittelwerte, danach für jede Variante
    Mittelwert/Std/n sowie die prozentuale Abweichung gegenüber genau dieser Baseline."""
    experiment_keys = ce.SETS["all"]
    table = ce.collect(experiment_keys)

    summary = {}
    for size, algo in ce.DATASETS:
        dataset_key = f"climate{size}{algo}"
        dataset_entry = {}

        # Baseline-Mittelwerte einmal vorab bestimmen
        base_means = {}
        for metric_key, _ in METRICS:
            mean, _, _ = ce.aggregate(table[dataset_key]["base"], metric_key)
            base_means[metric_key] = mean

        for exp_key in experiment_keys:
            exp = ce.EXPERIMENTS[exp_key]
            entry = {"label": exp["label"], "engine": exp["engine"]}

            for metric_key, out_key in METRICS:
                mean, std, n = ce.aggregate(table[dataset_key][exp_key], metric_key)
                metric_entry = {"mean": mean, "std": std, "n_runs": n}

                base_mean = base_means[metric_key]
                if mean is not None and base_mean:
                    metric_entry["pct_change_vs_base"] = round(
                        (mean - base_mean) / base_mean * 100, 2
                    )
                entry[out_key] = metric_entry

            dataset_entry[exp_key] = entry

        summary[dataset_key] = dataset_entry

    return summary


def main():
    summary = build_summary()

    os.makedirs(ce.RESULTS_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)

    print(f"Zusammenfassung geschrieben nach: {OUT_PATH}")
    print(f"{len(summary)} Datensätze x {len(ce.SETS['all'])} Varianten.")


if __name__ == "__main__":
    main()
