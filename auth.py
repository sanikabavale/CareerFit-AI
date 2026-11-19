import hashlib, hmac, os
from database.db import get_connection

def _hash_password(password, salt=None):
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 310000)
    return salt.hex() + "$" + digest.hex()

def _verify_password(password, stored):
    try:
        salt_hex, digest_hex = stored.split("$", 1)
        candidate = _hash_password(password, bytes.fromhex(salt_hex)).split("$",1)[1]
        return hmac.compare_digest(candidate, digest_hex)
    except Exception:
        return False

def register_user(username, email, password):
    username, email = username.strip(), email.strip().lower()
    if len(username) < 3 or len(password) < 8 or "@" not in email:
        return False, "Enter a username (3+ characters), valid email and password (8+ characters)."
    try:
        with get_connection() as conn:
            conn.execute("INSERT INTO users(username,email,password_hash,role,status) VALUES(?,?,?,'user','pending')",
                         (username, email, _hash_password(password)))
        return True, "Registration submitted. Await admin approval."
    except Exception:
        return False, "Username or email may already be registered."

def authenticate(username, password):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE username=? COLLATE NOCASE", (username.strip(),)).fetchone()
    if not row or not _verify_password(password, row["password_hash"]):
        return None, "Invalid username or password."
    if row["status"] != "approved":
        return None, f"Account status: {row['status']}. Admin approval is required."
    return dict(row), "Login successful."

def get_user_by_id(user_id):
    with get_connection() as conn:
        row = conn.execute("SELECT id,username,email,role,status FROM users WHERE id=?", (user_id,)).fetchone()
    return dict(row) if row else None
