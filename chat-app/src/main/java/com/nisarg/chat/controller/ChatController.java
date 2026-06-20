package com.nisarg.chat.controller;

import com.nisarg.chat.service.ChatService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/chat")
@RequiredArgsConstructor
@CrossOrigin(origins = "http://localhost:5173") // Allow frontend (Vite default port)
public class ChatController {

    private final ChatService chatService;

    @PostMapping
    public ChatService.ChatResponse chat(@RequestBody ChatRequest request) {
        return chatService.processChat(request.getMessage());
    }

    @Data
    public static class ChatRequest {
        private String sessionId;
        private String message;
    }
}
