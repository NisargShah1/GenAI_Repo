package com.nisarg.agentic.demo.logging;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

/**
 * AgentLogger provides structured logging for the agent pipeline.
 * It is meant to capture LLM thoughts, actions, tool calls, observations,
 * and final answers in a consistent format for analysis and debugging.
 */
@Component
public class AgentLogger {

    private static final Logger logger = LoggerFactory.getLogger("Agent");

    /**
     * Logs a structured event in the agent reasoning process.
     *
     * @param type  The type of log (e.g., "thought", "action", "observation", "answer", "error").
     * @param value The content/value of the log entry.
     */
    public void log(String type, String value) {
        // Structured format: [AGENT] type=value
        logger.info("[AGENT] {}: {}", type.toUpperCase(), value);
    }

    /**
     * Shortcut methods for common types
     */
    public void thought(String value) {
        log("thought", value);
    }

    public void action(String value) {
        log("action", value);
    }

    public void observation(String value) {
        log("observation", value);
    }

    public void answer(String value) {
        log("answer", value);
    }

    public void error(String value) {
        log("error", value);
    }
}
