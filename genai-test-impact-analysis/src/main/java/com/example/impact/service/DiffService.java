package com.example.impact.service;

import com.example.impact.model.ImpactResult;
import com.example.impact.model.ImpactedTest;
import com.example.impact.util.GitDiffParser;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.nio.file.*;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class DiffService {

    @Autowired
    TestDiscoveryService testDiscoveryService;

    @Autowired
    GenAIServiceGemini genAIService;

    private final Path repoRoot = Paths.get(System.getProperty("user.dir"));

    public ImpactResult analyzeDiff(String unifiedDiff) {
        // Extract changed files
        List<String> changed = GitDiffParser.extractChangedFiles(unifiedDiff);
        List<String> javaChanged = changed.stream()
                .filter(f -> f.trim().endsWith(".java"))
                .collect(Collectors.toList());

        // Gather impacted tests using static + method hierarchy analysis
        List<ImpactedTest> candidates = new ArrayList<>();
        for (String changedFile : javaChanged) {
            List<ImpactedTest> impacted = testDiscoveryService.findTestsReferencing(repoRoot, changedFile.trim());
            candidates.addAll(impacted);
        }

        // Rank and explain with Gemini
        List<ImpactedTest> scored = genAIService.scoreAndExplain(unifiedDiff, candidates);
        scored.sort(Comparator.comparingDouble(ImpactedTest::getScore).reversed());

        return new ImpactResult(UUID.randomUUID().toString(), scored);
    }
}
