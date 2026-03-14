#!/usr/bin/env node
import { Command } from 'commander';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { ensureSecrets } from '../tools/config.js';
import { callGeminiVertex } from '../tools/gemini.js';
import { callOllama } from '../tools/ollama.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const program = new Command();

program
  .name('gh-agent')
  .description('Autonomous GitHub Agent CLI (with Gemini Vertex AI and local Ollama support)')
  .version('1.0.0')
  .option('-p, --provider <type>', 'LLM Provider (copilot, vertex, ollama)', 'copilot')
  .option('-m, --model <name>', 'Model name for local Ollama execution (e.g., phi3, llama3)', 'phi3');

const REQUIRED_SECRETS = ['GITHUB_TOKEN', 'GOOGLE_API_KEY', 'GOOGLE_SEARCH_ENGINE_ID'];
const EMAIL_SECRETS = ['GMAIL_CLIENT_ID', 'GMAIL_CLIENT_SECRET', 'GMAIL_REFRESH_TOKEN'];
const VERTEX_SECRETS = ['GCP_PROJECT_ID']; // Expects standard gcloud ADC to be present
const LINKEDIN_SECRETS = ['LINKEDIN_ACCESS_TOKEN'];

program
  .command('implement')
  .description('Take a requirement and execute the autonomous development workflow.')
  .argument('<requirement>', 'The user requirement to implement')
  .action(async (requirement) => {
    const opts = program.opts();

    // 1. Ensure secrets exist locally depending on the selected provider
    if (opts.provider === 'vertex') {
      await ensureSecrets([...REQUIRED_SECRETS, ...VERTEX_SECRETS]);
    } else if (opts.provider === 'copilot') {
      await ensureSecrets(REQUIRED_SECRETS);
    }
    // Note: ollama running locally usually doesn't require cloud API keys just to init the chat, 
    // but tools might need them. Keeping it simple for now, we only enforce on vertex/copilot.

    console.log(`\n🚀 Starting implementation for requirement: "${requirement}"\nProvider: ${opts.provider}\n`);
    const personaPath = path.join(__dirname, '../personas/dev-agent.md');
    
    if (fs.existsSync(personaPath)) {
      console.log(`✅ Loaded persona from dev-agent.md`);
    } else {
      console.error('❌ Error: dev-agent.md persona not found.');
      process.exit(1);
    }

    const personaContent = fs.readFileSync(personaPath, 'utf8');

    if (opts.provider === 'vertex') {
      await callGeminiVertex(personaContent, requirement);
    } else if (opts.provider === 'ollama') {
      await callOllama(personaContent, requirement, opts.model);
    } else {
      console.log("Step 1: Requirement Understanding...");
      console.log("Step 2: Repository Analysis...");
      console.log("Step 3: Implementation Strategy...");
      console.log("...");
      console.log("✅ Execution loop initialized. (Copilot logic handled via extensions/MCP)");
    }
  });

program
  .command('persona')
  .description('Execute a specific persona against a task.')
  .argument('<name>', 'Name of the persona file (without .md)')
  .argument('<task>', 'The task to execute')
  .action(async (name, task) => {
    const opts = program.opts();
    
    // Aggregate required secrets based on persona and provider
    let secretsToEnsure = [];
    if (name === 'email-assistant') {
      secretsToEnsure = [...EMAIL_SECRETS];
    } else if (name === 'linkedin-agent') {
      secretsToEnsure = [...LINKEDIN_SECRETS];
    } else {
      secretsToEnsure = [...REQUIRED_SECRETS];
    }

    if (opts.provider === 'vertex') {
      secretsToEnsure.push(...VERTEX_SECRETS);
    }

    if (opts.provider !== 'ollama') {
        // Only rigidly block on secrets if we are not running a local test.
        await ensureSecrets(secretsToEnsure);
    }

    console.log(`\n🎭 Executing persona: "${name}" for task: "${task}"\nProvider: ${opts.provider}\n`);
    const personaPath = path.join(__dirname, `../personas/${name}.md`);
    
    if (fs.existsSync(personaPath)) {
      console.log(`✅ Loaded persona from ${name}.md`);
    } else {
      console.error(`❌ Error: ${name}.md persona not found.`);
      process.exit(1);
    }

    const personaContent = fs.readFileSync(personaPath, 'utf8');

    if (opts.provider === 'vertex') {
      await callGeminiVertex(personaContent, task);
    } else if (opts.provider === 'ollama') {
      await callOllama(personaContent, task, opts.model);
    } else {
      console.log("✅ Execution loop initialized. (Copilot logic handled via extensions/MCP)");
    }
  });

program.parse(process.argv);