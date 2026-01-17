import os
import sys


def split_file(file_path, chunk_size=512 * 1024 * 1024):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    file_size = os.path.getsize(file_path)
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
    target_file = r"d:\dayz xbox\backup_99.9.zip"
    split_file(target_file)
