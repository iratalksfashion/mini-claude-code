"""
Main entry point for mini claude code.
"""

import anthropic
from dotenv import load_dotenv
from model import get_model, DEFAULT_MODEL
from context import Context 
from agent import Agent

def main():
    load_dotenv()  # Load environment variables from .env file
    client = (
        anthropic.Anthropic()
    )  # finds Anthropic API key in environment variables automatically

    model_id = get_model(DEFAULT_MODEL)
    model_context = Context()  # Holds system prompt + Conversation History
    agent = Agent(client, model_id, model_context)
    print("Welcome to Mini Claude Code. Type /clear to erase, exit to quit")
    while True:
        question = input("Enter your question: ").strip()
        if question.lower() in ("exit", "quit"):
            break
        if (
            not question
        ):  # covers empty question scenario. Reads as "if question is empty"
            continue
        if question == "/clear":
            model_context.clear()
            print("Conversation Cleared")
            continue

        try:
            answer = agent.run(question)
        except anthropic.AuthenticationError:
            print("Error: your API key is rejected. Check .env")
        except anthropic.APIConnectionError:
            print("Error: can't reach the API. Check your internet connection.")
        except anthropic.APIStatusError as e:
            print(f"API Error: {e.status_code}: {e.message}")
        else:
            print(f"Claude: {answer}")

if __name__ == "__main__":
    main()
