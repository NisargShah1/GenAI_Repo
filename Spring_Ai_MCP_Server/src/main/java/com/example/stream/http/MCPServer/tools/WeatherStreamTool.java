package com.example.stream.http.MCPServer.tools;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.stereotype.Service;

@Service
public class WeatherStreamTool {


    @Tool(description = """ 
            Get the current weather for a specific location.
            input params:
            location: city name in string format
            """)
    public String getCurrentWeather(String location) {
        // In a real application, this would call a weather API.
        // For this example, a mock response is returned.
        if (location.equalsIgnoreCase("New York")) {
            return "The current temperature in New York is 25°C and sunny.";
        }else if(location.equalsIgnoreCase("Pune"))
            return "The current temperature in Pune is 27°C.";
        return "I could not retrieve the weather for that location.";
    }
}
