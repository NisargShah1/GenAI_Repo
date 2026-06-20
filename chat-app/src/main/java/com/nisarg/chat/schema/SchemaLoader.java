package com.nisarg.chat.schema;

import com.nisarg.chat.dto.SchemaDefinition;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.io.Resource;
import org.springframework.core.io.ResourceLoader;
import org.springframework.stereotype.Service;
import org.springframework.util.FileCopyUtils;

import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class SchemaLoader {

    private final ResourceLoader resourceLoader;
    private final List<SchemaDefinition> schemas = new ArrayList<>();

    @PostConstruct
    public void loadSchemas() {
        try {
            Resource resource = resourceLoader.getResource("classpath:schemas/mongo-schema");
            if (!resource.exists()) {
                log.warn("Schema file not found at classpath:schemas/mongo-schema");
                return;
            }

            String content = FileCopyUtils
                    .copyToString(new InputStreamReader(resource.getInputStream(), StandardCharsets.UTF_8));
            parseSchemas(content);
        } catch (IOException e) {
            log.error("Failed to load schemas", e);
        }
    }

    private void parseSchemas(String content) {
        // Split by "Collection Name:"
        String[] parts = content.split("Collection Name:");
        for (String part : parts) {
            String trimmed = part.trim();
            if (trimmed.isEmpty())
                continue;

            // Find the start of the JSON block
            int firstBrace = trimmed.indexOf('{');
            if (firstBrace == -1) {
                log.warn("Skipping invalid schema section (no JSON found): {}", trimmed);
                continue;
            }

            String collectionName = trimmed.substring(0, firstBrace).trim();
            String jsonContent = trimmed.substring(firstBrace).trim();

            // Handle potential trailing dot from copy-paste
            if (jsonContent.endsWith(".")) {
                jsonContent = jsonContent.substring(0, jsonContent.length() - 1).trim();
            }

            log.info("Loaded schema for collection: {}", collectionName);
            schemas.add(new SchemaDefinition(collectionName, jsonContent));
        }
    }

    public List<SchemaDefinition> getSchemas() {
        return Collections.unmodifiableList(schemas);
    }

    public String getAllSchemasAsString() {
        StringBuilder sb = new StringBuilder();
        for (SchemaDefinition sd : schemas) {
            sb.append("Collection: ").append(sd.getCollectionName()).append("\n");
            sb.append(sd.getJsonSchema()).append("\n\n");
        }
        return sb.toString();
    }
}
