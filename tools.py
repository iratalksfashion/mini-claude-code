"""
The Tools: Every tool that mini-claude possesses. 
"""
from pathlib import Path

# ---------- Tool functions (the actual python functions that run underneath) ---------- 
def read_file(path: str) -> str:
    """ Returns contents of a text file, or an error message. """
    try:
        return Path(path).read_text()
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except IsADirectoryError:
        return f"Error: {path} is a directory not a file"
    except UnicodeDecodeError:
        return f"Error: {path} is not a text file"

# ---------- Schemas (what Claude sees) ----------
TOOLS = [
    {
        "name": "read_file",
        "description": "Read a text file from user's project and return its contents. ",
        "input_schema": {
            "type": "object",
            "properties": {
                "path" : {
                    "type": "string",
                    "description" : "Path to the file, relative to the project folder",
                },
            },
            "required": ["path"],
        },
    },
]

# ---------- Registry: tool name → Python function ----------

""" Dictionary of all the tools available with Claude. tool name -> actual python function name. """
AVAILABLE_TOOLS = {
    "read_file": read_file,

}

def run_tool(tool_name: str, tool_input:dict) -> str:
    """ Runs the tool that claude asked for, without crashing. """
    func = AVAILABLE_TOOLS.get(tool_name) 
    if func is None:
        return f"mini Claude doesn't have this capability {tool_name}"
    try:
        return func(**tool_input)
    except TypeError as e:
        return f"Error: wrong inputs for {tool_name} : {e}"



 




    