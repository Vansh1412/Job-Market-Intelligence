const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const TARGET_DIR = path.resolve('reports/figures/staging_audit');

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function run() {
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    defaultViewport: { width: 1440, height: 1000, deviceScaleFactor: 1 },
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();

  // 1. Demand Page -> Switch to Tab 2 (Occupational Demand Explorer) -> Click UK
  console.log('Navigating to Demand page...');
  await page.goto('https://jobintel-staging.vercel.app/demand', { waitUntil: 'networkidle0', timeout: 30000 });
  await sleep(2000);

  // Click Tab 2
  console.log('Clicking Tab 2 (2. Occupational Demand Explorer)...');
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button'));
    const tab2 = buttons.find(b => b.innerText && b.innerText.includes('Occupational Demand Explorer'));
    if (tab2) tab2.click();
  });
  await sleep(2000);

  // Click the UK market button
  console.log('Clicking UK market button in Tab 2...');
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button'));
    const ukBtn = buttons.find(b => b.innerText && b.innerText.trim().endsWith('UK'));
    if (ukBtn) ukBtn.click();
  });
  await sleep(4000);

  const bannerText = await page.evaluate(() => document.body.innerText);
  console.log('Has UK Gating Header:', bannerText.includes('UK Labour Demand Publication Gate Active'));
  console.log('Has Withheld Message:', bannerText.includes('UK demand data is currently withheld'));

  const ssUK = path.join(TARGET_DIR, '05b_demand_uk_gated.png');
  await page.screenshot({ path: ssUK });
  console.log('Captured:', ssUK);

  // 2. Predictor Page -> Click Predict
  console.log('Navigating to Predictor page and clicking Predict...');
  await page.goto('https://jobintel-staging.vercel.app/predictor', { waitUntil: 'networkidle0', timeout: 30000 });
  await sleep(2000);

  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button'));
    const btn = buttons.find(b => b.innerText && b.innerText.includes('Calculate Market Salary'));
    if (btn) btn.click();
  });
  await sleep(4000);

  const predText = await page.evaluate(() => document.body.innerText);
  console.log('Has Estimated Salary:', predText.includes('$') || predText.includes('Point estimate'));
  console.log('Has Empirical MAE:', predText.includes('Holdout MAE') || predText.includes('historical authoritative evaluation'));

  const ssPred = path.join(TARGET_DIR, '02b_predictor_result.png');
  await page.screenshot({ path: ssPred });
  console.log('Captured:', ssPred);

  await browser.close();
  process.exit(0);
}

run();
