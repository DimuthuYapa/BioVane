from app.security.passwords import hash_password, verify_password

# Temporary demo users (development only)

USERS = {
    "admin": {
        "username": "admin",
        "hashed_password": hash_password("BioVane@123"),
        "role": "admin"
    },
    "safety": {
        "username": "safety",
        "hashed_password": hash_password("Safety@123"),
        "role": "safety_supervisor"
    },
    "environment": {
        "username": "environment",
        "hashed_password": hash_password("Environment@123"),
        "role": "environment_officer"
    },
    "operations": {
        "username": "operations",
        "hashed_password": hash_password("Operations@123"),
        "role": "operations_manager"
    }
}


def authenticate_user(username: str, password: str):
    user = USERS.get(username)

    if not user:
        return None

    if not verify_password(password, user["hashed_password"]):
        return None

    return {
        "username": user["username"],
        "role": user["role"]
    }


