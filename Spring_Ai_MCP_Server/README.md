MCP Client + Spring AI Server

This project demonstrates how to build a Model Context Protocol (MCP) client and server using Java 21 and Spring AI.

The server exposes tools via MCP, while the client can consume them and interact with an LLM (e.g., Gemini, OpenAI, etc.) to perform actions.

✨ Features

Spring AI MCP Server exposing tools:

📍 getCurrentWeather → Fetches current weather for a given city.

📧 sendEmail → Sends an email with recipient, subject, and body.

MCP Client that connects to the server over SSE and invokes tools.

Built on Java 21, Spring Boot 3.x, and Spring AI.

⚡ Prerequisites

Java 21+

Maven or Gradle

Spring Boot 3.x

🚀 Getting Started
1. Clone the repo
   git clone https://github.com/your-org/mcp-client-spring-ai.git
   cd mcp-client-spring-ai

2. Run the MCP Server

The MCP server is a Spring Boot application exposing tools.

Example tools:

@Tool(description = """
Get the current weather for a specific location.
input params:
location: city name in string format
""")
public String getCurrentWeather(String location) {
// Implementation here...
return "Weather in " + location + " is Sunny 25°C";
}

@Tool(description = """
Send Email.
input params:
recipient: email Id of recipient in string format
subject: subject of email in string
body: email body in string format
""")
public String sendEmail(String recipient, String subject, String body) {
// Implementation to send email
return "Email sent to " + recipient;
}


Run the server:

./mvnw spring-boot:run


The server will start and expose MCP endpoints over SSE (/mcp/sse).

3. Run the MCP Client

The client connects to the MCP server, lists tools, and invokes them based on LLM reasoning.

Example (Python client with LangChain):

agent.run("What is the weather in New York? Use tools if available.")


The client calls getCurrentWeather tool automatically.

📚 Using Spring AI for MCP Server

Spring AI makes it easy to define MCP-compatible tools:

Annotate Java methods with @Tool.

Each @Tool method is automatically exposed as an MCP tool.

Input parameters are derived from method arguments.

Descriptions help the LLM decide when to call the tool.

Pointers:

Annotations drive tool discovery
Use @Tool(description = "...") to expose methods as MCP tools.

Schemas generated automatically
Spring AI builds JSON schema from method signatures.

LLM agent orchestration
You can connect the MCP server to Gemini, OpenAI, or other LLMs.

Security & Auth
If exposing email or external APIs, add authentication and authorization to your MCP endpoints.

📌 Example Use Cases

Weather Assistant:
Ask: “What’s the weather in Pune?” → MCP client calls getCurrentWeather.

Email Assistant:
Ask: “Send an email to john@example.com
with subject ‘Meeting’ and body ‘Let’s sync tomorrow.’”
→ MCP client calls sendEmail.

🛠️ Next Steps

Add more tools (e.g., calendar scheduling, file operations).

Deploy MCP server to Kubernetes or Docker.

Integrate with Spring Security for authenticated tool calls.

Connect MCP client to UI (chatbot or frontend).

Example of MCP client in python using Langchain or LangGraph:
https://github.com/NisargShah1/GenAI_Repo/Agentic_ReAct_MCP_Client