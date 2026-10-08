/**
 * scripts/capture_qa_screenshots.cjs
 * Automated browser QA & screenshot regression runner using Puppeteer-core + Chrome.
 */

const puppeteer = require('../frontend/node_modules/puppeteer-core');
const path = require('path');
const fs = require('fs');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const SCREENSHOT_DIR = path.resolve(__dirname, '..', 'reports', 'bug_fix', 'screenshots');

if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function runQA() {
  console.log('Launching Chrome from:', CHROME_PATH);
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 900 });

  try {
    // 1. EXPLORE MARKET (USA & INDIA)
    console.log('Testing Explore Market Page...');
    await page.goto('http://localhost:5173/explore', { waitUntil: 'networkidle0' });
    await page.waitForSelector('.recharts-responsive-container', { timeout: 10000 });
    // Allow animation to complete
    await new Promise((r) => setTimeout(r, 1500));

    // Capture USA Explore Market
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'fixed_explore_market_usa.png'),
      fullPage: false,
    });
    console.log('Saved fixed_explore_market_usa.png');

    // Switch to India
    const buttons = await page.$$('button');
    for (const btn of buttons) {
      const text = await page.evaluate((el) => el.innerText, btn);
      if (text && text.includes('India')) {
        await btn.click();
        break;
      }
    }
    await new Promise((r) => setTimeout(r, 1500));

    // Verify Experience Chart has visible bars
    const experienceBars = await page.$$('.recharts-bar-rectangle');
    console.log(`India Experience & Role charts rendered ${experienceBars.length} bar rectangles.`);

    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'fixed_explore_market.png'),
      fullPage: false,
    });
    console.log('Saved fixed_explore_market.png (India)');

    // 2. SKILLS EXPLORER
    console.log('Testing Skills Explorer Page...');
    await page.goto('http://localhost:5173/skills', { waitUntil: 'networkidle0' });
    await page.waitForSelector('table', { timeout: 10000 });
    await new Promise((r) => setTimeout(r, 1000));

    // Switch to India
    const skillButtons = await page.$$('button');
    for (const btn of skillButtons) {
      const text = await page.evaluate((el) => el.innerText, btn);
      if (text && text.includes('India')) {
        await btn.click();
        break;
      }
    }
    await new Promise((r) => setTimeout(r, 1500));

    // Click SAP row
    const tableRows = await page.$$('table tbody tr');
    for (const row of tableRows) {
      const text = await page.evaluate((el) => el.innerText, row);
      if (text && text.includes('SAP')) {
        await row.click();
        break;
      }
    }
    await new Promise((r) => setTimeout(r, 1000));

    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'fixed_skills_explorer.png'),
      fullPage: false,
    });
    console.log('Saved fixed_skills_explorer.png');

    // 3. SALARY CALCULATOR
    console.log('Testing Guided Salary Calculator...');
    await page.goto('http://localhost:5173/salary', { waitUntil: 'networkidle0' });
    await new Promise((r) => setTimeout(r, 1000));

    // Step 1: Select USA and proceed
    // Click "Continue" button
    for (let s = 1; s <= 6; s++) {
      const stepBtns = await page.$$('button');
      for (const btn of stepBtns) {
        const text = await page.evaluate((el) => el.innerText, btn);
        if (text && (text.includes('Continue') || text.includes('Calculate My Salary') || text.includes('Estimate'))) {
          await btn.click();
          await new Promise((r) => setTimeout(r, 500));
          break;
        }
      }
    }
    // Wait for step 7 result
    await new Promise((r) => setTimeout(r, 2000));

    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'fixed_calculator_result.png'),
      fullPage: false,
    });
    console.log('Saved fixed_calculator_result.png');

    // 4. MOBILE RESPONSIVENESS
    console.log('Testing Mobile Viewports (390 x 844)...');
    await page.setViewport({ width: 390, height: 844 });

    await page.goto('http://localhost:5173/explore', { waitUntil: 'networkidle0' });
    await new Promise((r) => setTimeout(r, 1500));
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'mobile_explore_market.png'),
      fullPage: false,
    });
    console.log('Saved mobile_explore_market.png');

    await page.goto('http://localhost:5173/skills', { waitUntil: 'networkidle0' });
    await new Promise((r) => setTimeout(r, 1500));
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'mobile_skills_explorer.png'),
      fullPage: false,
    });
    console.log('Saved mobile_skills_explorer.png');

    console.log('ALL BROWSER QA SCREENSHOTS CAPTURED SUCCESSFULLY!');
  } catch (err) {
    console.error('Browser QA error:', err);
    process.exitCode = 1;
  } finally {
    await browser.close();
  }
}

runQA();
