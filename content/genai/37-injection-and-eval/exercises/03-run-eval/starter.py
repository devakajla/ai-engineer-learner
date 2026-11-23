# Given from earlier exercises. Do not change these.
def ask_model(client, system, text):
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": text}],
        temperature=0,
    )
    return response.choices[0].message.content



# Your task:
def run_eval(client, system, cases):
    ...
