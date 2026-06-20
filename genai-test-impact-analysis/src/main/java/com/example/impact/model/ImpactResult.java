package com.example.impact.model;

import java.util.List;

public class ImpactResult {
    private String changeId;
    private List<ImpactedTest> impactedTests;

    public ImpactResult() {}
    public ImpactResult(String changeId, List<ImpactedTest> impactedTests) {
        this.changeId = changeId;
        this.impactedTests = impactedTests;
    }
    public String getChangeId() { return changeId; }
    public void setChangeId(String changeId) { this.changeId = changeId; }
    public List<ImpactedTest> getImpactedTests() { return impactedTests; }
    public void setImpactedTests(List<ImpactedTest> impactedTests) { this.impactedTests = impactedTests; }
}
