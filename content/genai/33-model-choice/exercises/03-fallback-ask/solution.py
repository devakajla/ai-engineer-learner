def ask_with_fallback(client, model_names, messages):
    if not model_names:
        raise ValueError("no models to try")
    last_error = None
    for name in model_names:
        try:
            response = client.chat.completions.create(model=name, messages=messages)
            return name, response.choices[0].message.content
        except Exception as error:
            last_error = error
    raise last_error
