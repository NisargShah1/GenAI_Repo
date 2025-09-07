package com.example.stream.http.MCPServer.tools;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.stereotype.Service;


@Service
public class EmailTool {

    private static final Logger log = LoggerFactory.getLogger(EmailTool.class);

    @Tool(description = """ 
            Send Email.
            input params:
            recipient: email Id of recipient in string format
            subject: subject of email in string
            body: email body in string format
            """)
    public String sendEmail(String recipient, String subject,String body) {
        // In a real application, this would call an email sender.
        // For this example, a mock response is returned.
        String response = "Email sent to: "+ recipient +" with message:"+body;
        log.info(response);
        return response;
    }
}
