# EnvMCP

EnvMCP is a Model Context Protocol (MCP) server designed to assist with environment introspection, terminal state capture, and secure shell execution. It provides a set of tools for AI agents to safely interact with and diagnose the local development environment.

## Features

EnvMCP exposes the following tools via the MCP protocol:

- **`capture_terminal_state`**: Detects the current shell type and retrieves recent command history.
- **`introspect_runtime`**: Generates a comprehensive health report of the runtime environment, including:
  - Python version and path
  - Installed Pip packages (partial list)
  - Node.js and NPM versions (if available)
  - Local configuration files presence (e.g., `.env`, `pyproject.toml`)
- **`secure_shell_executor`**: Safely executes shell commands. Includes a dry-run mode and basic validation to prevent accidental execution of dangerous shell metacharacters.
- **`read_error_file`**: efficient reading of log files, capable of handling large files by reading the tail end.

## Installation

This project is managed with `uv`. To install dependencies:

```bash
uv sync
```

Alternatively, you can install the requirements using pip:

```bash
pip install -r requirements.txt
```

## Usage

To start the MCP server:

```bash
python -m env_mcp.server
```

Or run it directly as a script:

```bash
python env_mcp/server.py
```

## Dependencies

- `fastmcp`
- `pydantic`
- `python-dotenv`
- `langchain` ecosystem libraries