import ollama from 'ollama';
import * as systemTools from './system.js';
import * as gmailTools from './gmail.js';
import * as orchestratorTools from './orchestrator.js';

// Ollama tool schemas (OpenAI compatible)
const ollamaTools = [
  {
    type: "function",
    function: {
      name: "createPersona",
      description: "Creates a new specialized persona markdown file dynamically.",
      parameters: {
        type: "object",
        properties: {
          name: { type: "string", description: "The name of the persona (e.g., 'db-expert')" },
          content: { type: "string", description: "The markdown content defining the persona's role and rules." }
        },
        required: ["name", "content"]
      }
    }
  },
  {
    type: "function",
    function: {
      name: "spawnSubAgent",
      description: "Spawns a background process running the CLI with the specified persona and task.",
      parameters: {
        type: "object",
        properties: {
          personaName: { type: "string", description: "The name of the persona file (without .md)" },
          task: { type: "string", description: "The task for the sub-agent to execute" }
        },
        required: ["personaName", "task"]
      }
    }
  }
];

export async function callOllama(personaContent, userTask, modelName = 'phi3') {
  console.log(`\n🦙 Initializing Local Ollama (Model: ${modelName})`);
  console.log(`⏳ Executing Agent Logic...`);
  console.log('--- START RESPONSE ---\n');

  let messages = [
    { role: 'system', content: personaContent },
    { role: 'user', content: userTask }
  ];

  try {
    let callCount = 0;
    const MAX_CALLS = 10;

    while (callCount < MAX_CALLS) {
      callCount++;
      
      const response = await ollama.chat({
        model: modelName,
        messages: messages,
        tools: ollamaTools,
      });

      const message = response.message;
      messages.push(message);

      if (message.content) {
        process.stdout.write(message.content + '\n');
      }

      if (!message.tool_calls || message.tool_calls.length === 0) {
        break; // No more tool calls
      }

      for (const toolCall of message.tool_calls) {
        const name = toolCall.function.name;
        const args = toolCall.function.arguments;
        
        console.log(`\n**[Tool Call]** \x1b[36m${name}\x1b[0m(${JSON.stringify(args)})`);
        let toolResult = "";
        
        try {
          if (name === 'createPersona') toolResult = orchestratorTools.createPersona(args.name, args.content);
          else if (name === 'spawnSubAgent') toolResult = await orchestratorTools.spawnSubAgent(args.personaName, args.task);
          else toolResult = `Error: Tool ${name} not found locally.`;
          
          if (typeof toolResult !== 'string') toolResult = JSON.stringify(toolResult);
        } catch (err) {
          toolResult = `Error executing ${name}: ${err.message}`;
          console.error(`\x1b[31m[Tool Execution Error]\x1b[0m ${err.message}`);
        }

        console.log(`**[Tool Output]**\n${toolResult.substring(0, 300)}${toolResult.length > 300 ? '... [truncated]' : ''}`);

        messages.push({
          role: 'tool',
          content: toolResult,
          name: name
        });
      }
    }

    console.log('\n\n--- END RESPONSE ---');
  } catch (error) {
    console.error('\n❌ Ollama Execution Error:', error.message);
    console.log(`💡 Tip: Ensure Ollama is running ('ollama serve') and the model is pulled ('ollama pull ${modelName}').`);
    throw error;
  }
}
