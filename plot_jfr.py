# Erstellt aus einer einzelnen JFR-JSON-Datei einen VisualVM-ähnlichen Monitoring-Graphen
# (CPU-Last oben, Heap-Nutzung unten) für einen einzelnen Benchmark-Lauf.

import json
import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator

# 1. Argumente einlesen
parser = argparse.ArgumentParser(description='Erstellt Monitoring-Graphen aus JFR-JSON-Daten.')
parser.add_argument('json_file',    help='Pfad zur JFR-JSON-Datei (Pflichtargument)')
parser.add_argument('output_image', nargs='?', default=None,
                    help='Pfad für das Ausgabe-PNG (Standard: <json_file>_monitoring.png)')
args = parser.parse_args()

JSON_FILE = args.json_file
OUTPUT_IMAGE = args.output_image or os.path.splitext(JSON_FILE)[0] + '_monitoring.png'

# 2. JSON-Datei einlesen
print(f"Lese Daten aus {JSON_FILE}...")
try:
    with open(JSON_FILE, 'r') as file:
        data = json.load(file)
except FileNotFoundError:
    print(f"FEHLER: Die Datei {JSON_FILE} wurde nicht gefunden!")
    exit(1)

cpu_data = []
heap_data = []
heap_periodic_data = []

events = data.get('recording', {}).get('events', data)

# 3. Daten parsen
for event in events:
    event_type = event.get('type')
    values = event.get('values', {})
    timestamp = values.get('startTime')

    if not timestamp:
        continue

    time_obj = pd.to_datetime(timestamp)

    if event_type == 'jdk.CPULoad':
        jvm_cpu_load = (values.get('jvmUser', 0) + values.get('jvmSystem', 0)) * 100
        cpu_data.append({'Time': time_obj, 'CPU Load (%)': jvm_cpu_load})

    elif event_type == 'jdk.GCHeapSummary':
        heap_used_mb = values.get('heapUsed', 0) / (1024 * 1024)
        heap_space = values.get('heapSpace', {})
        if isinstance(heap_space, dict):
            heap_size_mb = heap_space.get('committedSize', 0) / (1024 * 1024)
        else:
            heap_size_mb = 0
        if heap_size_mb > 0:
            heap_data.append({
                'Time': time_obj,
                'Heap Used (MB)': heap_used_mb,
                'Heap Size (MB)': heap_size_mb
            })

    elif event_type == 'jdk.GCHeapMemoryUsage':
        used_mb = values.get('used', 0) / (1024 * 1024)
        committed_mb = values.get('committed', 0) / (1024 * 1024)
        if committed_mb > 0:
            heap_periodic_data.append({
                'Time': time_obj,
                'Heap Used (MB)': used_mb,
                'Heap Size (MB)': committed_mb
            })

# 4. DataFrames erstellen
if not cpu_data or not heap_data:
    print("FEHLER: Es wurden keine CPU- oder Heap-Daten in der JSON gefunden!")
    exit(1)

df_cpu = pd.DataFrame(cpu_data).set_index('Time').sort_index()
df_heap = pd.DataFrame(heap_data).set_index('Time').sort_index()

df_periodic = None
if heap_periodic_data:
    df_periodic = pd.DataFrame(heap_periodic_data).set_index('Time').sort_index()
    print(f"  -> {len(df_periodic)} periodische GCHeapMemoryUsage-Events gefunden.")
else:
    print("  -> Keine periodischen Heap-Daten. Fallback auf GCHeapSummary.")

# Zeitspanne des Prozesses
all_times = [df_cpu.index.min(), df_cpu.index.max(),
             df_heap.index.min(), df_heap.index.max()]
if df_periodic is not None:
    all_times += [df_periodic.index.min(), df_periodic.index.max()]
global_start = min(all_times)
global_end   = max(all_times)

df_heap.loc[global_end] = df_heap.iloc[-1]
df_heap = df_heap.sort_index()

if df_periodic is not None:
    df_periodic.loc[global_end] = df_periodic.iloc[-1]
    df_periodic = df_periodic.sort_index()
# df_periodic bevorzugt, df_heap bleibt Fallback

# Maximumwerte berechnen 
max_cpu = df_cpu['CPU Load (%)'].max()
df_mem = df_periodic if df_periodic is not None else df_heap
max_used_mb = df_mem['Heap Used (MB)'].max()
max_size_mb = df_mem['Heap Size (MB)'].max()

