import socket
import psycopg2


def check_postgres_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("127.0.0.1", 5432))
    sock.close()
    return result == 0


def check_postgres_login():
    # Try common defaults
    uris = [
        "postgresql://postgres:postgres@localhost:5432/postgres",
        "postgresql://postgres:admin@localhost:5432/postgres",
        "postgresql://postgres:123456@localhost:5432/postgres",
        "postgresql://postgres@localhost:5432/postgres",  # No password
    ]

    for uri in uris:
        try:
            conn = psycopg2.connect(uri)
            conn.close()
            return True, uri
        except:
            pass
    return False, None


if __name__ == "__main__":
    is_open = check_postgres_port()
    print(f"Port 5432 Open: {is_open}")

    if is_open:
        success, uri = check_postgres_login()
        if success:
            print(f"Login Success: {uri}")
        else:
            print("Login Failed: Could not guess credentials.")
    else:
        print("Postgres not running locally.")
