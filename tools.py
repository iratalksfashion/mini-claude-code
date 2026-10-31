"""
The Tools: Every tool that mini-claude possesses.

Each tool has 2 parts:
1. An actual python function that runs underneath and actually does the job. Every function returns str for Claude to see/use.
2. The schema - This contains everything Claude sees. Claude returns just texts. With the help of this schema, it converts text to actual method name and parameters.
"""

import subprocess
from pathlib import Path
from datetime import datetime
from guardrails import PROJECT_ROOT

BASH_TIMEOUT_SECONDS = 30  # a command running longer than this gets stopped


# ---------- Tool functions (the actual python functions that run underneath) ----------
def read_file(path: str) -> str:
    """Returns contents of a text file, or an error message."""
    try:
        return Path(path).read_text()
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except IsADirectoryError:
        return f"Error: {path} is a directory not a file"
    except UnicodeDecodeError:
        return f"Error: {path} is not a text file"


def list_files(path: str = ".") -> str:
    """Return list of all files present in the given folder path."""
    IGNORED = {".git", "__pycache__", ".venv", "node_modules", ".DS_Store"}

    try:
        files = sorted(
            Path(path).iterdir(), key=lambda p: (p.is_file(), p.name.lower())
        )
    except FileNotFoundError:
        return f"Error: Directory not found: {path}"
    except NotADirectoryError:
        return f"Error: {path} is a file not a directory"
    lines = [
        p.name + "/" if p.is_dir() else p.name for p in files if p.name not in IGNORED
    ]
    # lines = []
    # for p in entries:
    #     if p.name in IGNORED:
    #         continue
    #     lines.append(p.name + "/" if p.is_dir() else p.name)
    if not lines:
        return f"{path} is empty"
    return "\n".join(lines)


def get_current_time():
    """Returns current time of the machine."""
    return datetime.now().strftime("%A %d %B %Y, %H:%M")


def write_file(path: str, input_content: str) -> str:
    """Create a file, or overwrite it completely with the given input content"""
    file = Path(path)
    try:
        file.parent.mkdir(parents=True, exist_ok=True)  # creates missing folders
        chars = file.write_text(input_content)  # returns number of chracters written
    except IsADirectoryError:
        return f"Error: {path} This is a directory not a file"
    except OSError as e:
        return f"Error: couldn't write {path}: {e}"
    return f"Wrote {chars:,} characters to {path}"


def edit_file(path: str, old_text: str, new_content: str) -> str:
    """Edit one part of the given file with the given content.
    old text must appear exactly ones"""
    if not old_text:
        return "Error: old_text can't be empty. Use write_file to create a new file."
    file = Path(path)
    try:
        text = file.read_text()
    except FileNotFoundError:
        return f"Error: File not found {path}"
    except IsADirectoryError:
        return f"Error: {path} is a directory not a file"
    except UnicodeDecodeError:
        return f"Error: {path} is not a text file"

    count = text.count(old_text)  # checks how many times old_text appears in text
    if count == 0:
        return f"Error: old_text not found in {path}. Read the file first and copy the text exactly."
    if count > 1:
        return f"Error: old_text appears {count} times in {path}. Include more surrounding lines so it matches exactly once. "

    file.write_text(text.replace(old_text, new_content, 1))
    return f"Edited {path}"


def run_bash(command: str) -> str:
    """Run a shell command in the project folder and returns its output."""
    try:
        result = subprocess.run(
            command,
            shell=True,  # lets us pass one string like "ls -la"
            capture_output=True,  # collect output instead of printing it
            text=True,  # strings, not bytes
            timeout=BASH_TIMEOUT_SECONDS,
            cwd=PROJECT_ROOT,  # always run inside the project
        )
    except subprocess.TimeoutExpired:
        return f"Error: Timed out after {BASH_TIMEOUT_SECONDS} seconds: {command}"
    parts = []
    if result.stdout:
        parts.append(result.stdout.rstrip())
    if result.stderr:
        parts.append(
            f"[stderr]\n{result.stderr.rstrip()}"
        )  # stderr label allows claude to see that this is different than stdout
    parts.append(
        f"[exit code {result.returncode}]"
    )  # always present so the result is never empty
    return "\n".join(parts)


# ---------- Schemas (what Claude sees) ----------
TOOLS = [
    {
        "name": "read_file",
        "description": "Read a text file from user's project and return its contents. ",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file, relative to the project folder",
                },
            },
            "required": ["path"],
        },
    },
    {
        "name": "list_files",
        "description": "List all files and folders in a directory from user's project",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path of the directory, relative to the project folder. Defaults to '.' (the project root).",
                },
            },
            "required": [],  # This is not required as Claude can request to view all files under project root folder too.
        },
    },
    {
        "name": "get_current_time",
        "description": "Get current time of the machine.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "write_file",
        "description": "Create a file and OVERWRITE it completely with the given text. "
        "If the parent folder doesn't exist, it will create one. "
        "For small changes in existing file, use edit_file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file, relative to the project folder",
                },
                "input_content": {
                    "type": "string",
                    "description": "Content to be added in the file",
                },
            },
            "required": ["path", "input_content"],
        },
    },
    {
        "name": "edit_file",
        "description": "Replace an exact piece of text in an existing file. old_text must match "
        "the file exactly (including spaces) and appear exactly once. "
        "Read the file first.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file, relative to the project folder",
                },
                "old_text": {
                    "type": "string",
                    "description": "The exact text in the existing file which will be overwritten",
                },
                "new_content": {
                    "type": "string",
                    "description": "Content to be added in the file",
                },
            },
            "required": ["path", "old_text", "new_content"],
        },
    },
    {
        "name": "run_bash",
        "description": "Run a shell command in the project folder and return stdout, stderr ",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to run, e.g. 'python playground/hello.py'r",
                },
            },
            "required": ["command"],
        },
    },
]

# ---------- Registry: tool name → Python function ----------

""" Dictionary of all the tools available with Claude. tool name -> actual python function name. """
AVAILABLE_TOOLS = {
    "read_file": read_file,
    "list_files": list_files,
    "get_current_time": get_current_time,
    "write_file": write_file,
    "edit_file": edit_file,
    "run_bash": run_bash,
}


def run_tool(tool_name: str, tool_input: dict) -> str:
    """Runs the tool that claude asked for, without crashing."""
    func = AVAILABLE_TOOLS.get(tool_name)
    if func is None:
        return f"mini Claude doesn't have this capability {tool_name}"
    try:
        return func(**tool_input)
    except TypeError as e:
        return f"Error: wrong inputs for {tool_name} : {e}"
