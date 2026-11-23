def choose_approach(prompt_works, knowledge_is_private_or_changing, needs_style_or_format, example_count):
    if prompt_works:
        return "prompting"
    if knowledge_is_private_or_changing:
        return "rag"
    if needs_style_or_format:
        return "fine-tune" if example_count >= 500 else "few-shot"
    return "prompting"
