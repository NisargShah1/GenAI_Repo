package com.nisarg.agentic.demo.controller;

import com.nisarg.agentic.demo.model.ChatRequest;
import com.nisarg.agentic.demo.service.AgentService;
import org.springframework.http.MediaType;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;

@RestController
@RequestMapping("/api/chat")
public class ChatController {

    private final AgentService agentService;

    public ChatController(AgentService agentService) {
        this.agentService = agentService;
    }

    @PostMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<ServerSentEvent<String>> chatStream(@RequestBody ChatRequest request) {
        return agentService.chatStream(request.getUserId(), request.getPrompt())
                .map(event -> ServerSentEvent.builder(event).build());
    }
}