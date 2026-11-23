def start_simple(question, simple_fn, agent_fn, good_enough):
    try:
        answer = simple_fn(question)
    except Exception:
        return {"answer": agent_fn(question), "used": "agent"}
    if good_enough(answer):
        return {"answer": answer, "used": "simple"}
    return {"answer": agent_fn(question), "used": "agent"}