# X-Achsen-Ticks: Startzeit + Minutenraster + Endzeit. Rasterabstand richtet sich nach der Laufzeit
duration_sec = (global_end - global_start).total_seconds()
if duration_sec <= 120:
    freq = '30s'
elif duration_sec <= 600:
    freq = '1min'
elif duration_sec <= 1800:
    freq = '2min'
else:
    freq = '5min'
regular_ticks = pd.date_range(global_start.ceil('min'), global_end.floor('min'), freq=freq)
x_ticks = sorted(set([global_start, global_end] + list(regular_ticks)))
x_tick_nums = mdates.date2num([t.floor('ms').to_pydatetime() for t in x_ticks])

# 5. Visualisierung erstellen 
print("Generiere Graphen...")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

#Graph 1: CPU Auslastung
ax1.plot(df_cpu.index, df_cpu['CPU Load (%)'], color='#1f77b4', linewidth=1.5, label='JVM CPU-Last')
ax1.fill_between(df_cpu.index, df_cpu['CPU Load (%)'], color='#1f77b4', alpha=0.2)
ax1.set_ylabel('CPU Auslastung (%)')
duration_s = int((global_end - global_start).total_seconds())
duration_str = f"{duration_s // 60} min {duration_s % 60} s"
ax1.set_title(
    f'CRExplorer Benchmark: Ressourcen-Monitoring\n'
    f'{os.path.basename(JSON_FILE)}  —  Laufzeit: {duration_str}',
    fontsize=14, pad=15
)
ax1.grid(True, linestyle='--', alpha=0.7)
ax1.legend(loc='upper right')
ax1.set_ylim(0, 100)
ax1.yaxis.set_major_locator(MultipleLocator(10))
ax1.set_xlim(global_start, global_end)
ax1.margins(x=0)
ax2.margins(x=0)

# Max-Wert CPU 
ax1.text(0.005, 0.97, f'Max: {max_cpu:.1f} %',
         transform=ax1.transAxes, fontsize=9, va='top', ha='left',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#1f77b4', alpha=0.85))

# Graph 2: Memory (Heap)
if df_periodic is not None:
    ax2.plot(df_periodic.index, df_periodic['Heap Size (MB)'], color='#ff7f0e', linewidth=1.5,
             drawstyle='steps-post', label='Heap Size (Committed)')
    ax2.fill_between(df_periodic.index, df_periodic['Heap Size (MB)'], color='#ff7f0e', alpha=0.15,
                     step='post')
    ax2.plot(df_periodic.index, df_periodic['Heap Used (MB)'], color='#1f77b4', linewidth=1.5,
             drawstyle='steps-post', label='Used Heap (1s-Polling)')
    ax2.fill_between(df_periodic.index, df_periodic['Heap Used (MB)'], color='#1f77b4', alpha=0.4,
                     step='post')
else:
    ax2.plot(df_heap.index, df_heap['Heap Size (MB)'], color='#ff7f0e', linewidth=1.5,
             drawstyle='steps-post', label='Heap Size (Committed)')
    ax2.fill_between(df_heap.index, df_heap['Heap Size (MB)'], color='#ff7f0e', alpha=0.15,
                     step='post')
    ax2.plot(df_heap.index, df_heap['Heap Used (MB)'], color='#1f77b4', linewidth=1.5,
             drawstyle='steps-post', label='Used Heap (GC-Events)')
    ax2.fill_between(df_heap.index, df_heap['Heap Used (MB)'], color='#1f77b4', alpha=0.4,
                     step='post')

ax2.set_ylabel('Speichernutzung (MB)')
ax2.set_xlabel('Uhrzeit')
ax2.grid(True, linestyle='--', alpha=0.7)
ax2.legend(loc='lower right')
ax2.set_ylim(0, max_size_mb)

# Max-Werte Memory 
ax2.text(0.995, 0.97,
         f'Max Used: {max_used_mb:.1f} MB  |  Heap Size: {max_size_mb:.1f} MB',
         transform=ax2.transAxes, fontsize=9, va='top', ha='right',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#ff7f0e', alpha=0.85))

# X-Achse: Ticks mit Start-/Endzeit + Minutenraster
ax2.set_xticks(x_tick_nums)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
fig.autofmt_xdate(rotation=35, ha='right')

plt.tight_layout()
plt.savefig(OUTPUT_IMAGE, dpi=300)
print(f"Fertig! Grafik wurde als '{OUTPUT_IMAGE}' gespeichert.")
