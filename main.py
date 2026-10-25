"""
Main entry point for mini claude code.
"""

import anthropic
from dotenv import load_dotenv
from model import get_model, DEFAULT_MODEL
from context import Context


def main():
    load_dotenv()  # Load environment variables from .env file
    client = (
        anthropic.Anthropic()
    )  # finds Anthropic API key in environment variables automatically

    model_id = get_model(DEFAULT_MODEL)
    model_context = Context()  # Holds system prompt + Conversation History

    print("Welcome to Mini Claude Code. Type /clear to erase, exit to quit")
    while True:
        question = input("Enter your question: ").strip()
        if question.lower() in ("exit", "quit"):
            break
        if (
            not question
        ):  # covers empty question scenario. Reads as "if question is empty"
            break
        if question == "/clear":
            model_context.clear()
            print("Conversation Cleared")
            continue

        model_context.add_user(question)

        # Send the question to the Claude model via messages API call and wait for a reply
        response = client.messages.create(
            model=model_id,
            max_tokens=16000,
            system=model_context.system_prompt,
            messages=model_context.messages,
        )

        # print the entire response with all different kinds of blocks.
        # print(response)

        model_context.add_assistant(response.content)

        # The reply is a list of blocks, we'll print only the text ones.
        for block in response.content:
            if block.type == "text":
                print(f"Claude: {block.text}")


if __name__ == "__main__":
    main()
