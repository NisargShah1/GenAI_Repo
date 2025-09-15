Set env variables:

export GEMINI_API_KEY="your_api_key"
export GEMINI_MODEL="gemini-pro"


Build & run:

mvn clean package
java -jar target/agentic-react-java-graph-spring-mcp-sse-1.0.0.jar

Test streaming:

curl -N -X POST http://localhost:8080/api/chat/stream \
-H "Content-Type: application/json" \
-d '{"userId":"u1","prompt":"What is the weather in Pune tomorrow?"}'


You’ll see step-by-step SSE messages like:

data: 🤔 LLM Thought: analyzing query...
data: 🤔 I should use the weather tool.
data: ⚡ Action: call weather tool via MCP
data: 📥 Observation: ☀️ Sunny, 28°C
data: 💡 Final Answer: The weather in Pune is Sunny, 28°C

Query where LLM uses tools:
![img.png](doc/img.png)

Query where LLM does not use tools:
![img.png](doc/llm_call_tool_not_required.png)