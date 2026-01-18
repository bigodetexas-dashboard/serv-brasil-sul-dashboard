"""
Utility script to split large files into smaller chunks.
Useful for splitting backup archives into manageable sizes.
"""

import os


def split_file(file_path, chunk_size=512 * 1024 * 1024):
    """
    Split a large file into smaller chunks.

    Args:
        file_path: Path to the file to split
        chunk_size: Size of each chunk in bytes (default: 512MB)
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    part_num = 1

    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break

            part_name = f"{file_path}.{part_num:03d}"
            with open(part_name, "wb") as part_file:
                part_file.write(chunk)

            print(f"Created: {part_name}")
            part_num += 1

    print("Splitting complete.")


if __name__ == "__main__":
    TARGET_FILE = r"d:\dayz xbox\backup_99.9.zip"
    split_file(TARGET_FILE)
