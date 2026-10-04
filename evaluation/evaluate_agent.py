from pathlib import Path
import sys


APP_DIR = Path(__file__).resolve().parent.parent / "app"

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


from supervisor import app as agent_app
from agent_test_cases import AGENT_TEST_CASES


def evaluate_agent():

    total = len(
        AGENT_TEST_CASES
    )

    correct = 0

    results = []

    print(
        "\n========================================"
    )
    print(
        "ENTERPRISE IT SERVICE DESK"
    )
    print(
        "AGENT EVALUATION"
    )
    print(
        "========================================\n"
    )

    for test_case in AGENT_TEST_CASES:

        test_id = test_case["id"]

        question = test_case["input"]

        expected_intent = (
            test_case["expected_intent"]
        )

        print(
            f"Running {test_id}..."
        )

        try:

            response = agent_app.invoke(
                {
                    "messages": [
                        {
                            "role":
                                "user",
                            "content":
                                question
                        }
                    ],
                    "conversation_context":
                        ""
                },
                config={
                    "configurable": {
                        "thread_id":
                            f"evaluation-{test_id}"
                    }
                }
            )

            if "__interrupt__" in response:

                actual_intent = (
                    response.get(
                        "intent"
                    )
                )

                status = "HITL_REQUIRED"

            else:

                actual_intent = (
                    response.get(
                        "intent"
                    )
                )

                status = (
                    "PASS"
                    if actual_intent
                    == expected_intent
                    else
                    "FAIL"
                )

            if actual_intent == expected_intent:

                correct += 1

            results.append(
                {
                    "id":
                        test_id,
                    "question":
                        question,
                    "expected":
                        expected_intent,
                    "actual":
                        actual_intent,
                    "status":
                        status
                }
            )

            print(
                f"Expected: {expected_intent}"
            )

            print(
                f"Actual:   {actual_intent}"
            )

            print(
                f"Status:   {status}\n"
            )

        except Exception as error:

            results.append(
                {
                    "id":
                        test_id,
                    "question":
                        question,
                    "expected":
                        expected_intent,
                    "actual":
                        "ERROR",
                    "status":
                        "ERROR",
                    "error":
                        str(error)
                }
            )

            print(
                f"ERROR: {error}\n"
            )

    accuracy = (
        correct / total * 100
        if total
        else 0
    )

    print(
        "========================================"
    )

    print(
        f"Total Tests: {total}"
    )

    print(
        f"Correct:     {correct}"
    )

    print(
        f"Accuracy:    {accuracy:.2f}%"
    )

    print(
        "========================================\n"
    )

    return results


if __name__ == "__main__":

    evaluate_agent()