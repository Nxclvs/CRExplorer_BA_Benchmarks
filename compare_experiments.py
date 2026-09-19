"""
Baut Vergleichs-Balkendiagramme (Laufzeit, Max Heap Used, Max Heap Size) aus den JFR-Rohdaten
mehrerer Benchmark-Varianten, gruppiert nach Datensatz (climate100/200/500 x LEV/COS/JACC).

Nutzung:
    python compare_experiments.py sqlite
    python compare_experiments.py postgres
    python compare_experiments.py sqlite postgres
"""

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
OUT_DIR = os.path.join(RESULTS_DIR, "comparisons")

# Feste, nie zyklisch vergebene Farbreihenfolge (kategorial) über alle Experimente hinweg.
EXPERIMENTS = {
    "base":       dict(folder="base",     suffix="_base",               label="Base",           color="#2a78d6", engine="SQLite"),
    "c1":         dict(folder="c1",       suffix="_crosscompare",       label="C1",              color="#1baf7a", engine="SQLite"),
    "c2":         dict(folder="c2",       suffix="_10000batch",         label="C2",              color="#eda100", engine="SQLite"),
    "c1c2":       dict(folder="c1c2",     suffix="_crosscompare_batch", label="C1+C2",           color="#008300", engine="SQLite"),
    "c1c2d1b":    dict(folder="c1c2d1b",  suffix="_c1c2d5b",            label="C1+C2+D1b",       color="#4a3aa7", engine="PostgreSQL"),
    "d1b":        dict(folder="d1b",      suffix="_postgres",           label="D1b",             color="#e34948", engine="PostgreSQL"),
    "d1bd2":      dict(folder="d1bd2",    suffix="_d1bd2",              label="D1b+D2",          color="#eb6834", engine="PostgreSQL"),
    "c1c2d1bd2":  dict(folder="c1c2d1bd2", suffix="_c1c2d1bd2",         label="C1+C2+D1b+D2",    color="#e87ba4", engine="PostgreSQL"),
    "c1d1bd2":    dict(folder="c1d1bd2",  suffix="_c1d1bd2",            label="C1+D1b+D2",       color="#7a4a9e", engine="PostgreSQL"),
}

# Welche Experimente in welchem Chart landen.
SETS = {
    "sqlite":   ["base", "c1", "c2", "c1c2"],
    "postgres": ["base", "c1c2d1b", "d1b", "d1bd2", "c1d1bd2", "c1c2d1bd2"],
    "all":      ["base", "c1", "c2", "c1c2", "c1c2d1b", "d1b", "d1bd2", "c1d1bd2", "c1c2d1bd2"],
}

TITLE_SUFFIX = {
    "sqlite":   "SQLite",
    "postgres": "PostgreSQL, mit SQLite-Baseline",
    "all":      "alle Experimente",
}

# Die neun Datensatz/Algorithmus-Kombinationen, die durchgehend benchmarkt wurden.
SIZES = ["100", "200", "500"]
ALGOS = ["LEV", "COS", "JACC"]
DATASETS = [(size, algo) for size in SIZES for algo in ALGOS]

# Anzahl Wiederholungen pro Benchmark (Mittelwert/Standardabweichung).
RUNS = [1, 2, 3]

# Farbpalette für Gitter/Achsen/Beschriftung.
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
INK = "#0b0b0b"
SECONDARY_INK = "#52514e"


