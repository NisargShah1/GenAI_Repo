package com.nisarg.chat.parser;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;

@Component
@RequiredArgsConstructor
@Slf4j
public class LlmResponseParser {

    private final ObjectMapper objectMapper;

    @Data
    public static class GeminiResponse {
        private String collection;
        private List<Map<String, Object>> pipeline;
        private String outputType;
        private ChartConfig chart;
        private String explanation; // Added explanation field as per some plans
    }

    @Data
    public static class ChartConfig {
        private String type;
        private String x;
        private String y;
    }

    public GeminiResponse parse(String jsonResponse) {
        try {
            // Cleanup markdown code blocks if present
            String cleanJson = jsonResponse;
            if (cleanJson.contains("```json")) {
                cleanJson = cleanJson.substring(cleanJson.indexOf("```json") + 7);
                if (cleanJson.contains("```")) {
                    cleanJson = cleanJson.substring(0, cleanJson.indexOf("```"));
                }
            } else if (cleanJson.contains("```")) {
                cleanJson = cleanJson.replace("```", "");
            }
            cleanJson = cleanJson.trim();

            return objectMapper.readValue(cleanJson, GeminiResponse.class);
        } catch (Exception e) {
            log.error("Failed to parse LLM response: {}", jsonResponse, e);
            throw new RuntimeException("Invalid JSON from LLM: " + e.getMessage(), e);
        }
    }
}
