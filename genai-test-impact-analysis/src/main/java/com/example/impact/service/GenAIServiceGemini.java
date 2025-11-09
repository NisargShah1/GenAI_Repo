package com.example.impact.service;

import com.example.impact.model.ImpactedTest;
import com.google.genai.Client;
import com.google.genai.types.Content;
import com.google.genai.types.GenerateContentConfig;
import com.google.genai.types.GenerateContentResponse;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.genai.types.Part;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class GenAIServiceGemini {

    private static final Logger log = LoggerFactory.getLogger(GenAIServiceGemini.class);

    public List<ImpactedTest> scoreAndExplain(String unifiedDiff, List<ImpactedTest> candidates) {
        if (candidates == null || candidates.isEmpty()) return Collections.emptyList();

        String apiKey = System.getenv("GEMINI_API_KEY");
        // fallback to system property to make unit tests easier to run
        if (apiKey == null || apiKey.isEmpty()) {
            apiKey = System.getProperty("GEMINI_API_KEY");
        }
        if (apiKey == null || apiKey.isEmpty()) {
            throw new RuntimeException("Missing GEMINI_API_KEY environment variable or system property");
        }

        @SuppressWarnings("resource")
        Client client = new Client(); // will pick up API key from GEMINI_API_KEY or GOOGLE_API_KEY

        try {
            StringBuilder sb = new StringBuilder();
            sb.append("You are an expert software test analyst. Given this code diff and candidate test files, ");
            sb.append("rank each test by likelihood that it is impacted and provide a brief reason and score between 0.0 and 1.0. ");
            sb.append("Provide smarter testing strategy and if any of the code is not having adequate test coverage then provide tests code to cover that code. Refer existing framework to generate testcases. ");
            sb.append("Respond ONLY as a JSON array of objects with fields: test, score, reason, testingStrategy, tests.\n\n");
            sb.append("DIFF:\n");
            sb.append(unifiedDiff.length() > 4000 ? unifiedDiff.substring(0, 4000) : unifiedDiff);
            sb.append("\n\nCANDIDATES:\n");
            for (ImpactedTest t : candidates) {
                sb.append(t.getTestFile()).append(" - ").append(t.getReason()).append("\n");
            }

            Content content = Content.builder()
                    .parts(Collections.singletonList(Part.fromText(sb.toString())))
                    .build();

            // ✅ Build configuration (optional)
            GenerateContentConfig config = GenerateContentConfig.builder()
                    .temperature(0.3f)
                    .build();
            // ✅ Generate content using Gemini
            GenerateContentResponse resp = client.models.generateContent(
                    "gemini-2.5-flash",
                    Collections.singletonList(content),
                    config

            );
            String text = resp.text();

            if (text == null || text.isEmpty()) {
                throw new RuntimeException("Empty response from Gemini API");
            }

            return parseResponse(text, candidates);

        } catch (Exception e) {
            log.error("Error while scoring and explaining candidates", e);
            // fallback if LLM fails
            candidates.forEach(t -> {
                if (t.getScore() == 0) t.setScore(0.3);
                if (t.getReason() == null) t.setReason("Fallback: Gemini call failed");
            });
            return candidates;
        }
    }

    /**
     * Parse the raw JSON/text response from the LLM and produce ImpactedTest results.
     * Made public for unit testing so tests can call this without invoking the external client.
     */
    public List<ImpactedTest> parseResponse(String rawText, List<ImpactedTest> candidates) throws Exception {
        String text = rawText.replaceAll("^```json", "").replaceAll("```$", "").trim();

        ObjectMapper mapper = new ObjectMapper();
        List<Map<String, Object>> list = mapper.readValue(
                text,
                new TypeReference<>() {}
        );

        Map<String, ImpactedTest> map = candidates.stream()
                .collect(Collectors.toMap(ImpactedTest::getTestFile, c -> c));

        List<ImpactedTest> results = new ArrayList<>();
        for (Map<String, Object> obj : list) {
            String test = (String) obj.get("test");
            double score = obj.get("score") instanceof Number
                    ? ((Number) obj.get("score")).doubleValue()
                    : 0.0;
            String reason = obj.getOrDefault("reason", "").toString();
            String testingStrategy = obj.getOrDefault("testingStrategy", "").toString();

            // Safely handle the 'tests' field which may be a Map, a JSON string, a List, or other types
            Object testsObj = obj.get("tests");
            Map<Object, Object> testsMap = new HashMap<>();
            if (testsObj != null) {
                if (testsObj instanceof Map) {
                    Map<?, ?> raw = (Map<?, ?>) testsObj;
                    // bulk copy entries
                    raw.forEach(testsMap::put);
                } else if (testsObj instanceof List) {
                    // e.g. ArrayList containing maps (description/code pairs)
                    try {
                        List<Map<String, Object>> converted = mapper.convertValue(testsObj, new TypeReference<>() {});
                        testsMap.put("testsList", converted);
                    } catch (IllegalArgumentException ex) {
                        testsMap.put("value", testsObj.toString());
                    }
                } else if (testsObj instanceof String) {
                    String s = ((String) testsObj).trim();
                    // try to parse JSON string into a map
                    try {
                        Map<String, Object> parsed = mapper.readValue(s, new TypeReference<>() {});
                        testsMap.putAll(parsed);
                    } catch (Exception ex) {
                        // not JSON, keep raw string under a key
                        testsMap.put("raw", s);
                    }
                } else {
                    // attempt to convert other types into a map via ObjectMapper
                    try {
                        Map<String, Object> converted = mapper.convertValue(testsObj, new TypeReference<>() {});
                        if (converted != null) testsMap.putAll(converted);
                    } catch (IllegalArgumentException ex) {
                        testsMap.put("value", testsObj.toString());
                    }
                }
            }

            ImpactedTest base = map.getOrDefault(test, new ImpactedTest(test, reason, score));
            base.setScore(score);
            base.setReason(reason);
            base.setTestingStrategy(testingStrategy);
            base.setAdditionalTests(testsMap);
            results.add(base);
        }

        return results;
    }
}
