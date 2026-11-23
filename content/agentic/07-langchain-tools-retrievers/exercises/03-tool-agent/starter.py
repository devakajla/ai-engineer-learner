# Given from earlier exercises. Do not change these.
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool


@tool
def convert_temp(celsius: float) -> float:
    """Convert a temperature from Celsius to Fahrenheit."""
    return celsius * 9 / 5 + 32


def run_tool_calls(ai_message, tools):
    by_name = {t.name: t for t in tools}
    results = []
    for call in ai_message.tool_calls:
        tool_fn = by_name.get(call["name"])
        if tool_fn is None:
            content = f"Error: unknown tool {call['name']}"
        else:
            try:
                content = str(tool_fn.invoke(call["args"]))
            except Exception as error:
                content = f"Error: {error}"
        results.append(ToolMessage(content=content, tool_call_id=call["id"]))
    return results


# Your task:
def run_langchain_agent(model, question, tools, max_steps=5):
    ...
