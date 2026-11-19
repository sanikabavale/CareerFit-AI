import sys
import getpass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_connection
from database.auth import _hash_password

def main():
    init_db()
    username = input("Admin username: ").strip()
    email = input("Admin email: ").strip().lower()
    password = getpass.getpass("Admin password (8+ chars): ")
    if len(username) < 3 or "@" not in email or len(password) < 8:
        raise SystemExit("Invalid details. Username 3+ chars, valid email, password 8+ chars.")
    with get_connection() as conn:
        exists = conn.execute("SELECT id FROM users WHERE role='admin'").fetchone()
        if exists:
            raise SystemExit("An admin already exists. Bootstrap stopped.")
        conn.execute("INSERT INTO users(username,email,password_hash,role,status) VALUES(?,?,?,'admin','approved')",
                     (username,email,_hash_password(password)))
    print("Admin account created successfully.")

if __name__ == "__main__":
    main()
