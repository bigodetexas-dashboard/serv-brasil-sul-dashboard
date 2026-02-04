import sqlite3

try:
    conn = sqlite3.connect("bigode_unified.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, type, sql FROM sqlite_master WHERE name IN ('events', 'deaths_log')"
    )
    results = cursor.fetchall()

    print(f"Found {len(results)} matches:")
    for name, type_, sql in results:
        print(f"\nName: {name}")
        print(f"Type: {type_}")
        print(f"SQL: {sql}")

    conn.close()
except Exception as e:
    print(f"Error: {e}")
