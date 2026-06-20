package com.example.impact.service;

import com.example.impact.model.ImpactedTest;
import com.example.impact.util.MethodCallGraphExtractor;
import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.file.*;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class TestDiscoveryService {

    private final Map<String, Set<String>> methodHierarchy;

    public TestDiscoveryService() {
        // Build hierarchy from source code once during startup
        this.methodHierarchy = MethodCallGraphExtractor.buildTransitiveHierarchy();
    }

    /**
     * Find tests that reference a changed file or any dependent method in the hierarchy.
     */
    public List<ImpactedTest> findTestsReferencing(Path repoRoot, String changedFilePath) {
        try {
            String changedSimpleName = extractSimpleClassName(changedFilePath);
            Set<String> dependentMethods = findDependentMethods(changedSimpleName);

            Path testRoot = repoRoot.resolve("src/test/java");
            if (!Files.exists(testRoot)) return Collections.emptyList();

            List<Path> testFiles = Files.walk(testRoot)
                    .filter(p -> p.toString().endsWith(".java"))
                    .collect(Collectors.toList());

            List<ImpactedTest> results = new ArrayList<>();
            for (Path testFile : testFiles) {
                String content = Files.readString(testFile);

                // if test references changed class or dependent methods
                boolean mentions = dependentMethods.stream()
                        .anyMatch(dep -> content.contains(dep.substring(dep.lastIndexOf('.') + 1)));

                if (mentions) {
                    results.add(new ImpactedTest(
                            repoRoot.relativize(testFile).toString(),
                            "References changed/dependent methods: " + dependentMethods,
                            0.7
                    ));
                } else {
                    // fallback: existing heuristic
                    boolean imports = false;
                    try {
                        CompilationUnit cu = StaticJavaParser.parse(content);
                        imports = cu.getImports().stream().anyMatch(i -> i.getNameAsString().endsWith(changedSimpleName));
                    } catch (Exception ignored) {}

                    if (imports) {
                        results.add(new ImpactedTest(
                                repoRoot.relativize(testFile).toString(),
                                "Imports changed class " + changedSimpleName,
                                0.5
                        ));
                    }
                }
            }
            return results;
        } catch (IOException e) {
            return Collections.emptyList();
        }
    }

    private Set<String> findDependentMethods(String simpleClassName) {
        Set<String> impacted = new HashSet<>();
        for (Map.Entry<String, Set<String>> entry : methodHierarchy.entrySet()) {
            if (entry.getKey().contains(simpleClassName)) {
                impacted.addAll(entry.getValue());
            }
        }
        return impacted;
    }

    private static String extractSimpleClassName(String path) {
        int s = path.lastIndexOf('/');
        if (s < 0) s = path.lastIndexOf('\\');
        String name = s >= 0 ? path.substring(s + 1) : path;
        if (name.endsWith(".java")) name = name.substring(0, name.length() - 5);
        return name;
    }
}
