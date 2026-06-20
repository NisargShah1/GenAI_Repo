package com.data.extract.docloader;

import ai.onnxruntime.*;
import net.sourceforge.tess4j.Tesseract;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.rendering.PDFRenderer;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

import com.google.cloud.vertexai.VertexAI;
import com.google.cloud.vertexai.api.GenerateContentResponse;
import com.google.cloud.vertexai.generativeai.ContentMaker;
import com.google.cloud.vertexai.generativeai.GenerativeModel;
import com.google.cloud.vertexai.generativeai.PartMaker;
import com.google.cloud.vertexai.generativeai.ResponseHandler;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;

public class PdfImageTextExtractor {

    private static final String TESSDATA_PATH = "C:\\Program Files\\Tesseract-OCR\\tessdata";
    private static final String MODEL_PATH = "C:\\models\\model.onnx";

    private static final ExecutorService executor = Executors.newFixedThreadPool(5);

    public static String extract(PDDocument document) throws IOException {
        StringBuilder extractedText = new StringBuilder();

        try (OrtEnvironment env = OrtEnvironment.getEnvironment();
                OrtSession session = env.createSession(MODEL_PATH, new OrtSession.SessionOptions())) {

            List<Callable<PageResult>> tasks = new ArrayList<>();

            for (int page = 0; page < document.getNumberOfPages(); page++) {
                final int pageIndex = page;
                tasks.add(() -> processPage(document, pageIndex, session, env));
            }

            try {
                List<Future<PageResult>> futures = executor.invokeAll(tasks);
                List<PageResult> results = new ArrayList<>();
                for (Future<PageResult> future : futures) {
                    results.add(future.get());
                }

                // Sort by page index to maintain order
                Collections.sort(results, (r1, r2) -> Integer.compare(r1.pageIndex, r2.pageIndex));

                for (PageResult result : results) {
                    extractedText.append("Page ").append(result.pageIndex + 1).append(" [").append(result.type)
                            .append("]:\n");
                    extractedText.append(result.text).append("\n\n");
                }

            } catch (InterruptedException | java.util.concurrent.ExecutionException e) {
                throw new IOException("Error during parallel PDF extraction", e);
            } finally {
                executor.shutdown();
                try {
                    if (!executor.awaitTermination(300, TimeUnit.SECONDS)) {
                        executor.shutdownNow();
                    }
                } catch (InterruptedException ex) {
                    executor.shutdownNow();
                    Thread.currentThread().interrupt();
                }
            }

        } catch (Exception e) {
            throw new IOException("Error running OCR pipeline", e);
        } finally {
            document.close();
        }

        return extractedText.toString();
    }

    private static String detectTextType(OrtSession session, OrtEnvironment env, BufferedImage image) {
        try {
            // 1. Preprocess: Resize to 600x1000 (Width x Height) as expected by the model
            // Error indicated Expected: 1000 (Index 2/Height), Expected: 600 (Index
            // 3/Width)
            BufferedImage resized = resize(image, 600, 1000);

            // 2. Convert to Tensor (NCHW format: [1, 3, 1000, 600])
            // Assuming model expects normalized floats 0.0-1.0 or similar.
            // Adjust normalization (mean/std) based on your specific training.
            float[][][][] inputData = imageToTensorData(resized);

            try (OnnxTensor inputTensor = OnnxTensor.createTensor(env, inputData)) {
                // 3. Run Inference
                // We assume the first input node is the image input
                String inputName = session.getInputNames().iterator().next();
                OrtSession.Result result = session.run(Collections.singletonMap(inputName, inputTensor));

                // 4. Process Output
                // Assuming output is [1, 2] (logits or probabilities)
                // Index 0: Printed, Index 1: Handwritten (Adjust based on model)
                float[][] output = (float[][]) result.get(0).getValue();

                float printedScore = output[0][0];
                float handwrittenScore = output[0][1];

                return handwrittenScore > printedScore ? "Handwritten" : "Printed";
            }
        } catch (Exception e) {
            System.err.println("Classification failed, defaulting to Printed: " + e.getMessage());
            e.printStackTrace();
            return "Printed";
        }
    }

