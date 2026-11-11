import os
from app.security.passwords import hash_password, verify_password

ROLE_CONFIG = {
    "admin": ("BIOVANE_ADMIN_PASSWORD", "admin"),
    "safety": ("BIOVANE_SAFETY_PASSWORD", "safety_supervisor"),
    "environment": ("BIOVANE_ENVIRONMENT_PASSWORD", "environment_officer"),
    "operations": ("BIOVANE_OPERATIONS_PASSWORD", "operations_manager"),
}

USERS = {}

for username, (env_name, role) in ROLE_CONFIG.items():
    password = os.getenv(env_name)
    if password:
        USERS[username] = {
            "username": username,
            "hashed_password": hash_password(password),
            "role": role,
        }


def authenticate_user(username: str, password: str):
    user = USERS.get(username)

    if not user:
        return None

    if not verify_password(password, user["hashed_password"]):
        return None

    return {
        "username": user["username"],
        "role": user["role"],
    }

