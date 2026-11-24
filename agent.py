def ai_agent():
    print("Welcome to Raghu AI Agent!")
    print("---------------------------")

    while True:
        user_input = input("You: ").lower()

        if user_input == "hello":
            print("AI Agent: Hello Raghu! How can I help you?")

        elif user_input == "help":
            print("AI Agent: I can answer simple questions.")

        elif user_input == "bye":
            print("AI Agent: Goodbye! Have a great day.")
            break

        else:
            print("AI Agent: I am learning. Please try hello, help, or bye.")


if _name_ == "_main_":
    ai_agent()