def extract_metrics(json_path):
    """Repliziert die Laufzeit-/Heap-Berechnung aus plot_jfr.py."""
    if not os.path.isfile(json_path):
        return None

    with open(json_path, "r") as fh:
        data = json.load(fh)

    events = data.get("recording", {}).get("events", data)

    cpu_times = []
    heap_times, heap_used, heap_size = [], [], []
    periodic_times, periodic_used, periodic_size = [], [], []

    for event in events:
        event_type = event.get("type")
        values = event.get("values", {})
        timestamp = values.get("startTime")
        if not timestamp:
            continue
        time_obj = pd.to_datetime(timestamp)

        if event_type == "jdk.CPULoad":
            #Bestimmung des Zeitfensters (Start/Ende des Laufs)
            cpu_times.append(time_obj)

        elif event_type == "jdk.GCHeapSummary":
            # Fallback-Quelle für Heap-Werte
            used_mb = values.get("heapUsed", 0) / (1024 * 1024)
            heap_space = values.get("heapSpace", {})
            size_mb = heap_space.get("committedSize", 0) / (1024 * 1024) if isinstance(heap_space, dict) else 0
            if size_mb > 0:
                heap_times.append(time_obj)
                heap_used.append(used_mb)
                heap_size.append(size_mb)

        elif event_type == "jdk.GCHeapMemoryUsage":
            # bevorzugte Quelle
            used_mb = values.get("used", 0) / (1024 * 1024)
            committed_mb = values.get("committed", 0) / (1024 * 1024)
            if committed_mb > 0:
                periodic_times.append(time_obj)
                periodic_used.append(used_mb)
                periodic_size.append(committed_mb)

    if not cpu_times or not heap_times:
        return None

    all_times = cpu_times + heap_times + periodic_times
    duration_s = (max(all_times) - min(all_times)).total_seconds()

    # periodische 1s-Werte bevorzugen
    if periodic_times:
        max_used_mb = max(periodic_used)
        max_size_mb = max(periodic_size)
    else:
        max_used_mb = max(heap_used)
        max_size_mb = max(heap_size)

    return dict(duration_s=duration_s, max_used_mb=max_used_mb, max_size_mb=max_size_mb)


def run_json_path(exp, dataset_key, run):
    """Baut den erwarteten Dateipfad einer Wiederholung aus Ordner + Suffix-Konvention zusammen."""
    fname = f"{dataset_key}{exp['suffix']}_run{run}.json"
    return os.path.join(RESULTS_DIR, exp["folder"], fname) if exp["folder"] else os.path.join(RESULTS_DIR, fname)


def collect(experiment_keys):
    """dataset -> experiment -> Liste der Metrik-Dicts"""
    table = {}
    for size, algo in DATASETS:
        dataset_key = f"climate{size}{algo}"
        table[dataset_key] = {}
        for exp_key in experiment_keys:
            exp = EXPERIMENTS[exp_key]
            run_metrics = []
            for run in RUNS:
                path = run_json_path(exp, dataset_key, run)
                metrics = extract_metrics(path)
                if metrics is not None:
                    run_metrics.append(metrics)

            # fehlende Läufe beim Aufruf sichtbar machen
            if len(run_metrics) < len(RUNS):
                if run_metrics:
                    print(f"  WARNUNG: nur {len(run_metrics)}/{len(RUNS)} Läufe gefunden -> {dataset_key} / {exp_key}")
                else:
                    print(f"  WARNUNG: keine Läufe gefunden -> {dataset_key} / {exp_key}")

            table[dataset_key][exp_key] = run_metrics
    return table


def aggregate(run_metrics, metric_key):
    """Liste von Metrik-Dicts -> (mean, std, n). std=0 bei n<2, (None, None, 0) bei n=0."""
    values = [m[metric_key] for m in run_metrics]
    n = len(values)
    if n == 0:
        return None, None, 0
    mean = float(np.mean(values))
    std = float(np.std(values, ddof=1)) if n > 1 else 0.0
    return mean, std, n


