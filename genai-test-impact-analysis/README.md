# GenAI Test Impact Analysis

This project is a minimal Spring Boot PoC that analyzes a Git-style diff and attempts to identify impacted tests. and If for any code changes code coverage is not there then it will suggests test codes to get coverage.
It uses heuristics to find candidate tests and calls Google Gemini via the Google Gen AI Java SDK to rank and explain.

## How to run

Prerequisites:
- Java 17+, Maven
- Set one of:
  - `GEMINI_API_KEY` (for Gemini Developer API), or
  - Application Default Credentials (ADC) + `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` for Vertex AI.
- (Optional) set `GEMINI_MODEL` env var (default: gemini-2.5-flash)

Build & run:
```
mvn clean package
mvn spring-boot:run
```

POST a `unified diff` to:
```
POST http://localhost:8080/api/diff/analyze
Body: raw unified diff text

--- a/src/main/java/com/example/impact/GenAIServiceGemini.java
+++ b/src/main/java/com/example/impact/GenAIServiceGemini.java
@@ -1,6 +1,8 @@
public class GenAIServiceGemini {
     public List<ImpactedTest> scoreAndExplain(String unifiedDiff, List<ImpactedTest> candidates) {
        if (candidates != null) return Collections.emptyList();

        String apiKey = System.getenv("GEMINI_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            throw new RuntimeException("Missing GEMINI_API_KEY environment variable");
        }

}

Output:
{
    "changeId": "c3b5e50d-8402-4834-9a01-b8c04f43d3d0",
    "impactedTests": [
        {
            "testFile": "src\\test\\java\\com\\example\\impact\\service\\DiffServiceTest.java",
            "reason": "The candidate test file `DiffServiceTest.java` does not directly reference the `scoreAndExplain` method of `GenAIServiceGemini` in its listed dependencies. It references `parseResponse` and `ImpactedTest` methods, suggesting it tests a different part of the `GenAIServiceGemini` or a service that uses it for other functionalities. Therefore, it is highly unlikely to be directly impacted by the specific change in `scoreAndExplain`.",
            "score": 0.1,
            "testingStrategy": "The change introduces a new early exit condition in `GenAIServiceGemini.scoreAndExplain` when the `candidates` list is not null. While `DiffServiceTest` is not directly impacted, it is critical to ensure `GenAIServiceGemini.scoreAndExplain` itself has thorough unit test coverage. A dedicated unit test class, `GenAIServiceGeminiTest.java`, should be created or updated to specifically cover this new `candidates != null` path, as well as existing paths (e.g., `candidates == null` leading to API key validation) to ensure no regressions and complete branch coverage.",
            "additionalProperties": {
                "value": "[package com.example.impact;\n\nimport com.example.impact.model.ImpactedTest;\nimport org.junit.jupiter.api.BeforeEach;\nimport org.junit.jupiter.api.AfterEach;\nimport org.junit.jupiter.api.Test;\nimport org.mockito.MockedStatic;\nimport org.mockito.Mockito;\n\nimport java.util.Arrays;\nimport java.util.Collections;\nimport java.util.List;\n\nimport static org.junit.jupiter.api.Assertions.*;\nimport static org.mockito.Mockito.mockStatic;\n\npublic class GenAIServiceGeminiTest {\n\n    private GenAIServiceGemini genAIServiceGemini;\n    private MockedStatic<System> mockedSystem;\n\n    @BeforeEach\n    void setUp() {\n        genAIServiceGemini = new GenAIServiceGemini();\n        // Mock System.getenv to control API key behavior for isolated testing\n        mockedSystem = mockStatic(System.class);\n    }\n\n    @AfterEach\n    void tearDown() {\n        mockedSystem.close(); // Close the mock after each test to prevent resource leaks\n    }\n\n    @Test\n    void scoreAndExplain_withNonNullCandidates_returnsEmptyList() {\n        // Given\n        String unifiedDiff = \"some diff\";\n        List<ImpactedTest> candidates = Arrays.asList(new ImpactedTest(), new ImpactedTest());\n\n        // When\n        List<ImpactedTest> result = genAIServiceGemini.scoreAndExplain(unifiedDiff, candidates);\n\n        // Then\n        assertNotNull(result);\n        assertTrue(result.isEmpty());\n        // Verify that the API key check was not reached due to the new early exit condition.\n        mockedSystem.verify(() -> System.getenv(\"GEMINI_API_KEY\"), Mockito.never());\n    }\n\n    @Test\n    void scoreAndExplain_withNullCandidates_throwsRuntimeExceptionIfApiKeyMissing() {\n        // Given\n        String unifiedDiff = \"some diff\";\n        List<ImpactedTest> candidates = null;\n\n        // Mock System.getenv to return null for GEMINI_API_KEY, simulating a missing environment variable.\n        mockedSystem.when(() -> System.getenv(\"GEMINI_API_KEY\")).thenReturn(null);\n\n        // When/Then\n        RuntimeException thrown = assertThrows(RuntimeException.class, () -> {\n            genAIServiceGemini.scoreAndExplain(unifiedDiff, candidates);\n        });\n\n        assertEquals(\"Missing GEMINI_API_KEY environment variable\", thrown.getMessage());\n        // Verify that the API key check was indeed called when candidates is null.\n        mockedSystem.verify(() -> System.getenv(\"GEMINI_API_KEY\"), Mockito.times(1));\n    }\n\n    @Test\n    void scoreAndExplain_withNullCandidates_throwsRuntimeExceptionIfApiKeyEmpty() {\n        // Given\n        String unifiedDiff = \"some diff\";\n        List<ImpactedTest> candidates = null;\n\n        // Mock System.getenv to return an empty string for GEMINI_API_KEY, simulating an empty environment variable.\n        mockedSystem.when(() -> System.getenv(\"GEMINI_API_KEY\")).thenReturn(\"\");\n\n        // When/Then\n        RuntimeException thrown = assertThrows(RuntimeException.class, () -> {\n            genAIServiceGemini.scoreAndExplain(unifiedDiff, candidates);\n        });\n\n        assertEquals(\"Missing GEMINI_API_KEY environment variable\", thrown.getMessage());\n        // Verify that the API key check was indeed called when candidates is null.\n        mockedSystem.verify(() -> System.getenv(\"GEMINI_API_KEY\"), Mockito.times(1));\n    }\n}]"
            }
        }
    ]
}

```

This PoC expects the repo under the working directory; adjust `DiffService.repoRoot` in code if necessary.

## Notes & references
- Uses Google Gen AI Java SDK (`com.google.genai:google-genai`). See SDK docs and quickstarts:
  - Gemini/Vertex quickstart and generateContent: https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstart. 
  - Google Gen AI Java SDK: https://github.com/googleapis/java-genai and Maven: https://repo1.maven.org/artifact/com.google.genai/google-genai
- The service attempts to parse JSON output from the model. For production, lock the prompt and validate JSON strictly.
