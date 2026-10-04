import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from database import get_connection


load_dotenv()


SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "development-secret-change-in-production"
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token"
)


def hash_password(password: str) -> str:

    return pwd_context.hash(
        password
    )


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_access_token(
    username: str,
    role: str
) -> str:

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": username,
        "role": role,
        "exp": expires_at
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def get_user(
    username: str
):

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    username,
                    password_hash,
                    role,
                    is_active
                FROM users
                WHERE username = %s
                """,
                (username,)
            )

            user = cursor.fetchone()

        if user is None:
            return None

        return {
            "id": user[0],
            "username": user[1],
            "password_hash": user[2],
            "role": user[3],
            "is_active": user[4]
        }

    finally:

        connection.close()


def authenticate_user(
    username: str,
    password: str
):

    user = get_user(
        username
    )

    if user is None:
        return None

    if not user["is_active"]:
        return None

    if not verify_password(
        password,
        user["password_hash"]
    ):
        return None

    return user


def get_current_user(
    token: str = Depends(
        oauth2_scheme
    )
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials.",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[
                ALGORITHM
            ]
        )

        username = payload.get(
            "sub"
        )

        role = payload.get(
            "role"
        )

        if not username or not role:
            raise credentials_exception

    except JWTError:

        raise credentials_exception

    user = get_user(
        username
    )

    if user is None:
        raise credentials_exception

    if not user["is_active"]:
        raise credentials_exception

    return user


def require_roles(
    *allowed_roles
):

    def role_dependency(
        current_user=Depends(
            get_current_user
        )
    ):

        if current_user["role"] not in allowed_roles:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions."
            )

        return current_user

    return role_dependency