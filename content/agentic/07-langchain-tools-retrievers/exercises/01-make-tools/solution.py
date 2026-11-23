from langchain_core.tools import tool


@tool
def convert_temp(celsius: float) -> float:
    """Convert a temperature from Celsius to Fahrenheit."""
    return celsius * 9 / 5 + 32


@tool
def word_count(text: str) -> int:
    """Count the words in a text."""
    return len(text.split())


def make_tools():
    return [convert_temp, word_count]
