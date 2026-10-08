/**
 * scripts/capture_motion_screenshots.cjs
 * Automated browser QA & motion capture runner using Puppeteer-core + Chrome.
 * Captures the 8 required screenshots for the JobIntel Motion & UX Polish Pass.
 */

const puppeteer = require('../frontend/node_modules/puppeteer-core');
const path = require('path');
const fs = require('fs');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const SCREENSHOT_DIR = path.resolve(__dirname, '..', 'reports', 'ux', 'screenshots');

if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function captureAll() {
  console.log('Launching headless Chrome from:', CHROME_PATH);
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
  });

  const page = await browser.newPage();

  // 1. LANDING DESKTOP (1440x900)
  console.log('Capturing landing_desktop.png...');
  await page.setViewport({ width: 1440, height: 900 });
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle0' });
  await new Promise((r) => setTimeout(r, 800)); // Allow entrance sequence
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, 'landing_desktop.png'),
    fullPage: false,
  });

  // 2. LANDING MOBILE (390x844)
  console.log('Capturing landing_mobile.png...');
  await page.setViewport({ width: 390, height: 844, isMobile: true, hasTouch: true });
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle0' });
  await new Promise((r) => setTimeout(r, 800));
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, 'landing_mobile.png'),
    fullPage: false,
  });

  // Reset to desktop viewport
  await page.setViewport({ width: 1440, height: 900 });

  // 3. PAGE TRANSITION (Navigating to /explore)
  console.log('Capturing page_transition.png...');
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle0' });
  await new Promise((r) => setTimeout(r, 400));
  // Click Explore nav link
  const navLinks = await page.$$('nav a, header button, a');
  let clicked = false;
  for (const link of navLinks) {
    const text = await page.evaluate((el) => el.innerText, link);
    if (text && text.includes('Explore')) {
      await link.click();
      clicked = true;
      break;
    }
  }
  // Capture during / just after transition
  await new Promise((r) => setTimeout(r, 120));
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, 'page_transition.png'),
    fullPage: false,
  });

  // 4. CALCULATOR TRANSITION (Step progression)
  console.log('Capturing calculator_transition.png...');
  await page.goto('http://localhost:5173/salary', { waitUntil: 'networkidle0' });
  await new Promise((r) => setTimeout(r, 500));
  // Fill role and click next to trigger slide transition
  const nextBtn = await page.$('button[type="button"], button');
  // Find "Continue" or "Next" button
  const allBtns = await page.$$('button');
  for (const btn of allBtns) {
    const text = await page.evaluate((el) => el.innerText, btn);
    if (text && (text.includes('Next') || text.includes('Continue') || text.includes('Select'))) {
      await btn.click();
      break;
    }
  }
  await new Promise((r) => setTimeout(r, 150)); // Mid-slide
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, 'calculator_transition.png'),
    fullPage: false,
  });

  // 5. SALARY RESULT ANIMATION (Result reveal)
  console.log('Capturing salary_result_animation.png...');
  await page.goto('http://localhost:5173/salary', { waitUntil: 'networkidle0' });
  await new Promise((r) => setTimeout(r, 600));
  // Advance through steps 1 to 5
  for (let s = 1; s <= 5; s++) {
    await page.waitForSelector('#wizard-continue-btn', { timeout: 5000 });
    await page.click('#wizard-continue-btn');
    await new Promise((r) => setTimeout(r, 350));
  }
  // Now on Step 6, click #predict-submit-btn
  await page.waitForSelector('#predict-submit-btn', { timeout: 5000 });
  await page.click('#predict-submit-btn');

  // Wait for result card or analyzing animation to complete
  await new Promise((r) => setTimeout(r, 2200));
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, 'salary_result_animation.png'),
    fullPage: false,
  });

  // 6. EXPLORE ANIMATION
  console.log('Capturing explore_animation.png...');
  await page.goto('http://localhost:5173/explore', { waitUntil: 'networkidle0' });
  await new Promise((r) => setTimeout(r, 800)); // Allow bar growth animation
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, 'explore_animation.png'),
    fullPage: false,
  });

  // 7. SKILLS ANIMATION
  console.log('Capturing skills_animation.png...');
  await page.goto('http://localhost:5173/skills', { waitUntil: 'networkidle0' });
  await new Promise((r) => setTimeout(r, 800));
  // Click a skill in the table
  const tableRows = await page.$$('table tr');
  if (tableRows.length > 2) {
    await tableRows[2].click();
    await new Promise((r) => setTimeout(r, 400));
  }
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, 'skills_animation.png'),
    fullPage: false,
  });

  // 8. ARCHETYPES ANIMATION
  console.log('Capturing archetypes_animation.png...');
  await page.goto('http://localhost:5173/archetypes', { waitUntil: 'networkidle0' });
  await new Promise((r) => setTimeout(r, 800));
  // Click second archetype card
  const cards = await page.$$('div[style*="cursor: pointer"]');
  if (cards.length > 1) {
    await cards[1].click();
    await new Promise((r) => setTimeout(r, 400));
  }
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, 'archetypes_animation.png'),
    fullPage: false,
  });

  console.log('All 8 screenshots successfully captured in:', SCREENSHOT_DIR);
  await browser.close();
}

captureAll().catch((err) => {
  console.error('Screenshot capture failed:', err);
  process.exit(1);
});
