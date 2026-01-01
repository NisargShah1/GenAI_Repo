package com.nisarg.chat.llm;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
@Slf4j
public class GeminiClient {

    private final ChatModel chatModel;

    public String generateAggregation(String prompt) {
        log.debug("Sending prompt to Gemini: {}", prompt);
        try {
            String response = chatModel.call(prompt);
            log.debug("Received response from Gemini: {}", response);
            return response;
        } catch (Exception e) {
            log.error("Error calling Gemini API", e);
            throw e;
        }
    }
}
