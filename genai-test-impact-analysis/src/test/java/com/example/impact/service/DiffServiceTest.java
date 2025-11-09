package com.example.impact.service;

import com.example.impact.model.ImpactResult;
import com.example.impact.model.ImpactedTest;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.nio.file.Path;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.anyList;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class DiffServiceTest {

    @Mock
    TestDiscoveryService testDiscoveryService;

    @Mock
    GenAIServiceGemini genAIService;

    DiffService diffService;

    @BeforeEach
    void setUp() {
        diffService = new DiffService();
        // fields are package-private in DiffService so we can set them directly
        diffService.testDiscoveryService = testDiscoveryService;
        diffService.genAIService = genAIService;
    }

    @Test
    void analyzeDiff_nullDiff_returnsEmptyImpactedTests() {
        when(genAIService.scoreAndExplain(anyString(), anyList())).thenReturn(Collections.emptyList());

        ImpactResult result = diffService.analyzeDiff(null);

        assertNotNull(result);
        assertNotNull(result.getImpactedTests());
        assertTrue(result.getImpactedTests().isEmpty());
        verify(genAIService, times(1)).scoreAndExplain(anyString(), anyList());
        verifyNoInteractions(testDiscoveryService);
    }

    @Test
    void analyzeDiff_nonJavaFiles_ignoresAndCallsGenAI() {
        String diff = "+++ b/README.md\n" +
                "+++ b/docs/notes.txt\n";

        when(genAIService.scoreAndExplain(eq(diff), anyList())).thenReturn(Collections.emptyList());

        ImpactResult result = diffService.analyzeDiff(diff);

        assertNotNull(result);
        assertNotNull(result.getImpactedTests());
        assertTrue(result.getImpactedTests().isEmpty());

        // verify test discovery not called for non-java changes
        verifyNoInteractions(testDiscoveryService);
        verify(genAIService, times(1)).scoreAndExplain(eq(diff), anyList());
    }

    @Test
    void analyzeDiff_javaFile_collectsCandidatesAndSortsByScore() {
        String diff = "+++ b/src/main/java/com/example/Foo.java\n";

        ImpactedTest t1 = new ImpactedTest("src/test/java/TestA.java", "reasonA", 0.0);
        ImpactedTest t2 = new ImpactedTest("src/test/java/TestB.java", "reasonB", 0.0);

        // testDiscoveryService should return candidates based on changed file
        when(testDiscoveryService.findTestsReferencing(any(Path.class), eq("src/main/java/com/example/Foo.java")))
                .thenReturn(Arrays.asList(t1, t2));

        // GenAI will score and explain; return results with different scores (out of order)
        ImpactedTest scored1 = new ImpactedTest(t1.getTestFile(), t1.getReason(), 0.4);
        ImpactedTest scored2 = new ImpactedTest(t2.getTestFile(), t2.getReason(), 0.9);
        // return list in original order to ensure DiffService sorts it
        when(genAIService.scoreAndExplain(eq(diff), anyList())).thenReturn(Arrays.asList(scored1, scored2));

        ImpactResult result = diffService.analyzeDiff(diff);

        assertNotNull(result);
        List<ImpactedTest> impacted = result.getImpactedTests();
        assertEquals(2, impacted.size());

        // Ensure sorted by score descending
        assertEquals("src/test/java/TestB.java", impacted.get(0).getTestFile());
        assertEquals(0.9, impacted.get(0).getScore());
        assertEquals("src/test/java/TestA.java", impacted.get(1).getTestFile());
        assertEquals(0.4, impacted.get(1).getScore());

        // verify test discovery was invoked with trimmed path
        ArgumentCaptor<Path> pathCaptor = ArgumentCaptor.forClass(Path.class);
        verify(testDiscoveryService, times(1)).findTestsReferencing(pathCaptor.capture(), eq("src/main/java/com/example/Foo.java"));
        assertNotNull(pathCaptor.getValue());

        verify(genAIService, times(1)).scoreAndExplain(eq(diff), anyList());
    }
}

