package com.example.impact.service;

import com.example.impact.model.ImpactedTest;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class GenAIServiceGeminiTest {

    @Test
    void parseResponse_handlesTestsList() throws Exception {
        GenAIServiceGemini svc = new GenAIServiceGemini();

        // candidate list must contain an entry matching the 'test' field in the response
        List<ImpactedTest> candidates = List.of(new ImpactedTest("MyTest", "", 0.0));

        String json = "[{" +
                "\"test\":\"MyTest\"," +
                "\"score\":0.75," +
                "\"reason\":\"r\"," +
                "\"testingStrategy\":\"s\"," +
                "\"tests\":[{\"description\":\"desc\",\"code\":\"code\"}]" +
                "}]";

        List<ImpactedTest> results = svc.parseResponse(json, candidates);

        assertNotNull(results);
        assertEquals(1, results.size());

        ImpactedTest it = results.get(0);
        Map<Object, Object> props = it.getAdditionalProperties();
        assertNotNull(props);
        assertTrue(props.containsKey("testsList"));

        Object testsListObj = props.get("testsList");
        assertNotNull(testsListObj);
        assertTrue(testsListObj instanceof List);

        List<?> testsList = (List<?>) testsListObj;
        assertEquals(1, testsList.size());

        Object entry = testsList.get(0);
        assertTrue(entry instanceof Map);
        Map<?, ?> mapEntry = (Map<?, ?>) entry;
        assertEquals("desc", mapEntry.get("description"));
        assertEquals("code", mapEntry.get("code"));
    }
}

