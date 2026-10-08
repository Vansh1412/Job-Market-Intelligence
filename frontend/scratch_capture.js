import puppeteer from 'puppeteer-core';
import fs from 'fs';
import path from 'path';

const SCREENSHOT_DIR = path.resolve('../reports/screenshots');
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function run() {
  console.log('Launching browser via Microsoft Edge...');
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  // 1. Home Page
  console.log('Capturing Home Page...');
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle0' });
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '01_home_page.png'), fullPage: false });

  // 2. Click "Estimate My Salary"
  console.log('Navigating to Salary Calculator...');
  const allBtns = await page.$$('button');
  for (const btn of allBtns) {
    const text = await page.evaluate(el => el.textContent, btn);
    if (text && text.includes('Estimate My Salary')) {
      await btn.click();
      break;
    }
  }
  await new Promise(r => setTimeout(r, 600));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02_calculator_step1.png'), fullPage: false });

  // Step 1 -> Step 2
  console.log('Proceeding to Step 2 (Role)...');
  const allBtns1 = await page.$$('button');
  for (const b of allBtns1) {
    const text = await page.evaluate(el => el.textContent, b);
    if (text && text.trim() === 'Continue') {
      await b.click();
      break;
    }
  }
  await new Promise(r => setTimeout(r, 400));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '03_calculator_step2_role.png'), fullPage: false });

  // Step 2 -> Step 3
  console.log('Proceeding to Step 3 (Experience)...');
  const allBtns2 = await page.$$('button');
  for (const b of allBtns2) {
    const text = await page.evaluate(el => el.textContent, b);
    if (text && text.trim() === 'Continue') {
      await b.click();
      break;
    }
  }
  await new Promise(r => setTimeout(r, 400));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '04_calculator_step3_exp.png'), fullPage: false });

  // Step 3 -> Step 4
  console.log('Proceeding to Step 4 (Location)...');
  const allBtns3 = await page.$$('button');
  for (const b of allBtns3) {
    const text = await page.evaluate(el => el.textContent, b);
    if (text && text.trim() === 'Continue') {
      await b.click();
      break;
    }
  }
  await new Promise(r => setTimeout(r, 400));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '05_calculator_step4_location.png'), fullPage: false });

  // Step 4 -> Step 5 (Skills)
  console.log('Proceeding to Step 5 (Skills)...');
  const allBtns4 = await page.$$('button');
  for (const b of allBtns4) {
    const text = await page.evaluate(el => el.textContent, b);
    if (text && text.trim() === 'Continue') {
      await b.click();
      break;
    }
  }
  await new Promise(r => setTimeout(r, 400));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '06_calculator_step5_skills.png'), fullPage: false });

  // Step 5 -> Step 6 (Work Mode)
  console.log('Proceeding to Step 6 (Work Mode)...');
  const allBtns5 = await page.$$('button');
  for (const b of allBtns5) {
    const text = await page.evaluate(el => el.textContent, b);
    if (text && text.trim() === 'Continue') {
      await b.click();
      break;
    }
  }
  await new Promise(r => setTimeout(r, 400));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '07_calculator_step6_workmode.png'), fullPage: false });

  // Step 6 -> Step 7 (Calculate Salary)
  console.log('Calculating Salary (Step 7 Result)...');
  const allBtns6 = await page.$$('button');
  for (const b of allBtns6) {
    const text = await page.evaluate(el => el.textContent, b);
    if (text && text.includes('Calculate My Salary')) {
      await b.click();
      break;
    }
  }
  await new Promise(r => setTimeout(r, 1200));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '08_calculator_step7_result.png'), fullPage: false });

  // 3. Explore Market Page
  console.log('Capturing Explore Market Page...');
  const navBtns = await page.$$('nav button');
  for (const b of navBtns) {
    const text = await page.evaluate(el => el.textContent, b);
    if (text && text.includes('Explore Market')) {
      await b.click();
      break;
    }
  }
  await new Promise(r => setTimeout(r, 800));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '09_explore_market.png'), fullPage: false });

  // 4. Skills Page
  console.log('Capturing Skills Page...');
  const navBtns2 = await page.$$('nav button');
  for (const b of navBtns2) {
    const text = await page.evaluate(el => el.textContent, b);
    if (text && text.includes('Skills')) {
      await b.click();
      break;
    }
  }
  await new Promise(r => setTimeout(r, 800));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '10_skills_page.png'), fullPage: false });

  // 5. Archetypes Page
  console.log('Capturing Archetypes Page...');
  const navBtns3 = await page.$$('nav button');
  for (const b of navBtns3) {
    const text = await page.evaluate(el => el.textContent, b);
    if (text && text.includes('Archetypes')) {
      await b.click();
      break;
    }
  }
  await new Promise(r => setTimeout(r, 800));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '11_archetypes_page.png'), fullPage: false });

  // 6. USA vs India Page
  console.log('Capturing USA vs India Page...');
  const navBtns4 = await page.$$('nav button');
  for (const b of navBtns4) {
    const text = await page.evaluate(el => el.textContent, b);
    if (text && text.includes('USA vs India')) {
      await b.click();
      break;
    }
  }
  await new Promise(r => setTimeout(r, 800));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '12_cross_market_page.png'), fullPage: false });

  // 7. How It Works Page
  console.log('Capturing How It Works Page...');
  const navBtns5 = await page.$$('nav button');
  for (const b of navBtns5) {
    const text = await page.evaluate(el => el.textContent, b);
    if (text && text.includes('How It Works')) {
      await b.click();
      break;
    }
  }
  await new Promise(r => setTimeout(r, 800));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '13_how_it_works_page.png'), fullPage: false });

  // 8. Mobile Viewport (iPhone 14)
  console.log('Capturing Mobile Viewport...');
  await page.setViewport({ width: 390, height: 844, isMobile: true, hasTouch: true });
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 500));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '14_mobile_home.png'), fullPage: false });

  console.log('All screenshots captured successfully in reports/screenshots/!');
  await browser.close();
}

run().catch(err => {
  console.error('Error capturing screenshots:', err);
  process.exit(1);
});
