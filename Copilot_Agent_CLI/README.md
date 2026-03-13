# Copilot Agent CLI (Node.js)

This module implements an Autonomous Development Persona integrated with GitHub Copilot concepts. It acts as an autonomous CLI that interacts with different GitHub operations (PRs, commits) and manages an iterative implementation loop (understanding requirements, analyzing repos, creating strategies, searching the internet, testing, and fixing issues).

## Architecture
- `cli/`: Entry point for the CLI tool built with Commander (`index.js`).
- `personas/`: Definitions for various agents (e.g., `dev-agent.md`).
- `tools/`: Extensible tools to interact with Git, GitHub (via `@octokit/rest`), and Google Search.
- `mcp_server/`: Directory reserved for exposing these tools via the Model Context Protocol (MCP).

## How to use with GitHub Copilot

There are several ways to integrate this module with GitHub Copilot in your daily workflow:

### 1. Copilot Chat Persona Prompting (Workspace Context)
You can directly instruct GitHub Copilot Chat in your IDE (VS Code, IntelliJ) to adopt the persona and workflow defined in this repository. 
Simply open Copilot Chat and type:
> `@workspace Read the persona definition in Copilot_Agent_CLI/personas/dev-agent.md and adopt this persona. Now, [insert your requirement here, e.g., "Add caching to the GitHub tools"].`

Copilot will read the exact multi-step workflow, boundaries, and tool descriptions from the markdown file and execute its response following the strict iterative plan.

### 2. GitHub Copilot Extensions / MCP (Model Context Protocol)
Because the tools and CLI are modularized in Node.js, they are primed to be exposed as an **MCP Server**. Once wrapped in an MCP server (in the `mcp_server/` directory), GitHub Copilot can natively call the `github.js` and `search.js` functions directly from the chat interface without you needing to run the CLI manually. Copilot will invoke the tools, read the secrets from your local machine safely, and perform actions autonomously.

## Standalone CLI Usage

You can also run the agent as a standalone command-line tool.

### Setup
```bash
cd GenAI_Repo/Copilot_Agent_CLI
npm install
```

### Secret Management
The CLI requires API keys (GitHub, Google Search) to function. **You do not need to put them in `.env` files.**
When you run a command for the first time, the CLI will securely prompt you for missing keys and store them in `~/.copilot-agent-secrets.json` (with restricted permissions `0o600` so only your user account can read them).

### Running Commands
```bash
# Run the agent for a new feature implementation
node cli/index.js implement "Add caching to GitHub API calls"

# Run a specific persona for a specific task
node cli/index.js persona dev-agent "Add pagination to commit API"
```
