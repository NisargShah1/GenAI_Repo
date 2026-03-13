import fs from 'fs';
import path from 'path';
import os from 'os';
import inquirer from 'inquirer';

const SECRETS_FILE = path.join(os.homedir(), '.copilot-agent-secrets.json');

export function getSecrets() {
  if (fs.existsSync(SECRETS_FILE)) {
    try {
      return JSON.parse(fs.readFileSync(SECRETS_FILE, 'utf8'));
    } catch (e) {
      return {};
    }
  }
  return {};
}

export function saveSecrets(secrets) {
  // Save with restricted permissions (read/write for owner only)
  fs.writeFileSync(SECRETS_FILE, JSON.stringify(secrets, null, 2), { mode: 0o600 });
}

/**
 * Ensures that the required secrets exist. If not, prompts the user interactively.
 * @param {string[]} requiredKeys Array of required environment variable names.
 */
export async function ensureSecrets(requiredKeys) {
  let secrets = getSecrets();
  let updated = false;

  for (const key of requiredKeys) {
    if (!secrets[key] && !process.env[key]) {
      console.log(`\n🔑 Missing required secret: ${key}`);
      const answers = await inquirer.prompt([
        {
          type: 'password',
          name: key,
          message: `Please enter your ${key}:`,
          mask: '*'
        }
      ]);
      secrets[key] = answers[key].trim();
      updated = true;
    }
  }

  if (updated) {
    saveSecrets(secrets);
    console.log(`✅ Secrets securely saved locally to ${SECRETS_FILE}`);
  }

  // Inject secrets into process.env so tools can access them transparently
  for (const [k, v] of Object.entries(secrets)) {
    if (!process.env[k]) {
      process.env[k] = v;
    }
  }
}
