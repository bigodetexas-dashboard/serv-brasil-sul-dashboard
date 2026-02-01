import json
with open('high_sec.json') as f:
    d = json.load(f)

print("ALL HIGH SEVERITY ISSUES (No Skips except backups):")
for i in d['results']:
    fname = i['filename']
    if 'backups' in fname:
        continue

    print(f"{fname}:{i['line_number']} - {i['test_id']} ({i['issue_text']})")
