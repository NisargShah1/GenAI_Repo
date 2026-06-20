package com.nisarg.chat.prompt;

import com.nisarg.chat.schema.SchemaLoader;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class PromptBuilder {

  private final SchemaLoader schemaLoader;

  private static final String PROMPT_TEMPLATE = """
      You are a MongoDB aggregation expert.

      Available collections and schemas:
      %s

      Rules:
      - Output ONLY valid JSON
      - Do NOT include explanations outside JSON
      - Use MongoDB aggregation pipeline syntax
      - Do NOT use $out or $merge
      - If the query cannot be answered with the available schema, return an empty pipeline and explanation in parsing.

      User Query:
      "%s"

      Output JSON format:
      {
        "collection": "<collection_name>",
        "pipeline": [ <MongoDB Aggregation Stages> ],
        "outputType": "TEXT | TABLE | CHART",
        "chart": {
          "type": "bar | line | pie",
          "x": "<field>",
          "y": "<field>"
        }
      }
      """;

  private static final String EXPLANATION_PROMPT_TEMPLATE = """
      You are a data analyst. Explain the following data result in response to the user's query.

      User Query:
      "%s"

      Data Result (from MongoDB Aggregation):
      %s

      Provide a clear, concise, and human-readable explanation of what this data means.
      If data is not proper format then reformat as required.
      """;

  public String buildPrompt(String userQuery) {
    String schemaContext = schemaLoader.getAllSchemasAsString();
    return String.format(PROMPT_TEMPLATE, schemaContext, userQuery);
  }

  public String buildExplanationPrompt(String userQuery, String dataResult) {
    return String.format(EXPLANATION_PROMPT_TEMPLATE, userQuery, dataResult);
  }
}
