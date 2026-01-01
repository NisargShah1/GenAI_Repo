package com.nisarg.chat.service;

import com.nisarg.chat.llm.GeminiClient;
import com.nisarg.chat.mongo.MongoAggregationExecutor;
import com.nisarg.chat.parser.LlmResponseParser;
import com.nisarg.chat.prompt.PromptBuilder;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.bson.Document;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class ChatService {

    private final PromptBuilder promptBuilder;
    private final GeminiClient geminiClient;
    private final LlmResponseParser parser;
    private final MongoAggregationExecutor mongoExecutor;

    public ChatResponse processChat(String userQuery) {
        log.info("Processing query: {}", userQuery);

        // 1. Build Prompt
        String prompt = promptBuilder.buildPrompt(userQuery);

        // 2. Call LLM
        String rawResponse = geminiClient.generateAggregation(prompt);

        // 3. Parse Response
        LlmResponseParser.GeminiResponse geminiResponse = parser.parse(rawResponse);

        // 4. Execute Aggregation (if pipeline exists)
        List<Document> data = Collections.emptyList();
        if (geminiResponse.getPipeline() != null && !geminiResponse.getPipeline().isEmpty()) {
            data = mongoExecutor.execute(geminiResponse.getCollection(), geminiResponse.getPipeline());
        }

        // 5. Build Final Explanation (Verify & Explain)
        String finalExplanation = geminiResponse.getExplanation();
       /* if (!data.isEmpty()) {
            try {
                // Limit data size prevents blowing up context window if result is huge
                String dataString = data.size() > 20 ? data.subList(0, 20).toString() + "... (truncated)"
                        : data.toString();
                String explanationPrompt = promptBuilder.buildExplanationPrompt(userQuery, dataString);
                finalExplanation = geminiClient.generateAggregation(explanationPrompt);
            } catch (Exception e) {
                log.warn("Failed to generate follow-up explanation", e);
            }
        }*/

        // 6. Build Final Response
        return new ChatResponse(
                geminiResponse.getOutputType(),
                data,
                geminiResponse.getChart(),
                finalExplanation);
    }

    @lombok.Data
    @lombok.AllArgsConstructor
    public static class ChatResponse {
        private String type;
        private Object data;
        private LlmResponseParser.ChartConfig chart;
        private String explanation;
    }
}
