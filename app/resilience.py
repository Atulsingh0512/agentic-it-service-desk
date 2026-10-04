import time


def retry_operation(
    operation,
    max_attempts=2,
    delay_seconds=1
):
    last_error = None

    for attempt in range(max_attempts):
        try:
            return operation()

        except Exception as error:
            last_error = error

            if attempt < max_attempts - 1:
                time.sleep(delay_seconds)

    raise last_error