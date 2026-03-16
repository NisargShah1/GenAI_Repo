import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PERSONAS_DIR = path.join(__dirname, '../personas');

/**
 * Creates a new specialized persona markdown file dynamically.
 * @param {string} name - The name of the persona (e.g., "db-expert").
 * @param {string} content - The markdown content defining the persona's role and rules.
 * @returns {string} Status message.
 */
export function createPersona(name, content) {
  if (!fs.existsSync(PERSONAS_DIR)) {
    fs.mkdirSync(PERSONAS_DIR, { recursive: true });
  }
  
  const filePath = path.join(PERSONAS_DIR, `${name}.md`);
  fs.writeFileSync(filePath, content, 'utf8');
  return `✅ Successfully created specialized persona: ${name} at ${filePath}`;
}

/**
 * Spawns a background process running the Copilot Agent CLI with the specified persona and task.
 * @param {string} personaName - The name of the persona file (without .md).
 * @param {string} task - The task for the sub-agent to execute.
 * @returns {Promise<string>} The output from the sub-agent execution.
 */
export async function spawnSubAgent(personaName, task) {
  return new Promise((resolve, reject) => {
    const cliPath = path.join(__dirname, '../cli/index.js');
    console.log(`\n🤖 Orchestrator spawning sub-agent: [${personaName}] for task: "${task}"...`);
    
    // Forward the provider and model from the parent process to the sub-agent
    const args = ['persona', personaName, task];
    
    const providerIndex = process.argv.findIndex(arg => arg === '-p' || arg === '--provider');
    if (providerIndex !== -1 && process.argv.length > providerIndex + 1) {
      args.push('-p', process.argv[providerIndex + 1]);
    }
    
    const modelIndex = process.argv.findIndex(arg => arg === '-m' || arg === '--model');
    if (modelIndex !== -1 && process.argv.length > modelIndex + 1) {
      args.push('-m', process.argv[modelIndex + 1]);
    }
    
    // Spawn the sub-agent as a child process of the orchestrator
    const child = spawn('node', [cliPath, ...args]);
    
    let output = '';
    
    child.stdout.on('data', (data) => {
      const str = data.toString();
      output += str;
      // Optionally stream the sub-agent's output to the console for real-time tracking
      process.stdout.write(`\x1b[36m[${personaName}]\x1b[0m ${str}`);
    });
    
    child.stderr.on('data', (data) => {
      const str = data.toString();
      output += str;
      process.stderr.write(`\x1b[31m[${personaName} ERROR]\x1b[0m ${str}`);
    });
    
    child.on('close', (code) => {
      if (code === 0) {
        resolve(`✅ Sub-agent [${personaName}] completed successfully.\nOutput:\n${output}`);
      } else {
        reject(new Error(`❌ Sub-agent [${personaName}] failed with exit code ${code}.\nOutput:\n${output}`));
      }
    });
  });
}
