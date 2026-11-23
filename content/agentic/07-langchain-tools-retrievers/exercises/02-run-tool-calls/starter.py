# Given from earlier exercises. Do not change these.
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool


@tool
def convert_temp(celsius: float) -> float:
    """Convert a temperature from Celsius to Fahrenheit."""
    return celsius * 9 / 5 + 32


# Your task:
def run_tool_calls(ai_message, tools):
    ...
