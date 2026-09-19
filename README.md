# CRExplorer_BA_Benchmarks

Begleit-Repository zur Bachelorarbeit *"KI-gestütztes Performance-Refactoring in der Praxis: Eine Untersuchung zu Claude Code am Beispiel des Java-Tools CRExplorer"* (Niclas Wienzek, HTWK Leipzig). Enthält die Rohdaten, Auswertungsskripte und Diagramme, mit denen die in Kapitel 4 und 5 der Arbeit berichteten Ergebnisse erzeugt wurden.

Die untersuchte Codebase selbst (CRExplorer-Fork mit den vier Optimierungen C1, C2, D1b, D2 als isolierte Git-Branches) liegt in einem separaten Repository: [CRExplorer_BA](https://github.com/Nxclvs/CRExplorer_BA).

## Ordnerstruktur

| Pfad | Inhalt |
|---|---|
| `base/`, `c1/`, `c2/`, `c1c2/`, `d1b/`, `d1bd2/`, `c1d1bd2/`, `c1c2d1b/`, `c1c2d1bd2/` | Je ein Ordner pro untersuchter Variante (Ordnername = Branch-Name im CRExplorer_BA-Repo). Enthält pro Datensatz/Algorithmus/Wiederholung die aus dem JFR-Recording extrahierte `*.json` sowie den zugehörigen Monitoring-Graphen (`*_monitoring.png`, erzeugt mit `plot_jfr.py`). |
| `cre_data/` | Die 27 `.cre`-Exportarchive (climate100, drei Algorithmen x neun Varianten), auf denen die Konformitätsprüfung (`compare_cre_data.py`) basiert. |
| `crs_scripts/` | Die neun CRExplorer-Skriptdateien (`load_and_cluster<Größe><Algo>.crs`), die Laden, Blocking, Matching und Clustering für einen Benchmark-Lauf steuern. |
| `datasets/` | Die drei Web-of-Science-Rohdatensätze (climate100/200/500), Basis aller Benchmark-Läufe. |
| `comparison_graphs/` | Die aggregierten Vergleichsdiagramme über alle Varianten hinweg (`compare_experiments.py`), getrennt nach SQLite-, PostgreSQL- und Gesamt-Ansicht. |
| `correctness_report.txt` | Ergebnis der Konformitätsprüfung (PASS/FAIL je Variante und Algorithmus). |
| `evaluation_summary.json` | Strukturierte Zusammenfassung aller Performance-Kennzahlen (Laufzeit, Heap Used, Heap Size) je Variante, inkl. prozentualer Abweichung zur Baseline. |

## Skripte

- **`compare_cre_data.py`** — vergleicht die `.cre`-Exportarchive jeder Variante inhaltlich gegen die Baseline (Konformitätsprüfung, Kapitel 4.4).
  ```
  python compare_cre_data.py --data-dir cre_data --out correctness_report.txt --detail-dir cre_data/comparisons
  ```
- **`compare_experiments.py`** — erzeugt die Vergleichsdiagramme in `comparison_graphs/` aus den JFR-JSON-Daten.
  ```
  python compare_experiments.py sqlite postgres all
  ```
- **`evaluate_results.py`** — fasst dieselben Rohdaten wie `compare_experiments.py` in `evaluation_summary.json` zusammen (Kapitel 5.1).
  ```
  python evaluate_results.py
  ```
- **`plot_jfr.py`** — erstellt aus einer einzelnen JFR-JSON-Datei einen Monitoring-Graphen (CPU-Last + Heap-Nutzung) für genau einen Lauf.
  ```
  python plot_jfr.py base/climate100LEV_base_run1.json
  ```
- **`benchmark.bat`** / **`export_cre_data.bat`** — dokumentieren die tatsächliche Aufrufreihenfolge, mit der die Benchmark-Läufe bzw. die `.cre`-Exporte erzeugt wurden (lokale Windows-Batch-Skripte mit absoluten Pfaden zur ursprünglichen Arbeitsumgebung, dienen der Nachvollziehbarkeit und sind nicht ohne Anpassung auf einem anderen Rechner lauffähig).
- **`ba_profile.jfc`** — das für alle Läufe verwendete JFR-Profil (Konfiguration, welche Events mit welchem Interval aufgezeichnet werden).

Alle Python-Skripte benötigen `pandas`, `numpy` und `matplotlib`.

