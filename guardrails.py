"""
Guardrails: This runs before ANY tool runs.

It protects us from our agent doing any dangerous things eg deleting all files on the system, write publicly on our behalf, etc.
This file is responsible for keeping the human in loop with (y/n)
The model proposes, and this file approves that proposal.
check() returns None if model's proposal is allowed, and error if its not allowed.

"""

from pathlib import Path

PROJECT_ROOT = Path.cwd().resolve()  # root folder where project is running.
BLOCKED_FILES = {".env", ".git"}
NEEDS_APPROVAL = {"write_file", "edit_file", "run_bash"}
DANGEROUS_COMMANDS = ["rm -rf", "sudo", "mkfs", "shutdown", "> /dev /", "chmod -R 777"]
MAX_OUTPUT_CHARS = 10_000
MAX_PREVIEW_CHARS = 300  # how much of each input to show in the approval prompt


def is_dangerous_command(command: str) -> bool:
    lowered = command.lower()
    return any(pattern in lowered for pattern in DANGEROUS_COMMANDS)


def is_safe_path(path: str) -> bool:
    resolved_path = Path(path).resolve()

    if not resolved_path.is_relative_to(PROJECT_ROOT):
        return False  # outside the project folder

    inside_parts = resolved_path.relative_to(
        PROJECT_ROOT
    ).parts  # e.g. ("playground", "notes.txt")
    return not any(part in BLOCKED_FILES for part in inside_parts)


def ask_permission(tool_name: str, tool_input: dict) -> bool:
    """Show the user what's about to happen and ask y/n."""
    print(f"\n⚠️  Claude wants to run {tool_name}")
    for key, value in tool_input.items():
        text = str(value)
        if len(text) > MAX_PREVIEW_CHARS:
            text = text[:MAX_PREVIEW_CHARS] + "...."
        print(f" {key}: {text}")
    answer = input("Allow?(y/n) ").strip().lower()
    return answer == "y"


def tool_check(tool_name: str, tool_input: dict) -> str | None:
    """Checks whether this Tool is safe to use.
    Return None if the call is allowed, or an 'Error: ...' message if not."""
    path = tool_input.get("path")
    if path is not None:
        if not isinstance(path, str) or not is_safe_path(path):
            return (
                f"Error: access denied for '{path}'. Only files inside the project "
                "folder are allowed, and .env and .git are off-limits."
            )

    if tool_name == "run_bash":
        command = tool_input.get("command", "")
        if is_dangerous_command(command):
            return f"Error: This command is blocked for safety: {command}"

    if tool_name in NEEDS_APPROVAL and not ask_permission(tool_name, tool_input):
        return f"Error: the user declined this action. Ask them what they'd like to do instead."

    return (
        None  # means tool_check has no Error to produce, and claude can run the tool.
    )


def trim_output(text: str) -> str:
    """Cut very long tool output so it can't flood the context."""
    if len(text) < MAX_OUTPUT_CHARS:
        return text
    cut = len(text) - MAX_OUTPUT_CHARS
    return text[:MAX_OUTPUT_CHARS] + f"\n[...truncated {cut:,} more characters]"
