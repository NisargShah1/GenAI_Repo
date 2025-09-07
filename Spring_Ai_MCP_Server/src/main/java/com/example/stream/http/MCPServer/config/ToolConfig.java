package com.example.stream.http.MCPServer.config;

import com.example.stream.http.MCPServer.tools.EmailTool;
import com.example.stream.http.MCPServer.tools.WeatherStreamTool;

import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.ai.tool.method.MethodToolCallbackProvider;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class ToolConfig {

    @Bean
    public ToolCallbackProvider tools(WeatherStreamTool weatherStreamTool, EmailTool emailTool) {
        return MethodToolCallbackProvider.builder().toolObjects(weatherStreamTool, emailTool).build();
    }
}
