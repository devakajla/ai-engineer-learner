# Given from earlier exercises. Do not change these.
def ask_model(client, system, text):
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": text}],
        temperature=0,
    )
    return response.choices[0].message.content



def run_eval(client, system, cases):
    failed = []
    for case in cases:
        reply = ask_model(client, system, case["input"]).lower()
        ok = all(word.lower() in reply for word in case.get("must_include", []))
        ok = ok and not any(word.lower() in reply for word in case.get("must_not_include", []))
        if not ok:
            failed.append(case["input"])
    total = len(cases)
    passed = total - len(failed)
    rate = round(passed / total, 4) if total else 0.0
    return {"passed": passed, "total": total, "rate": rate, "failed": failed}
