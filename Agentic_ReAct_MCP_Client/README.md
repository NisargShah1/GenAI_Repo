# 🌐 Agentic React MCP Client

This project demonstrates an **Agentic Client** built with **LangChain + LangGraph + MCP (Model Context Protocol)**.  
It connects to an MCP Server, retrieves available tools, and orchestrates **multi-step tool calls** using an **LLM (Gemini)**.

---

## 🚀 Features

### Available MCP Tools

#### 🌦️ getCurrentWeather  
📍 **Description**: Get the current weather for a specific location.  
🔑 **Input**:
```json
{
  "location": "city name in string format"
}
```
### 📧 sendEmail
📍 **Description:** Send an email.
🔑 **Input:**

```json
{
  "recipient": "email Id of recipient in string format",
  "subject": "subject of email in string",
  "body": "email body in string format"
}
```
Agentic Orchestration with LangGraph
Supports multi-tool workflows (e.g., fetch weather → send email).

Explicit control over execution graph (not just LLM free-form reflection).

Handles retries, ordering, and state transitions cleanly.

### 🏗️ Architecture
Frontend: Agentic UI

Agentic Logic: LangGraph (multi-step orchestration)

LLM: Gemini (gemini-2.0-flash or Any othe LLM model)

MCP Client: Connects to MCP Server via SSE

MCP Tools: Weather + Email

### 🔧 Example Workflows
🌀 Example 1: Multi-Tool Call
```
Query:
What is the weather in Pune? Send email of weather details to nisarg.shah84@gmail.com
Execution Trace:

Action: getCurrentWeather
Action Input: {"location": "Pune"}
Observation: "The current temperature in Pune is 27°C."

Action: sendEmail

Action Input: {"recipient": "nisarg.shah84@gmail.com", "subject": "Weather details", "body": "The current temperature in Pune is 27°C."}

Observation: "Email sent to: nisarg.shah84@gmail.com with message:The current temperature in Pune is 27°C."

✅ Final Answer:
The current temperature in Pune is 27°C.
The weather details have been sent to nisarg.shah84@gmail.com.
```

### 🌀 Example 2: LLM + Tool Mix

```
Query:
What is the capital of India? Send it to my email.
Execution Trace:

LLM: The capital of India is New Delhi.

Action: sendEmail
Action Input: {"recipient": "nisarg.shah84@gmail.com","subject":"Capital of India", "body": "The capital of India is New Delhi."}
Observation: "Email sent to: nisarg.shah84@gmail.com with message:The capital of India is New Delhi."

✅ Final Answer:
The capital of India is New Delhi.
An email with this information has been sent to nisarg.shah84@gmail.com.
```
### 🔄 LangGraph Flow
Node 1: Gemini LLM (parse query, plan steps)

Node 2: Call MCP tool (getCurrentWeather / sendEmail)

Loop: until LLM signals final answer

State includes:

query

history

next_action

final_answer

✔️ Naturally handles multi-tool chaining (weather → email).

### 🖥️ MCP Server Example
(Tools exposed by this MCP server)
Tools:
getCurrentWeather
sendEmail

https://github.com/NisargShah1/GenAI_Repo/tree/main/Spring_Ai_MCP_Server