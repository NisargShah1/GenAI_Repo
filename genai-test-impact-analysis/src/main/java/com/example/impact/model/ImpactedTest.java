package com.example.impact.model;

import java.util.Map;

public class ImpactedTest {
    private String testFile;
    private String reason;
    private double score;
    private String testingStrategy;
    private Map<Object, Object> additionalTests;

    public ImpactedTest() {}
    public ImpactedTest(String testFile, String reason, double score) {
        this.testFile = testFile;
        this.reason = reason;
        this.score = score;
    }
    public String getTestFile() { return testFile; }
    public void setTestFile(String testFile) { this.testFile = testFile; }
    public String getReason() { return reason; }
    public void setReason(String reason) { this.reason = reason; }
    public double getScore() { return score; }
    public void setScore(double score) { this.score = score; }
    public String getTestingStrategy() { return testingStrategy; }
    public void setTestingStrategy(String testingStrategy) { this.testingStrategy = testingStrategy; }
    public Map<Object, Object> getAdditionalTests() { return additionalTests; }
    public void setAdditionalTests(Map<Object, Object> additionalTests) { this.additionalTests = additionalTests; }
}
