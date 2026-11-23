def fits(prompt_tokens, max_output, context_limit):
    return prompt_tokens + max_output <= context_limit
