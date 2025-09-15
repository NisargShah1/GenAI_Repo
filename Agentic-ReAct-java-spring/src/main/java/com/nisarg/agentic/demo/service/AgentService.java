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
import java.util.*;

@Service
public class AgentService {

    private final GeminiClient gemini;
    private final MCPClient mcp;
    private final AgentLogger agentLogger;
    private final ObjectMapper mapper = new ObjectMapper();
    private final int MAX_STEPS = 6;

    public AgentService(GeminiClient gemini, MCPClient mcp, AgentLogger agentLogger) {
        this.gemini = gemini;
        this.mcp = mcp;
        this.agentLogger = agentLogger;
    }

    public Flux<String> chatStream(String userId, String prompt) {
        Sinks.Many<String> sink = Sinks.many().unicast().onBackpressureBuffer();

        new Thread(() -> {
            try {
                sink.tryEmitNext("🚀 Start: processing query -> " + prompt);

                // 1) get tool list from MCP (name -> description)
                Map<String, String> tools = Optional.ofNullable(mcp.listTools())
                        .orElse(Collections.emptyMap());

                List<Map<String, String>> history = new ArrayList<>();
                String finalAnswer = null;

                // 2) Step loop (LangGraph style)
                for (int step = 0; step < MAX_STEPS; step++) {
                    sink.tryEmitNext("Step " + step);

                    // Build context from previous tool calls
                    StringBuilder contextBuilder = new StringBuilder();
                    for (Map<String, String> h : history) {
                        contextBuilder.append("Action: ").append(h.get("action"))
                                .append(", Input: ").append(h.get("actionInput"))
                                .append(", Observation: ").append(h.get("observation"))
                                .append("\n");
                    }
                    String context = contextBuilder.toString();

                    // Ask Gemini what to do next
                    String thoughtRaw = gemini.think(prompt, tools, context);
                    agentLogger.log("llm_thought_raw", thoughtRaw);

                    JsonNode node;
                    try {
                        thoughtRaw = thoughtRaw.replace("```json", "").replace("```", "");
                        node = mapper.readTree(thoughtRaw);
                    } catch (Exception e) {
                        sink.tryEmitNext("⚠Could not parse LLM JSON, fallback to direct response");
                        finalAnswer = gemini.respond(prompt, context);
                        sink.tryEmitNext("Final Answer: " + finalAnswer);
                        break;
                    }

                    String thought = node.path("thought").asText("");
                    String action = node.path("action").asText("none");
                    String actionInput = node.path("action_input").asText("");
                    finalAnswer = node.path("final_answer").asText(null);

                    sink.tryEmitNext("Thought: " + thought);

                    if (finalAnswer != null && !finalAnswer.trim().isEmpty()) {
                        sink.tryEmitNext("Final Answer: " + finalAnswer);
                        break;
                    }

                    if (!"none".equalsIgnoreCase(action)) {
                        sink.tryEmitNext("Action: " + action + " (input: " + actionInput + ")");

                        String observation;
                        try {
                            observation = mcp.callTool(action, actionInput);
                        } catch (Exception ex) {
                            observation = "Tool execution failed: " + ex.getMessage();
                        }

                        sink.tryEmitNext("Observation: " + observation);

                        // Record in history
                        Map<String, String> stepRecord = new HashMap<>();
                        stepRecord.put("action", action);
                        stepRecord.put("actionInput", actionInput);
                        stepRecord.put("observation", observation);
                        history.add(stepRecord);

                        continue; // loop again
                    }

                    // If no tool and no final answer -> fallback
                    finalAnswer = gemini.respond(prompt, context);
                    sink.tryEmitNext("Final Answer: " + finalAnswer);
                    break;
                }

                if (finalAnswer == null || finalAnswer.trim().isEmpty()) {
                    sink.tryEmitNext("Could not resolve query after max steps.");
                }

                sink.tryEmitNext("End.");
                sink.tryEmitComplete();

            } catch (Exception e) {
                sink.tryEmitNext("Error: " + e.getMessage());
                sink.tryEmitComplete();
            }
        }).start();

        return sink.asFlux().delayElements(Duration.ofMillis(250));
    }
}
