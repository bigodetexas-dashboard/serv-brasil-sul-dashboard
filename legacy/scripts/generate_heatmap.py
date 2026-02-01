import sqlite3
import matplotlib.pyplot as plt
import os

DB_FILE = "bigode_unified.db"
OUTPUT_FILE = "heatmap.png"


def generate_heatmap():
    if not os.path.exists(DB_FILE):
        print(f"Error: {DB_FILE} not found.")
        return False

    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()

        # Get last 500 kills
        cur.execute(
            "SELECT game_x, game_z FROM pvp_kills ORDER BY timestamp DESC LIMIT 500"
        )
        rows = cur.fetchall()
        conn.close()

        if not rows:
            print("No PvP events found in database.")
            return False

        x = [r[0] for r in rows]
        z = [r[1] for r in rows]

        # DayZ Chernarus Map Size approx 15360x15360
        plt.figure(figsize=(10, 10), facecolor="#2f3136")
        ax = plt.gca()
        ax.set_facecolor("#2f3136")

        # Plot points
        plt.scatter(x, z, c="red", alpha=0.5, s=15, edgecolors="none")

        plt.xlim(0, 15360)
        plt.ylim(0, 15360)
        plt.axis("off")  # Hide axis

        # Add title
        plt.title("BigodeTexas - PvP Heatmap", color="white", fontsize=20)

        plt.tight_layout()
        plt.savefig(OUTPUT_FILE, facecolor="#2f3136")
        plt.close()

        print(f"Heatmap generated from database and saved to {OUTPUT_FILE}")
        return True

    except Exception as e:
        print(f"Error generating heatmap: {e}")
        return False


if __name__ == "__main__":
    generate_heatmap()
