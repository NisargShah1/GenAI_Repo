import { VertexAI } from '@google-cloud/vertexai';

/**
 * Call Gemini on Google Cloud Vertex AI using the provided persona (system instruction) and prompt.
 * 
 * Assumes Application Default Credentials (ADC) are configured, or GOOGLE_APPLICATION_CREDENTIALS is set,
 * and that GCP_PROJECT_ID is provided via ~/.copilot-agent-secrets.json or process.env.
 */
export async function callGeminiVertex(personaContent, userTask) {
  const project = process.env.GCP_PROJECT_ID;
  const location = process.env.GCP_LOCATION || 'us-central1';

  if (!project) {
    throw new Error('GCP_PROJECT_ID is required to use Vertex AI Gemini.');
  }

  console.log(`\n🧠 Initializing Vertex AI Gemini (Project: ${project}, Location: ${location})`);

  const vertexAi = new VertexAI({ project, location });
  
  // Instantiate the models
  const generativeModel = vertexAi.preview.getGenerativeModel({
    model: 'gemini-1.5-pro',
    systemInstruction: {
      role: 'system',
      parts: [{ text: personaContent }]
    },
    generationConfig: {
      maxOutputTokens: 8192,
      temperature: 0.2,
    }
  });

  console.log(`⏳ Executing Agent Logic via Gemini 1.5 Pro...`);
  console.log('--- START RESPONSE ---\n');

  try {
    const request = {
      contents: [
        { role: 'user', parts: [{ text: userTask }] }
      ],
    };

    const streamingResp = await generativeModel.generateContentStream(request);
    
    let fullResponse = '';
    for await (const item of streamingResp.stream) {
      if (item.candidates && item.candidates[0] && item.candidates[0].content.parts[0].text) {
        const textChunk = item.candidates[0].content.parts[0].text;
        process.stdout.write(textChunk);
        fullResponse += textChunk;
      }
    }
    console.log('\n\n--- END RESPONSE ---');
    return fullResponse;
  } catch (error) {
    console.error('\n❌ Vertex AI Execution Error:', error.message);
    throw error;
  }
}
