const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const TARGET_DIR = path.resolve(__dirname, '..', '..', 'reports', 'figures', 'dashboard_qa');

if (!fs.existsSync(TARGET_DIR)) {
  fs.mkdirSync(TARGET_DIR, { recursive: true });
}

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function runQA() {
  console.log('Launching Chrome from:', CHROME_PATH);
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    defaultViewport: { width: 1440, height: 900, deviceScaleFactor: 1 },
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
  });

  const page = await browser.newPage();
  
  // Collect any console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('BROWSER ERROR:', msg.text());
    }
  });

  page.on('pageerror', err => {
    console.log('PAGE UNCAUGHT ERROR:', err.message, err.stack);
  });

  page.on('requestfailed', req => {
    console.log('FAILED REQUEST:', req.url(), req.failure() ? req.failure().errorText : '');
  });

  console.log('Navigating to JobIntel application...');
  await page.goto('http://127.0.0.1:5173/', { waitUntil: 'networkidle0', timeout: 30000 });
  await sleep(1500);

  // 1. Executive Overview
  console.log('Capturing 01: Executive Overview');
  await page.screenshot({ path: path.join(TARGET_DIR, '01_executive_overview.png') });

  // Helper to click sidebar nav items by text
  async function navigateTo(navText) {
    const buttons = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('aside button')).map(b => b.innerText.trim().replace(/\n/g, ' '));
    });
    console.log('Sidebar buttons:', JSON.stringify(buttons));

    const success = await page.evaluate((text) => {
      const asideButtons = Array.from(document.querySelectorAll('aside button'));
      const target = asideButtons.find(b => b.innerText && b.innerText.includes(text));
      if (target) {
        target.click();
        return true;
      }
      return false;
    }, navText);

    if (!success) {
      throw new Error(`Nav item "${navText}" not found in sidebar`);
    }
    await sleep(1500);
    return true;
  }

  // 2. Salary Intelligence
  console.log('Navigating to Salary Intelligence...');
  await navigateTo('Salary Intelligence');
  await sleep(1000);
  console.log('Capturing 02: Salary Intelligence');
  await page.screenshot({ path: path.join(TARGET_DIR, '02_salary_intelligence.png') });

  // 3. Skill Explorer
  console.log('Navigating to Skill Explorer...');
  await navigateTo('Skill Explorer');
  await sleep(1000);
  console.log('Capturing 03: Skill Explorer');
  await page.screenshot({ path: path.join(TARGET_DIR, '03_skill_explorer.png') });

  // 4. Archetype Explorer
  console.log('Navigating to Archetype Explorer...');
  await navigateTo('Archetype Explorer');
  await sleep(1000);
  console.log('Capturing 04: Archetype Explorer');
  await page.screenshot({ path: path.join(TARGET_DIR, '04_archetype_explorer.png') });

  // 5. Salary Predictor
  console.log('Navigating to Salary Predictor...');
  await navigateTo('Salary Predictor');
  await sleep(1000);
  
  // Click Estimate Salary
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const estBtn = btns.find(b => b.innerText && b.innerText.toLowerCase().includes('estimate'));
    if (estBtn) {
      estBtn.click();
    }
  });
  await sleep(1500);
  console.log('Capturing 05: Salary Predictor Result');
  await page.screenshot({ path: path.join(TARGET_DIR, '05_salary_predictor_result.png') });

  // 6. Salary Predictor - Zero Skill Case
  console.log('Testing Zero-Skill quarantine edge case...');
  const clearSuccess = await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const clearBtn = btns.find(b => b.innerText && b.innerText.includes('Clear All'));
    if (clearBtn) {
      clearBtn.click();
      return true;
    }
    return false;
  });
  console.log('Cleared skills:', clearSuccess);
  await sleep(800);

  // Click Estimate Salary again
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const estBtn = btns.find(b => b.innerText && b.innerText.toLowerCase().includes('estimate'));
    if (estBtn) {
      estBtn.click();
    }
  });
  await sleep(2000);
  console.log('Capturing 06: Zero-Skill Edge Case');
  await page.screenshot({ path: path.join(TARGET_DIR, '06_salary_predictor_zero_skill.png') });

  // 7. Model Performance
  console.log('Navigating to Model Performance...');
  await navigateTo('Model Performance');
  await sleep(1000);
  console.log('Capturing 07: Model Performance');
  await page.screenshot({ path: path.join(TARGET_DIR, '07_model_performance.png') });

  // 8. Error Analysis
  console.log('Navigating to Error Analysis...');
  await navigateTo('Archetype Error');
  await sleep(1000);
  console.log('Capturing 08: Error Analysis');
  await page.screenshot({ path: path.join(TARGET_DIR, '08_error_analysis.png') });

  // 9. Research Methodology
  console.log('Navigating to Research Methodology...');
  await navigateTo('Research Methodology');
  await sleep(1000);
  console.log('Capturing 09: Research Methodology');
  await page.screenshot({ path: path.join(TARGET_DIR, '09_research_methodology.png') });

  console.log('QA Walkthrough finished successfully. Closing browser.');
  await browser.close();
}

runQA().catch(err => {
  console.error('QA FAILED:', err);
  process.exit(1);
});
