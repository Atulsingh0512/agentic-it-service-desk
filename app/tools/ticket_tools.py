from datetime import datetime

from langchain_core.tools import tool

from database import get_connection, initialize_database


initialize_database()


@tool
def create_ticket(
    title: str,
    description: str,
    category: str
) -> str:
    """Create a new IT service desk ticket."""

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO tickets
                (
                    title,
                    description,
                    category,
                    status,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    title,
                    description,
                    category,
                    "OPEN",
                    datetime.now()
                )
            )

            ticket_id = cursor.fetchone()[0]

        connection.commit()

        return (
            f"Ticket created successfully. "
            f"Ticket ID: {ticket_id}"
        )

    finally:
        connection.close()


@tool
def get_ticket(ticket_id: int) -> str:
    """Get the current status and details of an IT service desk ticket."""

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    title,
                    description,
                    category,
                    status,
                    created_at
                FROM tickets
                WHERE id = %s
                """,
                (ticket_id,)
            )

            ticket = cursor.fetchone()

    finally:
        connection.close()

    if ticket is None:
        return f"Ticket {ticket_id} was not found."

    return (
        f"Ticket ID: {ticket[0]}\n"
        f"Title: {ticket[1]}\n"
        f"Description: {ticket[2]}\n"
        f"Category: {ticket[3]}\n"
        f"Status: {ticket[4]}\n"
        f"Created At: {ticket[5]}"
    )


@tool
def update_ticket_status(
    ticket_id: int,
    status: str
) -> str:
    """Update the status of an existing IT service desk ticket."""

    allowed_statuses = [
        "OPEN",
        "IN_PROGRESS",
        "RESOLVED",
        "CLOSED"
    ]

    status = status.upper()

    if status not in allowed_statuses:
        return (
            f"Invalid status. Allowed statuses: "
            f"{', '.join(allowed_statuses)}"
        )

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT id
                FROM tickets
                WHERE id = %s
                """,
                (ticket_id,)
            )

            ticket = cursor.fetchone()

            if ticket is None:
                return f"Ticket {ticket_id} was not found."

            cursor.execute(
                """
                UPDATE tickets
                SET status = %s
                WHERE id = %s
                """,
                (
                    status,
                    ticket_id
                )
            )

        connection.commit()

    finally:
        connection.close()

    return (
        f"Ticket {ticket_id} status updated "
        f"to {status}."
    )