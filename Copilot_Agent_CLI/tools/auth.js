import Conf from 'conf';
import inquirer from 'inquirer';
import fs from 'fs';
import path from 'path';

const config = new Conf({
  projectName: 'copilot-agent-cli',
  defaults: {
    GOOGLE_APPLICATION_CREDENTIALS: null
  }
});

export async function ensureAuthenticated() {
  let credPath = config.get('GOOGLE_APPLICATION_CREDENTIALS');

  // If path is missing or the file no longer exists
  if (!credPath || !fs.existsSync(credPath)) {
    console.log('❌ Google Cloud credentials not found or invalid.');
    
    const answers = await inquirer.prompt([
      {
        type: 'input',
        name: 'keyPath',
        message: 'Enter the absolute path to your GCP Service Account JSON key (e.g., C:\\keys\\auth.json):',
        validate: (input) => {
          const resolvedPath = path.resolve(input);
          if (fs.existsSync(resolvedPath) && resolvedPath.endsWith('.json')) {
            return true;
          }
          return 'Please provide a valid path to an existing .json file.';
        }
      }
    ]);

    credPath = path.resolve(answers.keyPath);
    config.set('GOOGLE_APPLICATION_CREDENTIALS', credPath);
    console.log(`✅ Credentials path saved successfully!\n`);
  }

  // Inject into process.env so Vertex AI automatically detects it
  process.env.GOOGLE_APPLICATION_CREDENTIALS = credPath;
}

export function clearCredentials() {
    config.delete('GOOGLE_APPLICATION_CREDENTIALS');
    console.log('🗑️  Saved credentials path cleared.');
}
