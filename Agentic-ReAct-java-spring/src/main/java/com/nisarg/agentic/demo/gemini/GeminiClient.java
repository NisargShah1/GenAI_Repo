package com.nisarg.agentic.demo.gemini;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.genai.Client;
import com.google.genai.types.GenerateContentResponse;
import org.springframework.stereotype.Component;

import java.util.Map;

@Component
public class GeminiClient {
    private static final String API_KEY = System.getenv("GEMINI_API_KEY");
    private static final String MODEL = System.getenv().getOrDefault("GEMINI_MODEL", "gemini-pro");
    private static final String ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/"
            + MODEL + ":generateContent?key=" + API_KEY;
    private final ObjectMapper mapper = new ObjectMapper();


    /**
     * New think() that receives a map of available tools (name -> description)
     * and includes them in the prompt provided to Gemini.
     *
     * The model is instructed to return only valid JSON with fields:
     *   { "thought": "...", "action": "toolName|none", "action_input":"...", "final_answer":"..." }
     */
    public String think(String query, Map<String, String> tools, String context) {
        StringBuilder toolsDesc = new StringBuilder();
        if (tools != null && !tools.isEmpty()) {
            toolsDesc.append("Available tools (name: description). Use these when needed:\n");
            for (Map.Entry<String, String> e : tools.entrySet()) {
                toolsDesc.append("- ").append(e.getKey());
                if (e.getValue() != null && !e.getValue().isBlank()) {
                    toolsDesc.append(": ").append(e.getValue());
                }
                toolsDesc.append("\n");
            }
        } else {
            toolsDesc.append("Available tools: none\n");
        }

        StringBuilder contextDesc = new StringBuilder();
        if (context != null && !context.isBlank()) {
            contextDesc.append("Previous steps and observations:\n").append(context).append("\n");
        } else {
            contextDesc.append("No previous steps.\n");
        }

        String systemInstruction = """
        You are an agent that follows the ReAct pattern (Reason -> Act -> Observe -> Repeat).
        You MUST output ONLY valid JSON (no explanatory text) with these fields:
        {
          "thought": "<brief thought about what to do next>",
          "action": "<tool name to call, or \\"none\\">",
          "action_input": "<JSON string input for the tool. Take input parameters from the tool description. If action is \\"none\\", leave this empty.>",
          "final_answer": "<final answer if ready, otherwise empty>"
        }
        If you decide a tool call is required, set action to the tool name and action_input appropriately.
        If no tool is required and you can answer, set action to "none" and fill final_answer.
        """;

        String prompt = systemInstruction
                + "\n\n" + toolsDesc
                + "\n" + contextDesc
                + "\nUser query: " + query;

        return callGemini(prompt);
    }


    private String callGemini(String prompt) {
        Client client = Client.builder()
                .apiKey(API_KEY)
                .build();

        // Then use client.models.generateContent(...) etc.
        GenerateContentResponse resp = client.models.generateContent("gemini-2.0-flash", prompt, null);

        return resp.text();
    }

    /**
     * Reuse existing respond() if you have one; otherwise you can call think() with
     * a modified prompt or implement respond() similarly. If you already had respond(), keep it.
     */
    public String respond(String query, String context) {
        String prompt = "User query: " + query;
        if (context != null && !context.isBlank()) {
            prompt += "\nTool observation: " + context;
        }
        // We request a plain text answer in this case
        String system = "You are an assistant. Provide a concise, user-facing final answer in plain text.";
        return callGemini(system + "\n\n" + prompt);
    }
}
