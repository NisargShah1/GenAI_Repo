#!/usr/bin/env node
import { Command } from 'commander';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { ensureSecrets } from '../tools/config.js';
import { callGeminiVertex } from '../tools/gemini.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const program = new Command();

program
  .name('gh-agent')
  .description('Autonomous GitHub Agent CLI (with Gemini Vertex AI support)')
  .version('1.0.0')
  .option('-p, --provider <type>', 'LLM Provider (copilot, vertex)', 'copilot');

const REQUIRED_SECRETS = ['GITHUB_TOKEN', 'GOOGLE_API_KEY', 'GOOGLE_SEARCH_ENGINE_ID'];
const EMAIL_SECRETS = ['GMAIL_CLIENT_ID', 'GMAIL_CLIENT_SECRET', 'GMAIL_REFRESH_TOKEN'];
const VERTEX_SECRETS = ['GCP_PROJECT_ID']; // Expects standard gcloud ADC to be present

program
  .command('implement')
  .description('Take a requirement and execute the autonomous development workflow.')
  .argument('<requirement>', 'The user requirement to implement')
  .action(async (requirement) => {
    const opts = program.opts();

    // 1. Ensure secrets exist locally depending on the selected provider
    if (opts.provider === 'vertex') {
      await ensureSecrets([...REQUIRED_SECRETS, ...VERTEX_SECRETS]);
    } else {
      await ensureSecrets(REQUIRED_SECRETS);
    }

    console.log(`\n🚀 Starting implementation for requirement: "${requirement}"\nProvider: ${opts.provider}\n`);
    const personaPath = path.join(__dirname, '../personas/dev-agent.md');
    
    if (fs.existsSync(personaPath)) {
      console.log(`✅ Loaded persona from dev-agent.md`);
    } else {
      console.error('❌ Error: dev-agent.md persona not found.');
      process.exit(1);
    }

    if (opts.provider === 'vertex') {
      const personaContent = fs.readFileSync(personaPath, 'utf8');
      await callGeminiVertex(personaContent, requirement);
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
    
    // Aggregate required secrets
    let secretsToEnsure = [];
    if (name === 'email-assistant') {
      secretsToEnsure = [...EMAIL_SECRETS];
    } else {
      secretsToEnsure = [...REQUIRED_SECRETS];
    }

    if (opts.provider === 'vertex') {
      secretsToEnsure.push(...VERTEX_SECRETS);
    }

    await ensureSecrets(secretsToEnsure);

    console.log(`\n🎭 Executing persona: "${name}" for task: "${task}"\nProvider: ${opts.provider}\n`);
    const personaPath = path.join(__dirname, `../personas/${name}.md`);
    
    if (fs.existsSync(personaPath)) {
      console.log(`✅ Loaded persona from ${name}.md`);
    } else {
      console.error(`❌ Error: ${name}.md persona not found.`);
      process.exit(1);
    }

    if (opts.provider === 'vertex') {
      const personaContent = fs.readFileSync(personaPath, 'utf8');
      await callGeminiVertex(personaContent, task);
    } else {
      console.log("✅ Execution loop initialized. (Copilot logic handled via extensions/MCP)");
    }
  });

program.parse(process.argv);
