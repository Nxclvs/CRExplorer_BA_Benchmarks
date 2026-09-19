r"""
Vergleicht die .cre-Exportarchive (crdata.json + crmatch.json) jeder Optimierungsvariante
inhaltlich gegen die Baseline, um zu prüfen, ob beide dieselben Match-Ergebnisse liefern.

Nutzung:
    python compare_cre_data.py
    python compare_cre_data.py --data-dir results/data --out results/data/correctness_report.txt
"""

import argparse
import json
import math
import os
import re
import zipfile
from collections import defaultdict

# Pfade relativ zum Skript.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_DIR = os.path.join(SCRIPT_DIR, "results", "data")
DEFAULT_OUT = os.path.join(DEFAULT_DATA_DIR, "correctness_report.txt")
DEFAULT_DETAIL_DIR = os.path.join(DEFAULT_DATA_DIR, "comparisons")

# Toleranz für den Score-Vergleich in crmatch.json.
REL_TOL = 1e-9
ABS_TOL = 1e-9
DETAIL_CAP = 500  

# Suffix 
SUFFIX_TO_VARIANT = {
    "base": "base",
    "crosscompare": "c1",
    "10000batch": "c2",
    "crosscompare_batch": "c1c2",
    "postgres": "d1b",
    "d1bd2": "d1bd2",
    "c1d1bd2": "c1d1bd2",
    "c1c2d1b": "c1c2d1b",
    "c1c2d5b": "c1c2d1b",
    "c1c2d1bd2": "c1c2d1bd2",
}

# Name crs Script Datei
FILENAME_RE = re.compile(r"^climate(?P<size>\d+)(?P<algo>LEV|COS|JACC)_(?P<suffix>.+)\.cre$")


def discover_files(data_dir):
    """Gruppiert vorhandene .cre-Dateien nach (Datensatzgröße, Algorithmus) -> {Variante: Pfad}.
    Fehlende Datensatzgrößen/Varianten werden nicht als Fehler behandelt, sondern im Report
    als 'nicht vorhanden' vermerkt."""
    groups = defaultdict(dict)
    unmapped = []
    for fname in sorted(os.listdir(data_dir)):
        m = FILENAME_RE.match(fname)
        if not m:
            continue  
        size, algo, suffix = m.group("size"), m.group("algo"), m.group("suffix")
        variant = SUFFIX_TO_VARIANT.get(suffix)
        if variant is None:
            unmapped.append(fname)  # unbekanntes Suffix
            continue
        groups[(size, algo)][variant] = os.path.join(data_dir, fname)
    return groups, unmapped


def load_json_member(cre_path, member):
    """Liest eine einzelne JSON-Datei direkt aus dem .cre-ZIP, ohne es komplett zu entpacken."""
    with zipfile.ZipFile(cre_path) as z:
        with z.open(member) as f:
            return json.load(f)


def compare_crdata(base_list, other_list):
    """Feldweiser Vergleich von crdata.json über die stabile numerische ID."""
    base_map = {r["ID"]: r for r in base_list}
    other_map = {r["ID"]: r for r in other_list}
    base_ids = set(base_map)
    other_ids = set(other_map)

    added_ids = sorted(other_ids - base_ids)
    removed_ids = sorted(base_ids - other_ids)

    field_mismatches = []
    for id_ in sorted(base_ids & other_ids):
        b, o = base_map[id_], other_map[id_]
        for k in sorted(set(b) | set(o)):
            bv, ov = b.get(k), o.get(k)
            if bv != ov:
                field_mismatches.append({"ID": id_, "field": k, "base": bv, "variante": ov})

    return {
        "added_ids": added_ids,
        "removed_ids": removed_ids,
        "field_mismatches": field_mismatches,
    }


def canonical_pairs(match_section):
    """Wandelt {"i": {"j": score, ...}, ...} in {(min(i,j), max(i,j)): score} um."""
    pairs = {}
    for outer_key, inner in match_section.items():
        outer = int(outer_key)
        for inner_key, score in inner.items():
            inner_id = int(inner_key)
            pair = (min(outer, inner_id), max(outer, inner_id))
            pairs[pair] = score
    return pairs


def compare_crmatch(base_json, other_json):
    """Vergleicht MATCH_AUTO und MATCH_MANU getrennt."""
    result = {}
    for section in ("MATCH_AUTO", "MATCH_MANU"):
        bp = canonical_pairs(base_json.get(section, {}))
        op = canonical_pairs(other_json.get(section, {}))
        bset, oset = set(bp), set(op)
        common = bset & oset

        score_diffs = []
        for pair in common:
            bv, ov = bp[pair], op[pair]
            if not math.isclose(bv, ov, rel_tol=REL_TOL, abs_tol=ABS_TOL):
                score_diffs.append({"pair": list(pair), "base": bv, "variante": ov})

        result[section] = {
            "added_pairs": [list(p) for p in sorted(oset - bset)],
            "removed_pairs": [list(p) for p in sorted(bset - oset)],
            "score_diffs": score_diffs,
        }
    return result


