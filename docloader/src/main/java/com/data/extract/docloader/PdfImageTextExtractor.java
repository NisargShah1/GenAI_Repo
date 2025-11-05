package com.data.extract.docloader;

import ai.onnxruntime.*;
import net.sourceforge.tess4j.Tesseract;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.rendering.PDFRenderer;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;

public class PdfImageTextExtractor {

    private static final String TESSDATA_PATH = "C:\\Program Files\\Tesseract-OCR\\tessdata";
    private static final String MODEL_PATH = "C:\\models\\model.onnx";

    public static String extract(PDDocument document) throws IOException {
        StringBuilder extractedText = new StringBuilder();

        try (OrtEnvironment env = OrtEnvironment.getEnvironment();
             OrtSession session = env.createSession(MODEL_PATH, new OrtSession.SessionOptions())) {

            PDFRenderer renderer = new PDFRenderer(document);
            Tesseract tesseract = new Tesseract();
            tesseract.setDatapath(TESSDATA_PATH);
            tesseract.setLanguage("eng");

            for (int page = 0; page < document.getNumberOfPages(); page++) {
                BufferedImage image = renderer.renderImageWithDPI(page, 300);
                File tempImage = new File("page_" + page + ".png");
                ImageIO.write(image, "png", tempImage);

                // Detect handwriting or printed
                String type = detectTextType(session, env, image);
                System.out.println("Page " + (page + 1) + " classified as: " + type);

                String text;
                if ("Handwritten".equals(type)) {
                    text = runHandwrittenPythonOCR(tempImage);
                } else {
                    text = tesseract.doOCR(tempImage);
                }

                extractedText.append("Page ").append(page + 1).append(" [").append(type).append("]:\n");
                extractedText.append(text).append("\n\n");

                tempImage.delete();
            }

        } catch (Exception e) {
            throw new IOException("Error running OCR pipeline", e);
        } finally {
            document.close();
        }

        return extractedText.toString();
    }

    private static String detectTextType(OrtSession session, OrtEnvironment env, BufferedImage image) {
        //ML to classify between handwritten and printed can be implemented here
        return "Printed";
    }

    private static String runHandwrittenPythonOCR(File imageFile) throws IOException, InterruptedException {
        ProcessBuilder pb = new ProcessBuilder("python", "C:\\scripts\\handwritten_ocr.py", imageFile.getAbsolutePath());
        pb.redirectErrorStream(true);
        Process process = pb.start();

        StringBuilder output = new StringBuilder();
        try (var reader = new java.io.BufferedReader(new java.io.InputStreamReader(process.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }
        }
        int exitCode = process.waitFor();
        if (exitCode != 0) {
            throw new IOException("Python OCR script failed with code " + exitCode);
        }
        return output.toString().trim();
    }

}
