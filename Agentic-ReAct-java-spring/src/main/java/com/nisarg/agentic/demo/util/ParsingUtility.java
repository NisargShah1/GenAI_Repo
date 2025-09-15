package com.nisarg.agentic.demo.util;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

public class ParsingUtility {

    private static final ObjectMapper mapper = new ObjectMapper();

    public static String extractResult(String json) {
        if (json == null || json.trim().isEmpty()) {
            return null;
        }

        try {
            JsonNode root = mapper.readTree(json);
            JsonNode contentNode = root.path("result").path("content");

            if (contentNode.isArray() && !contentNode.isEmpty()) {
                StringBuilder sb = new StringBuilder();

                for (JsonNode item : contentNode) {
                    JsonNode textNode = item.path("text");
                    if (textNode != null && !textNode.isMissingNode()) {
                        String text = textNode.asText();

                        // Remove wrapping quotes if present
                        if (text.startsWith("\"") && text.endsWith("\"") && text.length() > 1) {
                            text = text.substring(1, text.length() - 1);
                        }

                        if (!text.isEmpty()) {
                            if (!sb.isEmpty()) {
                                sb.append(" ");
                            }
                            sb.append(text);
                        }
                    }
                }

                return !sb.isEmpty() ? sb.toString() : null;
            }

        } catch (Exception e) {
            System.err.println("Failed to parse MCP result: " + e.getMessage());
        }

        return null;
    }
}
