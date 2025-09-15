package com.nisarg.agentic.demo.mcp;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.nisarg.agentic.demo.util.ParsingUtility;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;

import java.time.Duration;
import java.util.Collections;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class MCPClient {
    private static final Logger logger = LoggerFactory.getLogger(MCPClient.class);

    private final WebClient webClient;
    private String sessionId = null;
    private final Map<String, CompletableFuture<String>> pendingRequests = new ConcurrentHashMap<>();

    private final String sseUrl = System.getenv().getOrDefault("MCP_SSE_URL", "http://localhost:8081/mcp/sse");
    private final String messageUrl = System.getenv().getOrDefault("MCP_MESSAGE_URL", "http://localhost:8081/mcp/message");

    public MCPClient(WebClient.Builder builder) {
        this.webClient = builder.build();
    }

    @PostConstruct
    public void connect() {
        logger.info("Connecting to MCP SSE at {}", sseUrl);

        Flux<String> eventStream = webClient.get()
                .uri(sseUrl)
                .accept(MediaType.TEXT_EVENT_STREAM)
                .retrieve()
                .bodyToFlux(String.class);

        eventStream
                .doOnNext(this::handleEvent)
                .doOnError(err -> logger.error("SSE error: {}", err.getMessage()))
                .retryWhen(reactor.util.retry.Retry.backoff(Long.MAX_VALUE, Duration.ofSeconds(3)))
                .subscribe();
    }

    private void handleEvent(String event) {
        logger.info("SSE Event: {}", event);

        if (event.contains("sessionId")) {
            this.sessionId = extractSessionIdFromUrl(event);
            logger.info("Session ID: {}", sessionId);
            sendInitialize();
            return;
        }

        if (event.contains("\"id\":\"init-")) {
            logger.info("MCP connection initialized successfully!");
            onNotificationInitialize();
            return;
        }

        String id = extractIdField(event);
        if (event.contains("\"tools\"") || event.contains("\"tools/list\"")) {
            completeFuture(id, event);
            return;
        }

        try {
            if (id != null && pendingRequests.containsKey(id)) {
                String result = ParsingUtility.extractResult(event);
                completeFuture(id, result);
            }
        } catch (Exception e) {
            logger.error("Failed to parse SSE event: {}", e.getMessage());
        }
    }

    private void completeFuture(String id, String result) {
        if (id != null && pendingRequests.containsKey(id)) {
            pendingRequests.get(id).complete(result);
            pendingRequests.remove(id);
        }
    }

    private void onNotificationInitialize() {
        String initMessage = """
            {
              "jsonrpc": "2.0",
              "method": "notifications/initialized"
            }
            """;
        postMessage(initMessage, "Sent notification initialize message", "Failed to send notification initialize");
    }

    private void sendInitialize() {
        String initMessage = """
            {
              "jsonrpc": "2.0",
              "id": "init-%s",
              "method": "initialize",
              "params": {
                "protocolVersion": "2024-11-05",
                "clientInfo": {
                  "name": "spring-agent-client",
                  "version": "1.0.0"
                },
                "capabilities": {}
              }
            }
            """.formatted(UUID.randomUUID().toString());
        postMessage(initMessage, "Sent initialize message", "Failed to send initialize");
    }

    private void postMessage(String payload, String successMsg, String errorMsg) {
        webClient.post()
                .uri(messageUrl + "?sessionId=" + sessionId)
                .contentType(MediaType.APPLICATION_JSON)
                .body(BodyInserters.fromValue(payload))
                .retrieve()
                .onStatus(
                        HttpStatusCode::isError,
                        clientResponse -> clientResponse.bodyToMono(String.class)
                                .doOnNext(body -> logger.error("Error response: {}", body))
                                .thenReturn(new RuntimeException("HTTP error: " + clientResponse.statusCode()))
                )
                .toBodilessEntity()
                .doOnSuccess(r -> logger.info(successMsg))
                .doOnError(err -> logger.error(errorMsg + ": {}", err.getMessage()))
                .subscribe();
    }

    public String callTool(String toolName, String inputJson) {
        String requestId = UUID.randomUUID().toString();
        CompletableFuture<String> future = new CompletableFuture<>();
        pendingRequests.put(requestId, future);

        String payload = String.format(
                "{\"jsonrpc\":\"2.0\",\"id\":\"%s\",\"method\":\"tools/call\",\"params\":{\"name\":\"%s\",\"arguments\":%s}}",
                requestId, toolName, inputJson
        );

        postMessage(payload, null, "Failed to send tool call");

        try {
            return future.get(20, java.util.concurrent.TimeUnit.SECONDS);
        } catch (Exception e) {
            pendingRequests.remove(requestId);
            return "Timeout waiting for tool response";
        }
    }

    private String extractIdField(String json) {
        String pattern = "\"" + "id" + "\":\"";
        int start = json.indexOf(pattern);
        if (start == -1) return null;
        int end = json.indexOf("\"", start + pattern.length());
        return json.substring(start + pattern.length(), end);
    }

    public static String extractSessionIdFromUrl(String url) {
        String key = "sessionId=";
        int idx = url.indexOf(key);
        if (idx == -1) return null;
        int start = idx + key.length();
        int end = url.indexOf('&', start);
        if (end == -1) end = url.length();
        return url.substring(start, end);
    }

    public Map<String, String> listTools() {
        String requestId = UUID.randomUUID().toString();
        CompletableFuture<String> future = new CompletableFuture<>();
        pendingRequests.put(requestId, future);

        String payload = String.format(
                "{\"jsonrpc\":\"2.0\",\"id\":\"%s\",\"method\":\"tools/list\",\"params\":{}}",
                requestId
        );

        postMessage(payload, null, "Failed to request tool list");

        try {
            String result = future.get(10, java.util.concurrent.TimeUnit.SECONDS);
            Map<String, String> tools = new ConcurrentHashMap<>();
            JsonNode json = new ObjectMapper().readTree(result);
            JsonNode toolsNode = json.path("result").path("tools");
            if (toolsNode.isArray()) {
                for (JsonNode t : toolsNode) {
                    String name = t.path("name").asText();
                    String desc = t.path("description").asText("");
                    tools.put(name, desc);
                }
            }
            return Collections.unmodifiableMap(tools);
        } catch (Exception e) {
            logger.error("Timeout or error waiting for tool list: {}", e.getMessage());
            return Collections.emptyMap();
        } finally {
            pendingRequests.remove(requestId);
        }
    }
}
