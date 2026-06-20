package com.data.extract.docloader.controller;

import com.data.extract.docloader.PdfImageTextExtractor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.http.ResponseEntity;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.RestController;
import java.io.IOException;
import java.util.Map;

import org.apache.pdfbox.pdmodel.PDDocument;

@RestController
@RequestMapping("/api/docs")
public class DocController {

    @PostMapping(value = "/extract-text", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<Map> extractTextFromPdf(@RequestParam("file") MultipartFile file) {
        if (file.isEmpty() || !file.getOriginalFilename().endsWith(".pdf")) {
            throw new RuntimeException("Please upload a valid PDF file.");
        }
        try (PDDocument document = PDDocument.load(file.getInputStream())) {
            String text = PdfImageTextExtractor.extract(document);
            Map<String, String> map = Map.of("extractedText", text);
            return ResponseEntity.ok(map);
        } catch (IOException e) {
            e.printStackTrace();
            throw new RuntimeException("Please upload a valid PDF file." + e.getMessage());
        }
    }
}
