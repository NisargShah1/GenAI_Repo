import { browserOpen, browserExtract, takeScreenshot } from '../tools/system.js';

async function run() {
  try {
    console.log('Starting smoke test...');
      await browserOpen('https://google.com');
    const h1 = await browserExtract('a', { timeout: 20000 });
    console.log('EXTRACTED_H1:', h1);
    await takeScreenshot('example-example1.png');
    console.log('Screenshot saved: example-example.png');
    process.exit(0);
  } catch (err) {
    console.error('Smoke test failed:', err);
    process.exit(1);
  }
}

run();
