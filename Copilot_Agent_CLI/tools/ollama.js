import ollama from 'ollama';

/**
 * Call a locally hosted LLM via Ollama using the provided persona (system instruction) and prompt.
 * 
 * Assumes the Ollama daemon is running locally (e.g., http://127.0.0.1:11434)
 * and the requested model has been pulled (e.g., `ollama pull phi3`).
 */
export async function callOllama(personaContent, userTask, modelName = 'phi3') {
  console.log(`\n🦙 Initializing Local Ollama (Model: ${modelName})`);
  console.log(`⏳ Executing Agent Logic...`);
  console.log('--- START RESPONSE ---\n');

  try {
    const response = await ollama.chat({
      model: modelName,
      messages: [
        { role: 'system', content: personaContent },
        { role: 'user', content: userTask }
      ],
      stream: true,
    });

    let fullResponse = '';
    for await (const part of response) {
      if (part.message && part.message.content) {
        process.stdout.write(part.message.content);
        fullResponse += part.message.content;
      }
    }
    console.log('\n\n--- END RESPONSE ---');
    return fullResponse;
  } catch (error) {
    console.error('\n❌ Ollama Execution Error:', error.message);
    console.log(`💡 Tip: Ensure Ollama is running ('ollama serve') and the model is pulled ('ollama pull ${modelName}').`);
    throw error;
  }
}
