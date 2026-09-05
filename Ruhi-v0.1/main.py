import os
from dotenv import load_dotenv
from google import genai


# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")

# Create Gemini client and chat session
client = genai.Client(api_key=api_key)
chat = client.chats.create(model="gemini-2.5-flash")


print("RUHI v0.1 is online!")
print("Type 'exit' to quit.\n")


while True:

    # Get message from user
    user_input = input("You: ")

    # Exit condition
    if user_input.lower() == "exit":
        print("\nRUHI: Goodbye!")
        break

    # Ignore empty messages
    if not user_input.strip():
        continue

    try:
        print("\nRUHI is thinking...\n")

        # Send message to Gemini
        response = chat.send_message(user_input)

        # Print Gemini's response
        print(f"RUHI: {response.text}\n")

    except Exception as e:
        print(f"\nError: {e}\n")