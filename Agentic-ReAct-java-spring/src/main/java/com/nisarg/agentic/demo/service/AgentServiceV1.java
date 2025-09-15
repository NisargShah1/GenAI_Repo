package com.nisarg.agentic.demo.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.nisarg.agentic.demo.gemini.GeminiClient;
import com.nisarg.agentic.demo.logging.AgentLogger;
import com.nisarg.agentic.demo.mcp.MCPClient;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Sinks;

import java.time.Duration;
import java.util.Map;

@Service
public class AgentServiceV1 {

    private final GeminiClient gemini;
    private final MCPClient mcp;
    private final AgentLogger agentLogger;
    private final ObjectMapper mapper = new ObjectMapper();

    public AgentServiceV1(GeminiClient gemini, MCPClient mcp, AgentLogger agentLogger) {
        this.gemini = gemini;
        this.mcp = mcp;
        this.agentLogger = agentLogger;
    }

    public Flux<String> chatStream(String userId, String prompt) {
        Sinks.Many<String> sink = Sinks.many().unicast().onBackpressureBuffer();

        new Thread(() -> {
            try {
                sink.tryEmitNext("LLM: preparing reasoning...");

                // 1) get tool list from MCP (name -> description)
                Map<String, String> tools = mcp.listTools(); // ensure MCPClient exposes this method

                // 2) ask Gemini for a JSON-formatted thought/action
                //without history
                String thoughtRaw = gemini.think(prompt, tools, null);
                agentLogger.log("llm_thought_raw", thoughtRaw);
                sink.tryEmitNext("🤔 " + (thoughtRaw.length() > 200 ? thoughtRaw.substring(0, 200) + "..." : thoughtRaw));

                // 3) parse Gemini's JSON output (thought/action/action_input/final_answer)
                JsonNode node;
                try {
                    thoughtRaw=thoughtRaw.replace("```json", "");
                    node = mapper.readTree(thoughtRaw);
                } catch (Exception e) {
                    // If parsing fails, treat whole response as thought text (no action)
                    sink.tryEmitNext("⚠️ Could not parse LLM JSON output, treating as thought text");
                    String fallbackThought = thoughtRaw;
                    sink.tryEmitNext("🤔 " + fallbackThought);
                    // Ask Gemini directly for an answer when JSON parsing fails:
                    String fallbackAnswer = gemini.respond(prompt, null);
                    sink.tryEmitNext("💡 Final Answer: " + fallbackAnswer);
                    sink.tryEmitComplete();
                    return;
                }

                String thought = node.path("thought").asText("");
                String action = node.path("action").asText("none");
                String actionInput = node.path("action_input").asText("");
                String finalAnswer = node.path("final_answer").asText(null);

                sink.tryEmitNext("🤔 Thought: " + thought);

                // 4) If model asked to call a tool:
                if (!"none".equalsIgnoreCase(action) && (finalAnswer == null || finalAnswer.isBlank())) {
                    sink.tryEmitNext("⚡ Action: " + action + " (input: " + actionInput + ")");

                    // Send tool call via MCP's /message endpoint; MCP server should post result back on SSE
                    String observation = mcp.callTool(action, actionInput);
                    sink.tryEmitNext("📥 Observation: " + observation);

                    // 5) Feed observation back to Gemini for final answer
                    String followup = gemini.respond(prompt, observation);
                    sink.tryEmitNext("💡 Final Answer: " + followup);
                } else if (finalAnswer != null && !finalAnswer.isBlank()) {
                    // Model already provided final answer
                    sink.tryEmitNext("💡 Final Answer: " + finalAnswer);
                } else {
                    // No action requested and no final answer -> fallback
                    String fallback = gemini.respond(prompt, null);
                    sink.tryEmitNext("💡 Final Answer: " + fallback);
                }

                sink.tryEmitComplete();
            } catch (Exception e) {
                sink.tryEmitNext("❌ Error: " + e.getMessage());
                sink.tryEmitComplete();
            }
        }).start();

        return sink.asFlux().delayElements(Duration.ofMillis(250));
    }
}
