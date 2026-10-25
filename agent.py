"""
The Agent: This is the loop that talks to Claude and makes sure to run tools until Claude is done. 

One call to run() can have multiple API calls.
user message -> Claude asks for a tool -> Agent calls the tool, returns the response -> .... -> final answer
"""
from context import Context
from tools import run_tool, TOOLS #the schema which talks to claude

MAX_STEPS = 20 #Safety limit, so that a confused agent doesn't loop forever

class Agent:

    def __init__(self, client, model_id: str, context: Context):
        self.client = client
        self.model_id = model_id
        self.context = context

    def run(self, user_text:str) -> str:
        """Handle one user message. Returns Claude's final text."""
        self.context.add_user(user_text)

        for step in range(MAX_STEPS):
            # Send the question to the Claude model via messages API call and wait for a reply
            response = self.client.messages.create(
                        model=self.model_id,
                        max_tokens=16000,
                        system=self.context.system_prompt,
                        messages=self.context.messages,
                        tools=TOOLS,
                    )

            self.context.add_assistant(response.content)

            if response.stop_reason == "end_turn":
                return self.__text(response)
            elif response.stop_reason == "max_tokens":
                return self.__text(response) + "\n[Reply was cut off due to max tokens limit reached]"
            else:
                # Run every tool Claude asked for, collecting the results
                results = []
                for block in response.content:
                    if block.type == "tool_use":
                        print(f"  🔧 {block.name}({block.input})")
                        output = run_tool(block.name, block.input)
                        results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": output
                            }
                        )
                self.context.add_tool_results(results)
        return "Stopped: too many steps."


    def __text(self, response) -> str:
        """Join all the text blocks in a response into one string. """
        return "\n".join(b.text for b in response.content if b.type == "text") 
        # The reply is a list of blocks, we'll print only the text ones.
        # for block in response.content:
        #     if block.type == "text":
        #         return "\n".join(block.text)
      