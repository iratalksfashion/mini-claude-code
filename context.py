"""
The context: Contains system prompt (aka gives the agent personality) + it ensures that the agent
knows and remembers the full conversation (aka memory of previous chat sessions)

"""

DEFAULT_SYSTEM_PROMPT = (
    "You are Mini Claude, a helpful coding agent running in a terminal. "
    "Keep your answers short and clear."
)

# CHARACTER_SYSTEM_PROMPT = (
#     "You are Mini Claude with personality of Barney from How I met Mother show."
#     "Keep your answers accurate, short and "
# )


class Context:
    def __init__(self, system_prompt: str = DEFAULT_SYSTEM_PROMPT):
        # Save the prompt on the object so that other methods (agent.py) can read it
        self.system_prompt = system_prompt
        # Conversation starts empty. This is a list of dicts, each element is {"role": "..", "content": ".."}
        self.messages = []

    def add_user(self, content: str):
        # Adds user's last message
        self.messages.append({"role": "user", "content": content})

    def add_assistant(self, content: list):
        # Adds assistant's last message
        self.messages.append({"role": "assistant", "content": content})

    def add_tool_results(self, content: list):
        # Adds tool's result. The API only has 2 roles: user and assistant. It doesn't differentiate whether something is
        # coming from actual user (user input etc) or some tool call.
        self.messages.append({"role": "user", "content": content})

    def clear(self) -> None:
        # Clears all past conversation history (the system prompt remains)
        self.messages.clear()

    def __len__(self):
        return len(self.messages)

    def __repr__(self):
        print("Context" + len(self) + "messages")
