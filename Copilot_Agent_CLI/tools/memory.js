import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const MEMORY_DIR = path.join(__dirname, '../memory');

function ensureMemoryDir() {
  if (!fs.existsSync(MEMORY_DIR)) {
    fs.mkdirSync(MEMORY_DIR, { recursive: true });
  }
}

/**
 * Lists all existing memory topics.
 * @returns {string} Comma separated list of topics.
 */
export function listMemories() {
  ensureMemoryDir();
  const files = fs.readdirSync(MEMORY_DIR);
  const topics = files.filter(f => f.endsWith('.md')).map(f => f.replace('.md', ''));
  if (topics.length === 0) return "No memory files exist yet.";
  return JSON.stringify(topics);
}

/**
 * Reads the memory for a specific topic.
 * @param {string} topic - The memory category/topic.
 * @returns {string} The memory content.
 */
export function readMemory(topic) {
  ensureMemoryDir();
  // Sanitize topic to prevent path traversal
  const safeTopic = path.basename(topic);
  const filePath = path.join(MEMORY_DIR, `${safeTopic}.md`);
  
  if (fs.existsSync(filePath)) {
    return fs.readFileSync(filePath, 'utf8');
  }
  return `No memory found for topic: ${safeTopic}. You can create it by writing to it.`;
}

/**
 * Appends content to a memory topic file. Creates the file if it doesn't exist.
 * @param {string} topic - The memory category/topic.
 * @param {string} content - The content to remember.
 * @returns {string} Status message.
 */
export function writeMemory(topic, content) {
  ensureMemoryDir();
  const safeTopic = path.basename(topic);
  const filePath = path.join(MEMORY_DIR, `${safeTopic}.md`);
  
  const timestamp = new Date().toISOString();
  const entry = `\n### [${timestamp}]\n${content}\n`;
  
  fs.appendFileSync(filePath, entry, 'utf8');
  return `✅ Successfully saved memory to ${safeTopic}.md`;
}
