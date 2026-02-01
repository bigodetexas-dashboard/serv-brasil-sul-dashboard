import json

with open("high_sec.json") as f:
    d = json.load(f)

print("HIGH SEVERITY ISSUES (Active Files):")
for i in d["results"]:
    fname = i["filename"]
    if "backups" in fname or "backup" in fname.lower() or "test" in fname.lower():
        continue
    print(f"{fname}:{i['line_number']} - {i['test_id']} ({i['issue_text']})")
