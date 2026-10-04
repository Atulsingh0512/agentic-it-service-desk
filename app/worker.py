from rq import SimpleWorker

from jobs.queue import agent_queue, redis_connection
from logging_config import configure_logging, get_logger


configure_logging()

logger = get_logger("agent_worker")


def start_worker():

    logger.info(
        "Agent background worker starting."
    )

    worker = SimpleWorker(
        queues=[agent_queue],
        connection=redis_connection
    )

    logger.info(
        "Listening on queue: %s",
        agent_queue.name
    )

    worker.work()


if __name__ == "__main__":
    start_worker()