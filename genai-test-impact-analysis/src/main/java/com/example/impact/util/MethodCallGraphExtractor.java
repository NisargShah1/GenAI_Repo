package com.example.impact.util;

import com.github.javaparser.*;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import com.github.javaparser.symbolsolver.JavaSymbolSolver;
import com.github.javaparser.symbolsolver.resolution.typesolvers.*;

import java.io.File;
import java.io.IOException;
import java.util.*;

public class MethodCallGraphExtractor {

    private static final Map<String, Set<String>> methodCalls = new HashMap<>();

    public static void buildCallHierarchy() {
        // Configure type solvers for symbol resolution
        CombinedTypeSolver typeSolver = new CombinedTypeSolver();
        typeSolver.add(new ReflectionTypeSolver());
        typeSolver.add(new JavaParserTypeSolver(new File("src/main/java")));

        ParserConfiguration config = new ParserConfiguration()
                .setSymbolResolver(new JavaSymbolSolver(typeSolver));
        StaticJavaParser.setConfiguration(config);

        File projectDir = new File("src/main/java");
        try {
            new MethodCallGraphExtractor().analyzeDirectory(projectDir);
        } catch (IOException e) {
            // Shouldn't happen as analyzeDirectory handles IO internally, but log just in case
            System.err.println("Error analyzing directory: " + e.getMessage());
        }

        // Print multi-level (transitive) call hierarchy
        // find roots (methods that are not callees of any other method)
        Set<String> allCallers = new HashSet<>(methodCalls.keySet());
        Set<String> allCallees = new HashSet<>();
        methodCalls.values().forEach(allCallees::addAll);

        Set<String> roots = new HashSet<>(allCallers);
        roots.removeAll(allCallees);
        if (roots.isEmpty()) {
            // fallback: if no clear roots, print all callers as roots
            roots = allCallers;
        }

        int maxDepth = 10; // set a reasonable default max depth to avoid infinite recursion in large graphs
        for (String root : roots) {
            printHierarchy(root, 0, new HashSet<>(), maxDepth);
        }
    }

    private void analyzeDirectory(File dir) throws IOException {
        for (File file : Objects.requireNonNull(dir.listFiles())) {
            if (file.isDirectory()) analyzeDirectory(file);
            else if (file.getName().endsWith(".java")) {
                try {
                    CompilationUnit cu = StaticJavaParser.parse(file);
                    cu.accept(new MethodVisitor(), null);
                } catch (Exception e) {
                    System.err.println("Skipping " + file.getName() + ": " + e.getMessage());
                }
            }
        }
    }

    private static class MethodVisitor extends VoidVisitorAdapter<Void> {
        @Override
        public void visit(MethodDeclaration method, Void arg) {
            try {
                String methodName = method.resolve().getQualifiedSignature();
                Set<String> callees = methodCalls.computeIfAbsent(methodName, k -> new HashSet<>());

                method.findAll(MethodCallExpr.class).forEach(call -> {
                    try {
                        String calledMethod = call.resolve().getQualifiedSignature();

                        // ✅ Filter out default Java / JDK calls
                        if (!isDefaultJavaPackage(calledMethod)) {
                            callees.add(calledMethod);
                        }

                    } catch (Exception ignored) {
                        // unresolved or external
                    }
                });
            } catch (Exception ignored) {
                // Skip methods that can’t be resolved
            }
        }

        private boolean isDefaultJavaPackage(String qualifiedSignature) {
            return qualifiedSignature.startsWith("java.") ||
                    qualifiedSignature.startsWith("javax.") ||
                    qualifiedSignature.startsWith("jdk.") ||
                    qualifiedSignature.startsWith("sun.") ||
                    qualifiedSignature.startsWith("com.sun.") ||
                    qualifiedSignature.startsWith("org.springframework.") ||
                    qualifiedSignature.startsWith("org.slf4j.");
        }

    }

    // Recursive printer for multi-level hierarchy with cycle detection
    private static void printHierarchy(String method, int depth, Set<String> visited, int maxDepth) {
        if (depth > maxDepth) {
            System.out.println(indent(depth) + "... (max depth reached)");
            return;
        }

        System.out.println(indent(depth) + method);

        Set<String> callees = methodCalls.getOrDefault(method, Collections.emptySet());
        if (callees.isEmpty()) return;

        visited.add(method);
        for (String callee : new TreeSet<>(callees)) { // sort for stable output
            if (visited.contains(callee)) {
                System.out.println(indent(depth + 1) + callee + " (cycle)");
            } else {
                printHierarchy(callee, depth + 1, new HashSet<>(visited), maxDepth);
            }
        }
    }

    // New: build transitive hierarchy as a Map<caller, Set<reachable callees>>

    private static String indent(int depth) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < depth; i++) sb.append("  ");
        return sb.toString();
    }
    public static Map<String, Set<String>> buildTransitiveHierarchy(int maxDepth) {
        Map<String, Set<String>> transitive = new HashMap<>();
        for (String caller : methodCalls.keySet()) {
            Set<String> reach = new HashSet<>();
            // start with empty visited set containing the caller to avoid immediate cycles
            Set<String> visited = new HashSet<>();
            visited.add(caller);
            buildReachable(caller, 0, visited, maxDepth, reach);
            transitive.put(caller, reach);
        }
        return transitive;
    }

    // Convenience overload with default maxDepth
    public static Map<String, Set<String>> buildTransitiveHierarchy() {
        buildCallHierarchy();
        return buildTransitiveHierarchy(10);
    }

    // Helper: recursively collect reachable methods up to maxDepth
    private static void buildReachable(String method, int depth, Set<String> visited, int maxDepth, Set<String> reach) {
        if (depth >= maxDepth) return;
        Set<String> callees = methodCalls.getOrDefault(method, Collections.emptySet());
        for (String callee : callees) {
            // add returns true if callee was newly added
            boolean added = reach.add(callee);
            if (!visited.contains(callee)) {
                Set<String> newVisited = new HashSet<>(visited);
                newVisited.add(callee);
                // only recurse if we haven't just hit a cycle that would cause infinite recursion
                buildReachable(callee, depth + 1, newVisited, maxDepth, reach);
            }
        }
    }

}
