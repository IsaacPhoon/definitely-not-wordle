from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

pwd_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return pwd_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_hash.verify(password, hashed)


def create_access_token(user_id: int, secret_key: str) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")


def decode_access_token(token: str, secret_key: str) -> dict:
    return jwt.decode(token, secret_key, algorithms=["HS256"])
