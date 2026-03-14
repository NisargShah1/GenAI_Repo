import { VertexAI } from '@google-cloud/vertexai';
import { ensureAuthenticated } from './auth.js';
import * as systemTools from './system.js';

// Define the function declarations for Vertex AI
const systemToolDeclarations = [
  {
    name: "browserOpen",
    description: "Open a browser and navigate to a URL",
    parameters: {
      type: "OBJECT",
      properties: {
        url: { type: "STRING", description: "The URL to navigate to" }
      },
      required: ["url"]
    }
  },
  {
    name: "browserClick",
    description: "Click an element in the browser using a CSS selector",
    parameters: {
      type: "OBJECT",
      properties: {
        selector: { type: "STRING", description: "CSS selector of the element to click" }
      },
      required: ["selector"]
    }
  },
  {
    name: "browserType",
    description: "Type text into an element in the browser",
    parameters: {
      type: "OBJECT",
      properties: {
        selector: { type: "STRING", description: "CSS selector of the input element" },
        text: { type: "STRING", description: "Text to type" }
      },
      required: ["selector", "text"]
    }
  },
  {
    name: "browserExtract",
    description: "Extract text content from an element in the browser",
    parameters: {
      type: "OBJECT",
      properties: {
        selector: { type: "STRING", description: "CSS selector of the element to extract text from" }
      },
      required: ["selector"]
    }
  },
  {
    name: "takeScreenshot",
    description: "Take a screenshot of the current browser page",
    parameters: {
      type: "OBJECT",
      properties: {
        filepath: { type: "STRING", description: "File path to save the screenshot (e.g., screenshot.png)" }
      },
      required: ["filepath"]
    }
  },
  {
    name: "runCommand",
    description: "Execute a safe shell command on the local OS",
    parameters: {
      type: "OBJECT",
      properties: {
        cmd: { type: "STRING", description: "Shell command to execute" }
      },
      required: ["cmd"]
    }
  },
  {
    name: "openApplication",
    description: "Open a local application",
    parameters: {
      type: "OBJECT",
      properties: {
        appName: { type: "STRING", description: "Name of the application to open" }
      },
      required: ["appName"]
    }
  }
];

/**
 * Call Gemini on Google Cloud Vertex AI using the provided persona (system instruction) and prompt.
 */
export async function callGeminiVertex(personaContent, userTask) {
  await ensureAuthenticated();

  const project = process.env.GCP_PROJECT_ID;
  const location = process.env.GCP_LOCATION || 'us-central1';

  if (!project) {
    throw new Error('GCP_PROJECT_ID is required to use Vertex AI Gemini. Please set it in process.env.GCP_PROJECT_ID');
  }

  console.log(`\n🧠 Initializing Vertex AI Gemini (Project: ${project}, Location: ${location})`);

  const vertexAi = new VertexAI({ project, location });
  
  // Instantiate the model
  const generativeModel = vertexAi.preview.getGenerativeModel({
    model: 'gemini-2.5-pro', // Fallback to stable version
    systemInstruction: {
      role: 'system',
      parts: [{ text: personaContent }]
    },
    tools: [{ functionDeclarations: systemToolDeclarations }],
    generationConfig: {
      maxOutputTokens: 8192,
      temperature: 0.2,
    }
  });

  console.log(`⏳ Executing Agent Logic via Gemini 1.5 Pro...`);
  console.log('--- START RESPONSE ---\n');

  try {
    const chat = generativeModel.startChat();
    let response = await chat.sendMessage([{ text: userTask }]);

    let callCount = 0;
    const MAX_CALLS = 15;

    // Handle Function Calling Loop
    while (response.response.candidates && response.response.candidates[0].content.parts.some(p => p.functionCall)) {
      if (callCount >= MAX_CALLS) {
        console.log("\n⚠️ Max tool call limit reached. Stopping loop.");
        break;
      }
      callCount++;

      const functionCalls = response.response.candidates[0].content.parts.filter(p => p.functionCall).map(p => p.functionCall);
      const functionResponses = [];

      for (const call of functionCalls) {
        console.log(`\n**[Tool Call]** \x1b[36m${call.name}\x1b[0m(${JSON.stringify(call.args)})`);
        
        let toolResult = "";
        try {
          const args = call.args;
          if (call.name === 'browserOpen') toolResult = await systemTools.browserOpen(args.url);
          else if (call.name === 'browserClick') toolResult = await systemTools.browserClick(args.selector);
          else if (call.name === 'browserType') toolResult = await systemTools.browserType(args.selector, args.text);
          else if (call.name === 'browserExtract') toolResult = await systemTools.browserExtract(args.selector);
          else if (call.name === 'takeScreenshot') toolResult = await systemTools.takeScreenshot(args.filepath);
          else if (call.name === 'runCommand') toolResult = await systemTools.runCommand(args.cmd);
          else if (call.name === 'openApplication') toolResult = await systemTools.openApplication(args.appName);
          else toolResult = `Error: Tool ${call.name} not found locally.`;
          
          if (typeof toolResult !== 'string') {
            toolResult = JSON.stringify(toolResult);
          }
        } catch (err) {
          toolResult = `Error executing ${call.name}: ${err.message}`;
          console.error(`\x1b[31m[Tool Execution Error]\x1b[0m ${err.message}`);
        }

        console.log(`**[Tool Output]**\n${toolResult.substring(0, 300)}${toolResult.length > 300 ? '... [truncated]' : ''}`);

        functionResponses.push({
          functionResponse: {
            name: call.name,
            response: { result: toolResult }
          }
        });
      }

      // Send the actual results of the local tools back to Gemini so it can continue
      response = await chat.sendMessage(functionResponses);
    }

    // Print final natural language response text parts
    if (response.response.candidates && response.response.candidates[0].content.parts) {
       const finalParts = response.response.candidates[0].content.parts;
       for (const part of finalParts) {
         if (part.text) {
           process.stdout.write(part.text);
         }
       }
    }

    console.log('\n\n--- END RESPONSE ---');
  } catch (error) {
    console.error('\n❌ Vertex AI Execution Error:', error.message);
    if (error.message.includes('Unable to authenticate your request') || error.message.includes('Could not load the default credentials')) {
        import('./auth.js').then(auth => auth.clearCredentials());
        console.log('\nPlease run the command again to provide a new service account key.');
    }
    throw error;
  }
}
