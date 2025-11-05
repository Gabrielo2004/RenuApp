import os
import hashlib
from typing import Optional

from ..storage import StorageService


class UserRepository:
    def __init__(self, storage: StorageService) -> None:
        self.storage = storage

    # --- password helpers ---
    def _generate_salt(self) -> str:
        return os.urandom(16).hex()

    def _hash_password(self, password: str, salt_hex: str) -> str:
        salt = bytes.fromhex(salt_hex)
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_000)
        return dk.hex()

    # --- session helpers ---
    def get_current_user_id(self) -> Optional[int]:
        row = self.storage.fetchone("SELECT value FROM settings WHERE key = ?", ("current_user_id",))
        if row and row[0] is not None:
            try:
                return int(row[0])
            except Exception:
                return None
        return None

    def set_current_user_id(self, user_id: int) -> None:
        self.storage.execute(
            "INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            ("current_user_id", str(user_id)),
        )

    def clear_session(self) -> None:
        self.storage.execute("DELETE FROM settings WHERE key = ?", ("current_user_id",))

    # --- users ---
    def create_user(self, username: str, password: str, email: Optional[str] = None) -> int:
        # Enforce unique username
        existing = self.storage.fetchone("SELECT id FROM users WHERE username = ?", (username.strip(),))
        if existing:
            raise ValueError("El usuario ya existe")
        salt = self._generate_salt()
        pwd_hash = self._hash_password(password, salt)
        self.storage.execute(
            "INSERT INTO users(username, email, password_hash, salt) VALUES (?, ?, ?, ?)",
            (username.strip(), email, pwd_hash, salt),
        )
        row = self.storage.fetchone("SELECT id FROM users WHERE username = ?", (username.strip(),))
        return int(row[0]) if row else 0

    def authenticate(self, username: str, password: str) -> Optional[int]:
        row = self.storage.fetchone(
            "SELECT id, password_hash, salt FROM users WHERE username = ?",
            (username.strip(),),
        )
        if not row:
            return None
        user_id, stored_hash, salt = row
        if self._hash_password(password, salt) == stored_hash:
            return int(user_id)
        return None
