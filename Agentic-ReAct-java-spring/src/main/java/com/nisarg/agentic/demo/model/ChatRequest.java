package com.nisarg.agentic.demo.model;

public class ChatRequest {
    private String userId;
    private String prompt;

    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }

    public String getPrompt() { return prompt; }
    public void setPrompt(String prompt) { this.prompt = prompt; }
}