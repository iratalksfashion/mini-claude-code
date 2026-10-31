"""
The Tools: Every tool that mini-claude possesses. 

Each tool has 2 parts:
1. An actual python function that runs underneath and actually does the job.
2. The schema - This contains everything Claude sees. Claude returns just texts. With the help of this schema, it converts text to actual method name and parameters. 
"""
from pathlib import Path
from datetime import datetime

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

def list_files(path: str = ".") -> str:
    """ Return list of all files present in the given folder path. """
    IGNORED = {".git", "__pycache__", ".venv", "node_modules", ".DS_Store"}
    
    try:
        files = sorted(Path(path).iterdir(), key = lambda p: (p.is_file(), p.name.lower()))
    except FileNotFoundError:
        return f"Error: Directory not found: {path}"
    except NotADirectoryError:
        return f"Error: {path} is a file not a directory"
    lines = [p.name + "/" if p.is_dir() else p.name for p in files if p.name not in IGNORED]
    # lines = []
    # for p in entries:
    #     if p.name in IGNORED:
    #         continue
    #     lines.append(p.name + "/" if p.is_dir() else p.name)
    if not lines:
        return f"{path} is empty"
    return "\n".join(lines)

def get_current_time():
    """ Returns current time of the machine. """
    return datetime.now().strftime("%A %d %B %Y, %H:%M")




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
    {
        "name": "list_files",
        "description": "List all files and folders in a directory from user's project",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type" : "string",
                    "description" : "Path of the directory, relative to the project folder. Defaults to '.' (the project root).",
                },
            },
            "required" : [], #This is not required as Claude can request to view all files under project root folder too. 
        },
    },
    {
        "name": "get_current_time",
        "description": "Get current time of the machine.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required" : [],
        },
    },
]

# ---------- Registry: tool name → Python function ----------

""" Dictionary of all the tools available with Claude. tool name -> actual python function name. """
AVAILABLE_TOOLS = {
    "read_file": read_file,
    "list_files": list_files,
    "get_current_time": get_current_time,

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



 




    