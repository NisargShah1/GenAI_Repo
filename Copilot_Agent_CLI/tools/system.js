import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';
import util from 'util';
import { chromium } from 'playwright';

const execAsync = util.promisify(exec);

let browserInstance = null;
let contextInstance = null;
let pageInstance = null;

async function ensureBrowser(launchOptions = {}) {
  if (pageInstance && browserInstance) {
    try {
      const closed = await pageInstance.isClosed();
      if (!closed) return;
    } catch (e) {
      // ignore and continue to ensure browser
    }
  }
  if (!browserInstance) {
    // Determine headless mode: explicit launchOptions.headless -> env var -> default true
    const envVal = process.env.PLAYWRIGHT_HEADLESS;
    // Default to headful (false) unless explicitly requested via env or options.
    const defaultHeadless = (typeof envVal !== 'undefined') ? (envVal === 'true' || envVal === '1') : false;
    const headless = (typeof launchOptions.headless !== 'undefined') ? launchOptions.headless : defaultHeadless;
    const commonLaunch = { headless, args: ['--no-sandbox'] };
    try {
      browserInstance = await chromium.launch({ ...commonLaunch });
    } catch (err) {
      console.warn('Default chromium launch failed, trying system Chrome...', err.message);
      // Fallback to system-installed Chrome (if available)
      try {
        browserInstance = await chromium.launch({ ...commonLaunch, channel: 'chrome' });
      } catch (err2) {
        console.error('Failed to launch any chromium/browser:', err2.message);
        throw err2;
      }
    }
  }
  if (!contextInstance) {
    contextInstance = await browserInstance.newContext();
  }
  pageInstance = await contextInstance.newPage();
}

/**
 * Open a browser and navigate to a URL using Playwright.
 */
export async function browserOpen(url, options = {}) {
  await ensureBrowser(options);
  const timeout = options.timeout ?? 30000;
  const waitModes = [options.waitUntil || 'domcontentloaded', 'load', 'networkidle'];
  let lastErr = null;
  for (const waitUntil of waitModes) {
    try {
      await pageInstance.goto(url, { waitUntil, timeout });
      return `Opened ${url}`;
    } catch (err) {
      lastErr = err;
      console.warn(`browserOpen: navigation to ${url} using ${waitUntil} failed: ${err.message}`);
    }
  }
  throw lastErr;
}

/**
 * Click an element in the browser using Playwright.
 */
export async function browserClick(selector, opts = {}) {
  if (!pageInstance) await ensureBrowser();
  await pageInstance.waitForSelector(selector, { state: 'visible', timeout: opts.timeout ?? 10000 });
  await pageInstance.click(selector, opts);
  return `Clicked ${selector}`;
}

/**
 * Type text into an element in the browser using Playwright.
 */
export async function browserType(selector, text, opts = {}) {
  if (!pageInstance) await ensureBrowser();
  await pageInstance.waitForSelector(selector, { state: 'visible', timeout: opts.timeout ?? 10000 });
  await pageInstance.fill(selector, text, opts);
  return `Typed into ${selector}`;
}

/**
 * Extract text from an element in the browser using Playwright.
 */
export async function browserExtract(selector, opts = {}) {
  if (!pageInstance) await ensureBrowser();
  const timeout = opts.timeout ?? 10000;
  try {
    if (selector) {
      await pageInstance.waitForSelector(selector, { state: 'visible', timeout });
      const txt = await pageInstance.textContent(selector);
      return txt ? txt.trim() : '';
    }
    // If no selector provided, return full page content
    return await pageInstance.content();
  } catch (err) {
    console.warn(`browserExtract initial wait failed for ${selector}: ${err.message}`);
    // Try a best-effort fallback by evaluating in page context (avoids strict waiting)
    try {
      const fallback = await pageInstance.evaluate((sel) => {
        try {
          const el = document.querySelector(sel);
          return el ? el.textContent : null;
        } catch (e) {
          return null;
        }
      }, selector);
      if (fallback) return fallback.trim();
    } catch (e) {
      console.warn('browserExtract fallback evaluate failed:', e.message);
    }
    throw err;
  }
}

/**
 * Execute a safe shell command on the local OS.
 */
/**
 * Read file content.
 */
export async function readFile(filepath) {
  console.log(`📄 [FS] Reading file: ${filepath}`);
  try {
    return fs.readFileSync(filepath, 'utf8');
  } catch (error) {
    throw new Error(`Failed to read file ${filepath}: ${error.message}`);
  }
}

/**
 * Write content to a file.
 */
export async function writeFile(filepath, content) {
  console.log(`💾 [FS] Writing file: ${filepath}`);
  try {
    const dir = path.dirname(filepath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(filepath, content, 'utf8');
    return `Successfully wrote to ${filepath}`;
  } catch (error) {
    throw new Error(`Failed to write file ${filepath}: ${error.message}`);
  }
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
    const { stdout, stderr } = await execAsync(cmd, { 
      maxBuffer: 10 * 1024 * 1024, // 10MB to prevent hanging on large outputs (like npm install)
      timeout: 180000 // 3 minute timeout to prevent infinite hangs
    });
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
  if (!pageInstance) await ensureBrowser();
  try {
    await pageInstance.screenshot({ path: filepath, fullPage: true });
    return `Screenshot saved successfully to ${filepath}`;
  } catch (err) {
    console.warn(`takeScreenshot failed: ${err.message}`);
    throw err;
  }
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
