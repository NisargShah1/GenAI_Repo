package com.nisarg.chat.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class SchemaDefinition {
    private String collectionName;
    private String jsonSchema;
}
