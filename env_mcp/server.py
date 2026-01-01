import os
import subprocess
from typing import Optional, List
from fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("EnvMCP")

class ShellHistory(BaseModel):
    shell: str
    history: List[str]
    last_exit_code: Optional[int] = None

class RuntimeHealth(BaseModel):
    python_version: str
    pip_packages: List[str]
    npm_packages: List[str]
    current_directory: str
    env_files: List[str]

class CommandExecution(BaseModel):
    command: str = Field(..., description="The command to execute")
    dry_run: bool = Field(True, description="If True, only returns the command without executing it")

@mcp.tool()
def capture_terminal_state(lines: int = 10) -> str:
    """Detects shell type and reads the last lines of history."""
    shell = os.environ.get("SHELL", "unknown")
    
    # Try to find history file
    hist_file = os.environ.get("HISTFILE")
    if not hist_file:
        home = os.path.expanduser("~")
        if "zsh" in shell:
            hist_file = os.path.join(home, ".zsh_history")
        elif "bash" in shell:
            hist_file = os.path.join(home, ".bash_history")
    
    history = []
    if hist_file and os.path.exists(hist_file):
        try:
            # Read last lines. Zsh history has some binary data sometimes, using errors='replace'
            with open(hist_file, "r", encoding="utf-8", errors="replace") as f:
                history = f.readlines()[-lines:]
        except Exception as e:
            history = [f"Error reading history: {str(e)}"]
    else:
        history = ["History file not found or HISTFILE not set."]

    return f"Shell: {shell}\nLast {len(history)} lines of history:\n" + "".join(history)

@mcp.tool()
def introspect_runtime() -> str:
    """Returns a Health Report of the current directory and runtime environment."""
    report = []
    
    # Python info
    try:
        python_path = subprocess.check_output(["which", "python3"], text=True).strip()
        python_version = subprocess.check_output(["python3", "--version"], text=True).strip()
        report.append(f"Python: {python_version} at {python_path}")
    except:
        report.append("Python: Not found")
    
    # Pip list (limited to first 20 for brevity)
    try:
        pip_list = subprocess.check_output(["pip", "list"], text=True).splitlines()[2:22]
        report.append("Pip Packages (partial): " + ", ".join([p.split()[0] for p in pip_list]))
    except:
        report.append("Pip: Failed to list packages")

    # Node info
    try:
        node_version = subprocess.check_output(["node", "--version"], text=True).strip()
        report.append(f"Node: {node_version}")
        npm_list = subprocess.check_output(["npm", "list", "--depth=0"], text=True).splitlines()[1:10]
        report.append("NPM Packages (partial): " + ", ".join(npm_list))
    except:
        report.append("Node/NPM: Not found or failed to list")

    # Local config files
    files = os.listdir(".")
    config_files = [f for f in files if f in [".env", "pyproject.toml", "package.json", "requirements.txt", "uv.lock"]]
    report.append(f"Current Directory: {os.getcwd()}")
    report.append(f"Config Files: {', '.join(config_files)}")

    return "\n".join(report)

@mcp.tool()
def secure_shell_executor(command: str, dry_run: bool = True) -> str:
    """Executes a fix command with a dry run safety layer."""
    if dry_run:
        return f"[DRY RUN] Would execute: {command}"
    
    try:
        # Basic validation to prevent some obvious disasters
        forbidden = [";", "&&", "||", "|", ">", "<", "`", "$("]
        # This is a very basic check, normally you'd want something more robust
        # But we are in a controlled agent environment.
        if any(char in command for char in forbidden):
             return f"Command blocked due to detected shell metacharacters: {command}"
        
        result = subprocess.run(command.split(), capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return f"Success:\n{result.stdout}"
        else:
            return f"Failure (Exit Code {result.returncode}):\n{result.stderr}"
    except Exception as e:
        return f"Error executing command: {str(e)}"

if __name__ == "__main__":
    mcp.run()
