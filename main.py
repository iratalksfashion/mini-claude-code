"""
Main entry point for mini claude code.
"""

import anthropic
from dotenv import load_dotenv
from model import get_model, DEFAULT_MODEL


def main():
    load_dotenv()  # Load environment variables from .env file
    client = (
        anthropic.Anthropic()
    )  # finds Anthropic API key in environment variables automatically

    model_id = get_model(DEFAULT_MODEL)

    messages = []

    while True:
        question = input("Enter your question: ")

        messages.append({"role": "user", "content": question})
        # Send the question to the Claude model via messages API call and wait for a reply
        response = client.messages.create(
            model=model_id,
            max_tokens=16000,
            messages=messages,
        )

        # print the entire response with all different kinds of blocks.
        # print(response)

        messages.append({"role": "assistant", "content": response.content})

        # The reply is a list of blocks, we'll print only the text ones.
        for block in response.content:
            if block.type == "text":
                print(f"Claude: {block.text}")


if __name__ == "__main__":
    main()
