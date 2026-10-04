from auth import hash_password
from database import get_connection, initialize_database


ALLOWED_ROLES = {
    "EMPLOYEE",
    "IT_SUPPORT",
    "ADMIN"
}


def create_user(
    username: str,
    password: str,
    role: str
):

    role = role.upper()

    if role not in ALLOWED_ROLES:

        raise ValueError(
            "Invalid role. "
            "Use EMPLOYEE, IT_SUPPORT, or ADMIN."
        )

    initialize_database()

    password_hash = hash_password(
        password
    )

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO users
                (
                    username,
                    password_hash,
                    role,
                    is_active
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    TRUE
                )
                ON CONFLICT (username)
                DO UPDATE SET
                    password_hash = EXCLUDED.password_hash,
                    role = EXCLUDED.role,
                    is_active = TRUE
                """,
                (
                    username,
                    password_hash,
                    role
                )
            )

        connection.commit()

    finally:

        connection.close()

    print(
        f"User '{username}' created successfully "
        f"with role '{role}'."
    )


if __name__ == "__main__":

    print("Create Enterprise IT Service Desk User")

    username = input(
        "Username: "
    ).strip()

    password = input(
        "Password: "
    ).strip()

    role = input(
        "Role (EMPLOYEE/IT_SUPPORT/ADMIN): "
    ).strip()

    create_user(
        username,
        password,
        role
    )