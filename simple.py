import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def currency_assistant(user_message, conversation_history=None):
    if conversation_history is None:
        conversation_history = []

    # Add the user's new message to the conversation
    conversation_history.append({"role": "user", "content": user_message})

    # Get initial response from the model
    response = client.responses.create(
        model="gpt-4o-mini",
        input=conversation_history,
    )

    return response.output_text, conversation_history
        


# Example usage
response, conversation = currency_assistant(
    "How much is 50 British pounds in Australian dollars?"
)
print("Assistant:", response)

# Continue the conversation
response, conversation = currency_assistant(
    "And what if I wanted to convert 200 Canadian dollars instead?", conversation
)
print("Assistant:", response)
