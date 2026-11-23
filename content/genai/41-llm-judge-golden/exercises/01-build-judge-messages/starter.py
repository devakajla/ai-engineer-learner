# Given from earlier exercises. Do not change these.
JUDGE_SYSTEM = (
    "You are a strict grader. Check if the ANSWER is fully supported by the CONTEXT "
    "and answers the QUESTION. Reply with JSON only: "
    '{"score": <1 to 5>, "reason": "<one short sentence>"}. '
    "5 means fully supported and complete. 1 means not supported or wrong."
)


# Your task:
def build_judge_messages(question, context, answer):
    ...