def plot_metric(table, experiment_keys, metric_key, ylabel, title, out_path, footnote=None):
    # Balkenbreite/-position: die Experimente einer Datensatzgruppe sitzen nebeneinander.
    n_groups = len(DATASETS)
    n_bars = len(experiment_keys)
    group_width = 0.82
    bar_width = group_width / n_bars

    fig_width = max(13, 1.35 * n_bars + 4)
    fig, ax = plt.subplots(figsize=(fig_width, 6.5))

    x_centers = np.arange(n_groups)

    max_val = 0
    any_partial_n = False
    for bar_i, exp_key in enumerate(experiment_keys):
        exp = EXPERIMENTS[exp_key]
        offset = (bar_i - (n_bars - 1) / 2) * bar_width
        xs = x_centers + offset

        # pro Experiment über alle neun Datensätze hinweg Balkenhöhe/Fehlerbalken sammeln
        heights, errs, missing_flags, ns = [], [], [], []
        for size, algo in DATASETS:
            dataset_key = f"climate{size}{algo}"
            mean, std, n = aggregate(table[dataset_key][exp_key], metric_key)
            if n == 0:
                heights.append(0)
                errs.append(0)
                missing_flags.append(True)
                ns.append(0)
            else:
                heights.append(mean)
                errs.append(std)
                missing_flags.append(False)
                ns.append(n)
                max_val = max(max_val, mean + std)
                if n < len(RUNS):
                    any_partial_n = True

        bars = ax.bar(xs, heights, width=bar_width * 0.92, yerr=errs, capsize=3,
                       error_kw=dict(ecolor=SECONDARY_INK, elinewidth=0.9, capthick=0.9, zorder=4),
                       color=exp["color"], label=exp["label"], zorder=3)

        # Beschriftung je Balken: "n/a" bei fehlender Messung, sonst Mittelwert +- Std
        for bar, h, err, missing, n in zip(bars, heights, errs, missing_flags, ns):
            if missing:
                ax.text(bar.get_x() + bar.get_width() / 2, max_val * 0.02 if max_val else 0.5,
                        "n/a", rotation=90, ha="center", va="bottom",
                        fontsize=7, color=MUTED)
            else:
                star = "*" if n < len(RUNS) else ""
                ax.text(bar.get_x() + bar.get_width() / 2, h + err + max_val * 0.012,
                        f"{h:,.0f}±{err:,.0f}{star}", rotation=90, ha="center", va="bottom",
                        fontsize=6.5, color=SECONDARY_INK)

    # Achsen, Gitter und Rahmen
    ax.set_xticks(x_centers)
    ax.set_xticklabels([f"climate{size}\n{algo}" for size, algo in DATASETS], fontsize=9)
    ax.set_ylabel(ylabel, color=INK)
    ax.set_title(title, fontsize=14, pad=14, color=INK)
    ax.set_ylim(0, max_val * 1.18 if max_val else 1)

    ax.grid(True, axis="y", linestyle="--", alpha=0.7, color=GRID, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(AXIS)
    ax.tick_params(colors=SECONDARY_INK)

    ax.legend(loc="upper left", bbox_to_anchor=(0, -0.13), ncol=min(n_bars, 5),
               frameon=False, fontsize=9)

    # Fussnote
    full_footnote = footnote or ""
    if any_partial_n:
        note = f"* basiert auf weniger als {len(RUNS)} Wiederholungen"
        full_footnote = f"{full_footnote}   {note}" if full_footnote else note
    if full_footnote:
        fig.text(0.01, 0.005, full_footnote, fontsize=8, color=MUTED, ha="left", va="bottom", style="italic")

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {out_path}")


def run_set(set_name):
    """Erzeugt alle drei Diagramme (Laufzeit, Heap Used, Heap Size) für ein Experiment-Set."""
    experiment_keys = SETS[set_name]
    print(f"\n== Set '{set_name}': {', '.join(EXPERIMENTS[k]['label'] for k in experiment_keys)} ==")

    os.makedirs(OUT_DIR, exist_ok=True)
    table = collect(experiment_keys)

    suffix = TITLE_SUFFIX[set_name]

    # Mix von unterschiedlichen DB-Engines
    engines_used = {EXPERIMENTS[k]["engine"] for k in experiment_keys}
    footnote = None
    if len(engines_used) > 1:
        parts = [f"{EXPERIMENTS[k]['label']}: {EXPERIMENTS[k]['engine']}" for k in experiment_keys]
        footnote = "Hinweis – unterschiedliche DB-Engines: " + " | ".join(parts)

    plot_metric(
        table, experiment_keys, "duration_s",
        ylabel="Laufzeit (s)",
        title=f"Laufzeit-Vergleich ({suffix})",
        out_path=os.path.join(OUT_DIR, f"compare_{set_name}_runtime.png"),
        footnote=footnote,
    )
    plot_metric(
        table, experiment_keys, "max_used_mb",
        ylabel="Max Heap Used (MB)",
        title=f"Max. genutzter Heap im Vergleich ({suffix})",
        out_path=os.path.join(OUT_DIR, f"compare_{set_name}_heap_used.png"),
        footnote=footnote,
    )
    plot_metric(
        table, experiment_keys, "max_size_mb",
        ylabel="Max Heap Size / Committed (MB)",
        title=f"Max. Heap-Größe (Committed) im Vergleich ({suffix})",
        out_path=os.path.join(OUT_DIR, f"compare_{set_name}_heap_size.png"),
        footnote=footnote,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sets", nargs="+", choices=list(SETS.keys()),
                         help="Welche(s) Experiment-Set(s) verglichen werden sollen")
    args = parser.parse_args()

    for set_name in args.sets:
        run_set(set_name)
