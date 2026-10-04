import os

import psycopg
from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():

    if not DATABASE_URL:

        raise ValueError(
            "DATABASE_URL is not configured in the .env file."
        )

    return psycopg.connect(
        DATABASE_URL
    )


def initialize_database():

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_audit_logs (
                    id SERIAL PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    user_request TEXT NOT NULL,
                    intent TEXT,
                    agent TEXT,
                    action TEXT,
                    status TEXT NOT NULL,
                    result TEXT,
                    created_at TIMESTAMP NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMP NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

        connection.commit()

    finally:

        connection.close()


def create_audit_log(
    thread_id: str,
    user_request: str,
    intent: str | None,
    agent: str | None,
    action: str | None,
    status: str,
    result: str | None
):

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO agent_audit_logs
                (
                    thread_id,
                    user_request,
                    intent,
                    agent,
                    action,
                    status,
                    result
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    thread_id,
                    user_request,
                    intent,
                    agent,
                    action,
                    status,
                    result
                )
            )

        connection.commit()

    finally:

        connection.close()


def get_audit_logs():

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    thread_id,
                    user_request,
                    intent,
                    agent,
                    action,
                    status,
                    result,
                    created_at
                FROM agent_audit_logs
                ORDER BY created_at DESC
                """
            )

            logs = cursor.fetchall()

        return [
            {
                "id": log[0],
                "thread_id": log[1],
                "user_request": log[2],
                "intent": log[3],
                "agent": log[4],
                "action": log[5],
                "status": log[6],
                "result": log[7],
                "created_at": log[8].isoformat()
            }
            for log in logs
        ]

    finally:

        connection.close()