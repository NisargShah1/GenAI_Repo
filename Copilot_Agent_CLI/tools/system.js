import { exec } from 'child_process';
import util from 'util';

const execAsync = util.promisify(exec);

// NOTE: In a full production environment, you would use 'playwright' or 'puppeteer'
// for real browser automation. We provide stubbed or lightweight implementations here.
// To use playwright: `npm install playwright` and import `{ chromium } from 'playwright'`

let browserInstance = null;
let pageInstance = null;

/**
 * Open a browser and navigate to a URL.
 * Requires Playwright or Puppeteer in production. This acts as a mock/stub.
 */
export async function browserOpen(url) {
  console.log(`🌐 [Browser] Opening URL: ${url}`);
  // Mock implementation for the agent persona
  return `Successfully opened browser and navigated to ${url}`;
}

/**
 * Click an element in the browser.
 */
export async function browserClick(selector) {
  console.log(`🖱️ [Browser] Clicking element: ${selector}`);
  return `Successfully clicked element matching ${selector}`;
}

/**
 * Type text into an element in the browser.
 */
export async function browserType(selector, text) {
  console.log(`⌨️ [Browser] Typing "${text}" into element: ${selector}`);
  return `Successfully typed text into ${selector}`;
}

/**
 * Extract text from an element in the browser.
 */
export async function browserExtract(selector) {
  console.log(`🔍 [Browser] Extracting text from: ${selector}`);
  return `Extracted sample data from ${selector}`;
}

/**
 * Execute a safe shell command on the local OS.
 */
export async function runCommand(cmd) {
  console.log(`💻 [OS] Executing command: ${cmd}`);
  
  // Basic safety check for the agent
  const forbidden = ['rm -rf', 'mkfs', 'dd ', '>', '>>'];
  if (forbidden.some(f => cmd.includes(f))) {
    throw new Error(`Command blocked for safety reasons: ${cmd}`);
  }

  try {
    const { stdout, stderr } = await execAsync(cmd);
    if (stderr) console.warn(`[OS] Warning: ${stderr}`);
    return stdout;
  } catch (error) {
    throw new Error(`Command failed: ${error.message}`);
  }
}

/**
 * Take a screenshot of the current state.
 */
export async function takeScreenshot(filepath = 'screenshot.png') {
  console.log(`📸 [OS] Taking screenshot to: ${filepath}`);
  return `Screenshot saved successfully to ${filepath}`;
}

/**
 * Open a local application.
 */
export async function openApplication(appName) {
  console.log(`🚀 [OS] Opening application: ${appName}`);
  
  // Very simplistic cross-platform open
  let openCmd = '';
  switch (process.platform) {
    case 'darwin':
      openCmd = `open -a "${appName}"`;
      break;
    case 'win32':
      openCmd = `start "" "${appName}"`;
      break;
    default:
      openCmd = `xdg-open "${appName}"`;
  }
  
  try {
    await execAsync(openCmd);
    return `Successfully opened ${appName}`;
  } catch (err) {
    return `Failed to open ${appName}: ${err.message}`;
  }
}
