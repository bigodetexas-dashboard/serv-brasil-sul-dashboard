import json

with open("high_sec.json") as f:
    d = json.load(f)

print("HIGH SEVERITY ISSUES (Detailed):")
for i in d["results"]:
    fname = i["filename"]
    if "backups" in fname or "backup" in fname.lower() or "test" in fname.lower():
        continue
    # Filter out FTP issues for a second to see what else remains
    if i["test_id"] in ["B402", "B321"]:
        continue

    print(f"{fname}:{i['line_number']} - {i['test_id']} ({i['issue_text']})")
    print(f"Code: {i['code'].strip()}")
    print("-" * 20)
