from datetime import datetime

from database import get_connection


def initialize_memory_table():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id SERIAL PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

        connection.commit()

    finally:
        connection.close()


def save_message(
    thread_id: str,
    role: str,
    content: str
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO conversation_messages
                (
                    thread_id,
                    role,
                    content,
                    created_at
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    thread_id,
                    role,
                    content,
                    datetime.now()
                )
            )

        connection.commit()

    finally:
        connection.close()


def get_conversation_history(
    thread_id: str,
    limit: int = 20
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    role,
                    content,
                    created_at
                FROM conversation_messages
                WHERE thread_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (
                    thread_id,
                    limit
                )
            )

            messages = cursor.fetchall()

        messages.reverse()

        return [
            {
                "role": message[0],
                "content": message[1],
                "created_at": message[2].isoformat()
            }
            for message in messages
        ]

    finally:
        connection.close()