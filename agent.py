def ai_agent():
    """A simple command-line agent for Python practice."""
    print("Welcome to Raghu AI Agent!")
    print("---------------------------")

    while True:
        user_input = input("You: ").strip().lower()

        if user_input == "hello":
            print("AI Agent: Hello! How can I help you?")
        elif user_input == "help":
            print("AI Agent: Try hello, help, or bye.")
        elif user_input == "bye":
            print("AI Agent: Goodbye! Have a great day.")
            break
        else:
            print("AI Agent: I am learning. Please try hello, help, or bye.")


if __name__ == "__main__":
    ai_agent()