def summarize_crdata(r):
    return len(r["added_ids"]), len(r["removed_ids"]), len(r["field_mismatches"])


def summarize_crmatch(r):
    total_added = sum(len(r[s]["added_pairs"]) for s in r)
    total_removed = sum(len(r[s]["removed_pairs"]) for s in r)
    total_score_diffs = sum(len(r[s]["score_diffs"]) for s in r)
    return total_added, total_removed, total_score_diffs


def cap_list(lst, cap=DETAIL_CAP):
    "Schneidet sehr lange Abweichungslisten ab."
    if len(lst) <= cap:
        return lst, 0
    return lst[:cap], len(lst) - cap


def write_detail_file(path, dataset, algo, variant, crdata_diff, crmatch_diff):
    """Schreibt bei einer gefundenen Abweichung eine eigene JSON-Datei mit allen betroffenen
    IDs, Paaren und Feldwerten."""
    added_ids, cut_added = cap_list(crdata_diff["added_ids"])
    removed_ids, cut_removed = cap_list(crdata_diff["removed_ids"])
    field_mismatches, cut_fields = cap_list(crdata_diff["field_mismatches"])

    crmatch_capped = {}
    for section, data in crmatch_diff.items():
        added, cut_a = cap_list(data["added_pairs"])
        removed, cut_r = cap_list(data["removed_pairs"])
        score_diffs, cut_s = cap_list(data["score_diffs"])
        crmatch_capped[section] = {
            "added_pairs": added, "added_pairs_truncated": cut_a,
            "removed_pairs": removed, "removed_pairs_truncated": cut_r,
            "score_diffs": score_diffs, "score_diffs_truncated": cut_s,
        }

    payload = {
        "dataset": dataset, "algorithmus": algo, "variante": variant,
        "crdata": {
            "added_ids": added_ids, "added_ids_truncated": cut_added,
            "removed_ids": removed_ids, "removed_ids_truncated": cut_removed,
            "field_mismatches": field_mismatches, "field_mismatches_truncated": cut_fields,
        },
        "crmatch": crmatch_capped,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def run(data_dir, out_path, detail_dir):
    if not os.path.isdir(data_dir):
        raise SystemExit(f"Datenordner nicht gefunden: {data_dir}")
    os.makedirs(detail_dir, exist_ok=True)

    groups, unmapped = discover_files(data_dir)

    report = []
    report.append("Korrektheitsvergleich crdata.json / crmatch.json gegen Baseline")
    report.append(f"Datenordner: {data_dir}")
    report.append("=" * 78)

    total_compared = 0
    total_fail = 0


    for (size, algo) in sorted(groups):
        variants = groups[(size, algo)]
        label = f"climate{size}{algo}"
        report.append(f"\n[{label}]")

        if "base" not in variants:
            report.append("  WARNUNG: keine Baseline (base) vorhanden - überspringe diese Gruppe.")
            continue

        base_path = variants["base"]
        base_crdata = load_json_member(base_path, "crdata.json")
        base_crmatch = load_json_member(base_path, "crmatch.json")

        for variant, path in sorted(variants.items()):
            if variant == "base":
                continue
            total_compared += 1

            other_crdata = load_json_member(path, "crdata.json")
            other_crmatch = load_json_member(path, "crmatch.json")

            crdata_diff = compare_crdata(base_crdata, other_crdata)
            crmatch_diff = compare_crmatch(base_crmatch, other_crmatch)

            a1, r1, f1 = summarize_crdata(crdata_diff)
            a2, r2, f2 = summarize_crmatch(crmatch_diff)
            ok = (a1 == 0 and r1 == 0 and f1 == 0 and a2 == 0 and r2 == 0 and f2 == 0)

            status = "PASS" if ok else "FAIL"
            report.append(
                f"  {variant:12s} {status}  "
                f"crdata[+{a1}/-{r1}/~{f1}]  crmatch[+{a2}/-{r2}/~{f2}]"
            )

            if not ok:
                total_fail += 1
                detail_path = os.path.join(detail_dir, f"{label}_{variant}_diff.json")
                write_detail_file(detail_path, label, algo, variant, crdata_diff, crmatch_diff)
                report.append(f"               -> Detail: {os.path.relpath(detail_path, SCRIPT_DIR)}")

    if unmapped:
        report.append(f"\nNicht zuordenbare Dateien (Suffix unbekannt, ignoriert): {unmapped}")

    report.append("\n" + "=" * 78)
    report.append("ZUSAMMENFASSUNG")
    report.append(f"  Verglichen: {total_compared} Varianten gegen ihre jeweilige Baseline")
    report.append(f"  Abweichungen (FAIL): {total_fail}")
    if total_compared and not total_fail:
        report.append("  Alle verglichenen Varianten sind inhaltlich äquivalent zur Baseline.")

    text = "\n".join(report)
    print(text)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(f"\nBericht gespeichert unter: {out_path}")
    return total_fail


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--detail-dir", default=DEFAULT_DETAIL_DIR)
    args = parser.parse_args()

    fails = run(args.data_dir, args.out, args.detail_dir)
    if fails:
        raise SystemExit(1)  
