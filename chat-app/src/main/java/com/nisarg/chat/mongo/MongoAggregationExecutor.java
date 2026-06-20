package com.nisarg.chat.mongo;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.bson.Document;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.aggregation.Aggregation;
import org.springframework.data.mongodb.core.aggregation.AggregationOperation;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class MongoAggregationExecutor {

    private final MongoTemplate mongoTemplate;

    public List<Document> execute(String collectionName, List<Map<String, Object>> pipeline) {
        log.info("Executing aggregation on collection: {}", collectionName);

        // Convert raw JSON pipeline stages to AggregationOperations
        // Check for read-only safety? (Ideally yes, but for now trusting the prompt
        // rules)

        List<AggregationOperation> operations = pipeline.stream()
                .map(json -> (AggregationOperation) context -> new Document(json))
                .collect(Collectors.toList());

        Aggregation aggregation = Aggregation.newAggregation(operations);

        try {
            return mongoTemplate.aggregate(aggregation, collectionName, Document.class).getMappedResults();
        } catch (Exception e) {
            log.error("Aggregation execution failed", e);
            throw new RuntimeException("Aggregation failed: " + e.getMessage(), e);
        }
    }
}
