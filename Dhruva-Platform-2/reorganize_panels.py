import json

# Read the current dashboard file
with open('grafana/provisioning/dashboards/Dhruva DevOps Operations Dashboard-v3-oct31.json', 'r', encoding='utf-8') as f:
    dashboard = json.load(f)

panels = dashboard['panels']

# Categorize panels by title patterns
overall_panels = []
latency_gauges = []
payload_stats = []
error_rate_stats = []
error_breakdown_piecharts = []

for panel in panels:
    title = panel.get('title', '')
    panel_type = panel.get('type', '')
    
    if 'Overall' in title:
        overall_panels.append(panel)
    elif 'Latency' in title and panel_type == 'gauge':
        latency_gauges.append(panel)
    elif 'Payload Size' in title and panel_type == 'stat':
        payload_stats.append(panel)
    elif 'Error Rate' in title and panel_type == 'stat':
        error_rate_stats.append(panel)
    elif 'Error Breakdown' in title and panel_type == 'piechart':
        error_breakdown_piecharts.append(panel)

# Sort each category to maintain consistent order
def sort_key_latency(panel):
    title = panel.get('title', '')
    order = ['ASR', 'TTS', 'Translation', 'OCR', 'Transliteration', 'Text Language Detection', 
             'Audio Language Detection', 'NER', 'Speaker Verification', 'Speaker Diarization', 'Language Diarization']
    for i, name in enumerate(order):
        if name in title:
            return i
    return 999

def sort_key_payload(panel):
    title = panel.get('title', '')
    order = ['TTS', 'Translation', 'ASR', 'OCR', 'Transliteration', 'Text Language Detection',
             'Audio Language Detection', 'NER', 'Speaker Verification', 'Speaker Diarization', 'Language Diarization']
    for i, name in enumerate(order):
        if name in title:
            return i
    return 999

def sort_key_error_rate(panel):
    title = panel.get('title', '')
    order = ['ASR', 'TTS', 'Translation', 'OCR', 'Transliteration', 'Text Language Detection',
             'Audio Language Detection', 'NER', 'Speaker Verification', 'Speaker Diarization', 'Language Diarization']
    for i, name in enumerate(order):
        if name in title:
            return i
    return 999

def sort_key_error_breakdown(panel):
    title = panel.get('title', '')
    order = ['ASR', 'TTS', 'Translation', 'OCR', 'Transliteration', 'Text Language Detection',
             'Audio Language Detection', 'NER', 'Speaker Verification', 'Speaker Diarization', 'Language Diarization']
    for i, name in enumerate(order):
        if name in title:
            return i
    return 999

latency_gauges.sort(key=sort_key_latency)
payload_stats.sort(key=sort_key_payload)
error_rate_stats.sort(key=sort_key_error_rate)
error_breakdown_piecharts.sort(key=sort_key_error_breakdown)

# Reconstruct panels in desired order
new_panels = overall_panels + latency_gauges + payload_stats + error_rate_stats + error_breakdown_piecharts

# Update grid positions
y_positions = {
    'overall_start': 0,
    'latency_start': 9,
    'payload_start': 25,  # After latency (9 + 3*8 rows for latency gauges = 33, but let's check)
    'error_rate_start': 33,  # After payload
    'error_breakdown_start': 49  # After error rates
}

# Recalculate positions
current_y = 0

# Overall panels (first row, height 9)
for i, panel in enumerate(overall_panels):
    if i == 0:
        panel['gridPos'] = {'h': 9, 'w': 12, 'x': 0, 'y': 0}
    elif i == 1:
        panel['gridPos'] = {'h': 9, 'w': 12, 'x': 12, 'y': 0}
    current_y = 9

# Latency gauges (8 wide, 3 per row)
latency_rows = (len(latency_gauges) + 2) // 3  # +2 for rounding up
for i, panel in enumerate(latency_gauges):
    row = i // 3
    col = i % 3
    panel['gridPos'] = {'h': 8, 'w': 8, 'x': col * 8, 'y': current_y + row * 8}
current_y += latency_rows * 8

# Payload stats (8 wide, 3 per row)
payload_rows = (len(payload_stats) + 2) // 3
for i, panel in enumerate(payload_stats):
    row = i // 3
    col = i % 3
    panel['gridPos'] = {'h': 8, 'w': 8, 'x': col * 8, 'y': current_y + row * 8}
current_y += payload_rows * 8

# Overall Error Rate (full width)
if error_rate_stats:
    # Find overall error rate
    overall_error = None
    service_error_rates = []
    for panel in error_rate_stats:
        if 'Overall' in panel.get('title', ''):
            overall_error = panel
        else:
            service_error_rates.append(panel)
    
    if overall_error:
        overall_error['gridPos'] = {'h': 5, 'w': 24, 'x': 0, 'y': current_y}
        current_y += 5
    
    # Service error rates (12 wide, 2 per row)
    error_rate_rows = (len(service_error_rates) + 1) // 2
    for i, panel in enumerate(service_error_rates):
        row = i // 2
        col = i % 2
        panel['gridPos'] = {'h': 8, 'w': 12, 'x': col * 12, 'y': current_y + row * 8}
    current_y += error_rate_rows * 8

# Error breakdown piecharts (12 wide, 2 per row, placed next to error rates)
# They should be aligned with their corresponding error rate panels
error_breakdown_start_y = current_y
if error_rate_stats:
    # Find overall error rate to know where service error rates start
    has_overall = any('Overall' in p.get('title', '') for p in error_rate_stats)
    if has_overall:
        error_breakdown_start_y = current_y - error_rate_rows * 8  # Start at same y as service error rates

for i, panel in enumerate(error_breakdown_piecharts):
    row = i // 2
    col = i % 2
    # Place next to error rate panels (x = 12 for right side of error rate panel)
    panel['gridPos'] = {'h': 8, 'w': 12, 'x': 12 + (col * 12), 'y': error_breakdown_start_y + row * 8}

# Update dashboard
dashboard['panels'] = new_panels

# Write back
with open('grafana/provisioning/dashboards/Dhruva DevOps Operations Dashboard-v3-oct31.json', 'w', encoding='utf-8') as f:
    json.dump(dashboard, f, indent=2, ensure_ascii=False)

print(f'Reorganized {len(new_panels)} panels')
print(f'  - Overall: {len(overall_panels)}')
print(f'  - Latency gauges: {len(latency_gauges)}')
print(f'  - Payload stats: {len(payload_stats)}')
print(f'  - Error rate stats: {len(error_rate_stats)}')
print(f'  - Error breakdown piecharts: {len(error_breakdown_piecharts)}')

