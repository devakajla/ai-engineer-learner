def usage_summary(response):
    usage = response.usage
    return {
        "input": usage.prompt_tokens,
        "output": usage.completion_tokens,
        "total": usage.total_tokens,
    }
