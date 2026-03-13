# Copilot Agent CLI (Node.js)

This module implements an Autonomous Agent CLI integrated with GitHub Copilot concepts. It allows you to run specialized AI "personas" that interact with the local file system, GitHub, Gmail, and Google Search to perform complex workflows.

## Architecture
- `cli/`: Entry point for the CLI tool built with Commander (`index.js`).
- `personas/`: Markdown definitions for various agents (e.g., `dev-agent.md`, `email-assistant.md`, `orchestrator-agent.md`).
- `tools/`: Extensible tools for the agents to use (`github.js`, `gmail.js`, `search.js`, `orchestrator.js`, `gemini.js`, `config.js`).
- `mcp_server/`: Reserved for exposing these tools via the Model Context Protocol (MCP).

---

## 🚀 Setup & Initialization

### 1. Install Dependencies
```bash
cd GenAI_Repo/Copilot_Agent_CLI
npm install
```

### 2. Secret Management
The CLI requires various API keys depending on the persona being used. **You do not need to put them in `.env` files.** 
When you run a command for the first time, the CLI will securely prompt you for missing keys and store them in `~/.copilot-agent-secrets.json` (with restricted `0o600` permissions).
- **GitHub & Search**: Prompts for `GITHUB_TOKEN`, `GOOGLE_API_KEY`, `GOOGLE_SEARCH_ENGINE_ID`.
- **Gmail**: Prompts for `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN`.
- **Vertex AI (Gemini)**: Prompts for `GCP_PROJECT_ID`. Ensure you have authenticated using `gcloud auth application-default login`.

---

## 🤖 Supported Providers

The CLI supports both **GitHub Copilot** (via MCP/Extensions) and natively executing tasks using **Google Cloud Vertex AI (Gemini 1.5 Pro)**. 

To run an agent using Gemini Vertex AI, simply append the `-p vertex` or `--provider vertex` flag to your command. The CLI will load the persona as a system instruction and execute the task!

---

## 🎭 Available Personas & Scenarios

### 1. The Autonomous Development Engineer (`dev-agent`)
Behaves like a senior software engineer. It takes a requirement, understands the repo, plans changes, searches the web for documentation, implements code, writes tests, validates, and iterates until the requirement is satisfied.

**Scenario:** You need to add pagination to an existing API endpoint but don't want to write the boilerplate.
**Steps:**
1. Open your terminal in the CLI directory.
2. Run the agent natively using Gemini Vertex AI:
   ```bash
   node cli/index.js -p vertex implement "Add pagination to the commit listing API in tools/github.js"
   ```
3. Gemini will assume the `dev-agent` persona, read the repository context, plan the strategy, implement the code, and print the output step-by-step.

### 2. The Executive Email Assistant (`email-assistant`)
An autonomous assistant that manages your Gmail inbox. It reads unread emails, categorizes them, archives newsletters, and drafts replies to important messages. **It will never send an email without your explicit review.**

**Scenario:** You return from vacation and have 50 unread emails. You want the AI to organize them and draft replies to urgent client requests.
**Steps:**
1. Run the email assistant persona using Vertex AI:
   ```bash
   node cli/index.js -p vertex persona email-assistant "Please analyze my recent unread emails, organize them, and draft replies to anything urgent."
   ```
2. The CLI will prompt you for your Gmail OAuth credentials and `GCP_PROJECT_ID` if you haven't set them up.
3. The Gemini agent receives the `email-assistant` system instructions and outputs its action plan. (Note: Tool execution loops for Gemini require enabling Function Calling in `gemini.js`).

### 3. The Lead Agent Orchestrator (`orchestrator-agent`)
A meta-agent capable of decomposing massive tasks into smaller chunks. It dynamically designs specialized sub-agent personas (e.g., `db-expert`, `frontend-designer`), generates their `.md` files, and spawns them concurrently to solve the problem.

**Scenario:** You want to build a complete full-stack application from scratch, requiring different domains of expertise.
**Steps:**
1. Run the orchestrator with a high-level goal:
   ```bash
   node cli/index.js -p vertex persona orchestrator-agent "Build a full-stack login portal with a React frontend and a Node/Express backend."
   ```
2. Gemini acts as the meta-agent, analyzing the request and writing two new personas to the `personas/` folder: `react-expert.md` and `node-expert.md`.
3. It uses the `spawnSubAgent` tool to launch both agents in the background.
4. You will see prefixed logs in your terminal as the sub-agents work.
5. The orchestrator waits for them to finish, synthesizes their outputs, and presents the final unified application.

---

## 🔧 How to use with GitHub Copilot

### 1. Copilot Chat Persona Prompting (Workspace Context)
You can directly instruct GitHub Copilot Chat in your IDE (VS Code, IntelliJ) to adopt any persona defined in this repository. 
Simply open Copilot Chat and type:
> `@workspace Read the persona definition in Copilot_Agent_CLI/personas/email-assistant.md and adopt this persona. Now, [insert your specific task here].`

Copilot will read the exact multi-step workflow, boundaries, and tool descriptions from the markdown file and execute its response following the strict plan.

### 2. GitHub Copilot Extensions / MCP (Model Context Protocol)
Because the tools and CLI are modularized in Node.js, they are primed to be exposed as an **MCP Server**. Once configured, GitHub Copilot can natively call `github.js`, `search.js`, `gmail.js`, and `orchestrator.js` directly from the chat interface. Copilot will invoke the tools, read the secrets safely from your local machine, and perform actions autonomously without you needing to run the CLI manually.
