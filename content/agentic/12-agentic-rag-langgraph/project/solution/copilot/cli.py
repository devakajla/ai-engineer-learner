from copilot.llm import chat_turn, get_client


def main():
    client = get_client()
    history = []
    print("DevDocs Copilot. Type 'quit' to stop.")
    while True:
        question = input("You: ").strip()
        if question.lower() in ("quit", "exit"):
            break
        if not question:
            continue
        try:
            reply, history = chat_turn(client, history, question, max_history_tokens=2000)
        except Exception as error:
            print(f"Sorry, the model call failed: {error}")
            continue
        print(f"Copilot: {reply}")


if __name__ == "__main__":
    main()
