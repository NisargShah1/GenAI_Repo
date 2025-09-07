/*
package com.example.stream.http.MCPServer.controller;

import com.example.stream.http.MCPServer.model.McpRequest;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.servlet.mvc.method.annotation.ResponseBodyEmitter;

import java.util.concurrent.Executors;

public class MCPController {

    @PostMapping(value = "/mcp/message", produces = MediaType.APPLICATION_OCTET_STREAM_VALUE)
    public ResponseBodyEmitter handleMessage(@RequestBody McpRequest request) {
        ResponseBodyEmitter emitter = new ResponseBodyEmitter(0L); // no timeout
        Executors.newSingleThreadExecutor().submit(() -> {
            try {
                emitter.send("chunk-1 ".getBytes());
                Thread.sleep(500);
                emitter.send("chunk-2 ".getBytes());
                Thread.sleep(500);
                emitter.send("chunk-3 ".getBytes());a
                emitter.complete();
            } catch (Exception e) {
                emitter.completeWithError(e);
            }
        });
        return emitter;
    }


}
*/
