#!/usr/bin/env node
import { Command } from 'commander';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { ensureSecrets } from '../tools/config.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const program = new Command();

program
  .name('gh-agent')
  .description('Autonomous GitHub Agent CLI')
  .version('1.0.0');

// List of required tools/keys based on the persona
const REQUIRED_SECRETS = ['GITHUB_TOKEN', 'GOOGLE_API_KEY', 'GOOGLE_SEARCH_ENGINE_ID'];
const EMAIL_SECRETS = ['GMAIL_CLIENT_ID', 'GMAIL_CLIENT_SECRET', 'GMAIL_REFRESH_TOKEN'];

program
  .command('implement')
  .description('Take a requirement and execute the autonomous development workflow.')
  .argument('<requirement>', 'The user requirement to implement')
  .action(async (requirement) => {
    // 1. Ensure secrets exist locally before doing anything else
    await ensureSecrets(REQUIRED_SECRETS);

    console.log(`\n🚀 Starting implementation for requirement: "${requirement}"\n`);
    const personaPath = path.join(__dirname, '../personas/dev-agent.md');
    
    if (fs.existsSync(personaPath)) {
      console.log(`✅ Loaded persona from dev-agent.md`);
    } else {
      console.error('❌ Error: dev-agent.md persona not found.');
      process.exit(1);
    }

    console.log("Step 1: Requirement Understanding...");
    console.log("Step 2: Repository Analysis...");
    console.log("Step 3: Implementation Strategy...");
    console.log("...");
    console.log("✅ Execution loop initialized. (Agent logic pending implementation)");
  });

program
  .command('persona')
  .description('Execute a specific persona against a task.')
  .argument('<name>', 'Name of the persona file (without .md)')
  .argument('<task>', 'The task to execute')
  .action(async (name, task) => {
    // Ensure appropriate secrets depending on the persona
    if (name === 'email-assistant') {
      await ensureSecrets(EMAIL_SECRETS);
    } else {
      await ensureSecrets(REQUIRED_SECRETS);
    }

    console.log(`\n🎭 Executing persona: "${name}" for task: "${task}"\n`);
    const personaPath = path.join(__dirname, `../personas/${name}.md`);
    
    if (fs.existsSync(personaPath)) {
      console.log(`✅ Loaded persona from ${name}.md`);
    } else {
      console.error(`❌ Error: ${name}.md persona not found.`);
      process.exit(1);
    }
  });

program.parse(process.argv);
