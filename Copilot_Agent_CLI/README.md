# Copilot Agent CLI (Node.js)

This module implements an Autonomous Development Persona integrated with GitHub Copilot concepts. It acts as an autonomous CLI that interacts with different GitHub operations (PRs, commits) and manages an iterative implementation loop (understanding requirements, analyzing repos, creating strategies, testing, and fixing issues).

## Architecture
- `cli/`: Entry point for the CLI tool built with Commander (`index.js`).
- `personas/`: Definitions for various agents (e.g., `dev-agent.md`).
- `tools/`: Extensible tools to interact with Git and GitHub (using `@octokit/rest`).
- `mcp_server/`: Integrations for MCP clients to use these workflows.

## Features
- Interprets user requirements iteratively.
- Creates implementation plans.
- Writes and executes tests.
- Evaluates and fixes bugs until validation succeeds.
- Ask questions if clarification is needed.

## Quickstart

```bash
cd GenAI_Repo/Copilot_Agent_CLI
npm install

# Run the agent for a new feature implementation
node cli/index.js implement "Add caching to GitHub API calls"

# Run a specific persona for a specific task
node cli/index.js persona dev-agent "Add pagination to commit API"
```