    private static BufferedImage resize(BufferedImage img, int newW, int newH) {
        Image tmp = img.getScaledInstance(newW, newH, Image.SCALE_SMOOTH);
        BufferedImage dimg = new BufferedImage(newW, newH, BufferedImage.TYPE_INT_RGB);
        Graphics2D g2d = dimg.createGraphics();
        g2d.drawImage(tmp, 0, 0, null);
        g2d.dispose();
        return dimg;
    }

    private static float[][][][] imageToTensorData(BufferedImage image) {
        int width = image.getWidth();
        int height = image.getHeight();
        float[][][][] data = new float[1][3][height][width];

        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                int rgb = image.getRGB(x, y);
                // Extract channels
                float r = ((rgb >> 16) & 0xFF) / 255.0f;
                float g = ((rgb >> 8) & 0xFF) / 255.0f;
                float b = (rgb & 0xFF) / 255.0f;

                // NCHW layout
                data[0][0][y][x] = r; // Red
                data[0][1][y][x] = g; // Green
                data[0][2][y][x] = b; // Blue
            }
        }
        return data;
    }

    private static String runGeminiVisionOCR(File imageFile) throws IOException {
        // TODO: Configure these via environment variables or properties
        String projectId = System.getenv("GOOGLE_CLOUD_PROJECT");
        if (projectId == null) {
            // Fallback for local development if env var not set
            // User must ensure they have 'gcloud auth application-default login' set up
            projectId = "your-project-id";
        }
        String location = "us-central1"; // "asia-south1"; //
        String modelName = "gemini-2.5-flash-lite";

        try (VertexAI vertexAI = new VertexAI(projectId, location)) {
            GenerativeModel model = new GenerativeModel(modelName, vertexAI);

            byte[] imageBytes = java.nio.file.Files.readAllBytes(imageFile.toPath());

            var content = ContentMaker.fromMultiModalData(
                    "Transcribe the handwritten text in this image exactly as it appears. Do not add any markdown formatting or commentary.",
                    PartMaker.fromMimeTypeAndData("image/png", imageBytes));

            GenerateContentResponse response = model.generateContent(content);
            return ResponseHandler.getText(response);
        } catch (Exception e) {
            throw new IOException("Gemini API call failed", e);
        }
    }

    private static PageResult processPage(PDDocument document, int pageIndex, OrtSession session, OrtEnvironment env)
            throws IOException {
        // PDFRenderer is not thread-safe for the same document, so we need to
        // synchronize access to it or create a new one per thread?
        // Actually, PDFRenderer is NOT thread-safe for concurrency on same document.
        // Safer to synchronize the rendering part or use a lock.
        // However, standard PDFBox PDFRenderer usage might have issues if document is
        // accessed concurrently.
        // We will synchronize on document to be safe for rendering.

        BufferedImage image;
        synchronized (document) {
            PDFRenderer renderer = new PDFRenderer(document);
            image = renderer.renderImageWithDPI(pageIndex, 300);
        }

        File tempImage = new File("page_" + pageIndex + "_" + Thread.currentThread().getId() + ".png");
        ImageIO.write(image, "png", tempImage);

        try {
            // Detect handwriting or printed
            String type = detectTextType(session, env, image);
            System.out.println("Page " + (pageIndex + 1) + " classified as: " + type);

            String text;
            if ("Handwritten".equals(type)) {
                text = runGeminiVisionOCR(tempImage);
            } else {
                // Tesseract instance might need to be thread safe. Tesseract class is generally
                // thread safe IF different instances are used or if underlying C API handles
                // it.
                // To be safe we should probably create Tesseract instance per thread or
                // synchronize.
                // But the passed 'tesseract' object is shared.
                // Let's create a local instance or synchronize.
                // Best practice with Tess4J: create new instance or pool them.
                // We'll create a new lightweight instance here reusing datapath
                Tesseract localTesseract = new Tesseract();
                localTesseract.setDatapath(TESSDATA_PATH);
                localTesseract.setLanguage("eng");
                text = localTesseract.doOCR(tempImage);
            }
            return new PageResult(pageIndex, type, text);
        } catch (Exception e) {
            throw new IOException("Failed to process page " + pageIndex, e);
        } finally {
            if (tempImage.exists()) {
                tempImage.delete();
            }
        }
    }

    private static class PageResult {
        int pageIndex;
        String type;
        String text;

        public PageResult(int pageIndex, String type, String text) {
            this.pageIndex = pageIndex;
            this.type = type;
            this.text = text;
        }
    }
}
