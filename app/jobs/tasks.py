from supervisor import app as supervisor_graph

from database import create_audit_log
from memory import save_message
from logging_config import configure_logging, get_logger


configure_logging()

logger = get_logger("agent_job")


def process_agent_request(
    message: str,
    thread_id: str,
    conversation_context: str = ""
):

    logger.info(
        "Agent job started | thread_id=%s",
        thread_id
    )

    try:

        result = supervisor_graph.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "conversation_context": conversation_context
            },
            config={
                "configurable": {
                    "thread_id": thread_id
                }
            }
        )

        if "__interrupt__" in result:

            interrupt_data = result[
                "__interrupt__"
            ][0].value

            approval_message = interrupt_data.get(
                "message",
                "Approval required."
            )

            save_message(
                thread_id=thread_id,
                role="assistant",
                content=approval_message
            )

            create_audit_log(
                thread_id=thread_id,
                user_request=message,
                intent=result.get("intent"),
                agent=None,
                action=interrupt_data.get("action"),
                status="APPROVAL_REQUIRED",
                result=approval_message
            )

            logger.info(
                "Agent job requires approval | thread_id=%s",
                thread_id
            )

            return {
                "status": "approval_required",
                "thread_id": thread_id,
                "intent": result.get("intent"),
                "approval": interrupt_data
            }

        final_result = result.get(
            "tool_result",
            ""
        )

        save_message(
            thread_id=thread_id,
            role="assistant",
            content=final_result
        )

        audit_status = (
            "FAILED"
            if result.get("agent") == "system"
            else "COMPLETED"
        )

        create_audit_log(
            thread_id=thread_id,
            user_request=message,
            intent=result.get("intent"),
            agent=result.get("agent"),
            action=None,
            status=audit_status,
            result=final_result
        )

        logger.info(
            "Agent job completed | thread_id=%s | agent=%s | status=%s",
            thread_id,
            result.get("agent"),
            audit_status
        )

        return {
            "status": (
                "failed"
                if audit_status == "FAILED"
                else "completed"
            ),
            "thread_id": thread_id,
            "intent": result.get("intent"),
            "agent": result.get("agent"),
            "result": final_result,
            "sources": result.get(
                "sources",
                []
            )
        }

    except Exception as error:

        logger.exception(
            "Agent job failed | thread_id=%s",
            thread_id
        )

        create_audit_log(
            thread_id=thread_id,
            user_request=message,
            intent=None,
            agent="system",
            action=None,
            status="FAILED",
            result=str(error)
        )

        return {
            "status": "failed",
            "thread_id": thread_id,
            "agent": "system",
            "result": (
                "Background agent processing failed."
            ),
            "sources": [],
            "error": str(error)
        }