import { chromium } from 'playwright';
import { resolve } from 'path';
const browser = await chromium.launch();
const page = await browser.newPage();
await page.setViewportSize({ width: 800, height: 500 });
await page.goto('file://' + resolve('preview-button.html'));
await page.screenshot({ path: 'preview-button.png', fullPage: true });
await browser.close();
console.log('done');
