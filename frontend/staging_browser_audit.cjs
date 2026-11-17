const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const TARGET_DIR = path.resolve('reports/figures/staging_audit');
if (!fs.existsSync(TARGET_DIR)) {
  fs.mkdirSync(TARGET_DIR, { recursive: true });
}

const BASE_URL = 'https://jobintel-staging.vercel.app';
const STAGING_BACKEND = 'https://jobintel-backend-staging.onrender.com';
const PROD_BACKEND = 'job-market-intelligence-6ral.onrender.com';
const PROD_FRONTEND = 'job-market-intelligence-dusky.vercel.app';

const auditLog = {
  routesTested: [],
  networkRequests: [],
  backendRequests: [],
  productionLeakAttempts: [],
  consoleErrors: [],
  pageErrors: [],
  uiVerifications: {},
  screenshots: []
};

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function run() {
  console.log('Launching Chrome for E2E Staging Audit...');
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    defaultViewport: { width: 1440, height: 900, deviceScaleFactor: 1 },
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
  });

  const page = await browser.newPage();

  // Monitor network
  page.on('request', req => {
    const url = req.url();
    const method = req.method();
    auditLog.networkRequests.push({ method, url });

    if (url.includes('onrender.com')) {
      auditLog.backendRequests.push({ method, url });
    }

    if (url.includes(PROD_BACKEND) || url.includes(PROD_FRONTEND)) {
      console.error('CRITICAL: PRODUCTION LEAK DETECTED:', url);
      auditLog.productionLeakAttempts.push({ method, url });
    }
  });

  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('Console Error:', msg.text());
      auditLog.consoleErrors.push(msg.text());
    }
  });

  page.on('pageerror', err => {
    console.log('Page Error:', err.message);
    auditLog.pageErrors.push(err.message);
  });

  try {
    // 1. Landing Page
    console.log('Testing 1: Landing Page...');
    await page.goto(BASE_URL + '/', { waitUntil: 'networkidle0', timeout: 30000 });
    await sleep(1500);
    const title = await page.title();
    const bodyText = await page.evaluate(() => document.body.innerText);
    auditLog.routesTested.push('/');
    auditLog.uiVerifications.landing = {
      title,
      hasHeroText: bodyText.includes('JobIntel') || bodyText.includes('Career'),
      hasMarkets: bodyText.includes('USA') && bodyText.includes('India')
    };
    const ss1 = path.join(TARGET_DIR, '01_landing_page.png');
    await page.screenshot({ path: ss1 });
    auditLog.screenshots.push(ss1);

    // 2. Predictor Page
    console.log('Testing 2: Predictor Page (/predictor)...');
    await page.goto(BASE_URL + '/predictor', { waitUntil: 'networkidle0', timeout: 30000 });
    await sleep(2000);
    auditLog.routesTested.push('/predictor');
    
    // Check initial text and prediction
    const predictorInitialText = await page.evaluate(() => document.body.innerText);
    
    // Look for Predict button and click
    const predictClicked = await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      const pBtn = btns.find(b => b.innerText && (b.innerText.includes('Predict') || b.innerText.includes('Estimate')));
      if (pBtn) {
        pBtn.click();
        return true;
      }
      return false;
    });
    await sleep(3000);

    const predictorResultText = await page.evaluate(() => document.body.innerText);
    auditLog.uiVerifications.predictor = {
      predictButtonClicked: predictClicked,
      hasEmpiricalDispersionNote: predictorResultText.includes('Empirical dispersion based on holdout MAE') || predictorResultText.includes('empirical_mae_dispersion'),
      hasConfidenceInterval: predictorResultText.includes('$') || predictorResultText.includes('Salary') || predictorResultText.includes('LPA')
    };
    const ss2 = path.join(TARGET_DIR, '02_predictor_page.png');
    await page.screenshot({ path: ss2 });
    auditLog.screenshots.push(ss2);

    // 3. Skills Page
    console.log('Testing 3: Skills Page (/skills)...');
    await page.goto(BASE_URL + '/skills', { waitUntil: 'networkidle0', timeout: 30000 });
    await sleep(2500);
    auditLog.routesTested.push('/skills');
    const skillsText = await page.evaluate(() => document.body.innerText);
    auditLog.uiVerifications.skills = {
      hasPython: skillsText.includes('Python') || skillsText.includes('python'),
      hasGeneralCorpusDenominator: skillsText.includes('335,995') || skillsText.includes('335995'),
      notSalaryModelSize: !skillsText.includes('34,036 postings') && !skillsText.includes('34036 postings')
    };
    const ss3 = path.join(TARGET_DIR, '03_skills_page.png');
    await page.screenshot({ path: ss3 });
    auditLog.screenshots.push(ss3);

    // 4. Occupations Page
    console.log('Testing 4: Occupations Page (/occupations)...');
    await page.goto(BASE_URL + '/occupations', { waitUntil: 'networkidle0', timeout: 30000 });
    await sleep(2000);
    auditLog.routesTested.push('/occupations');
    const occText = await page.evaluate(() => document.body.innerText);
    auditLog.uiVerifications.occupations = {
      hasTaxonomy: occText.includes('SOC') || occText.includes('Software') || occText.includes('Engineer') || occText.includes('Occupations')
    };
    const ss4 = path.join(TARGET_DIR, '04_occupations_page.png');
    await page.screenshot({ path: ss4 });
    auditLog.screenshots.push(ss4);

    // 5. Demand Page
    console.log('Testing 5: Demand Page (/demand)...');
    await page.goto(BASE_URL + '/demand', { waitUntil: 'networkidle0', timeout: 30000 });
    await sleep(2500);
    auditLog.routesTested.push('/demand');
    const demandText = await page.evaluate(() => document.body.innerText);
    auditLog.uiVerifications.demand = {
      hasDemandHeader: demandText.includes('Demand') || demandText.includes('Market Demand'),
      hasSkillGaps: demandText.includes('Skill') || demandText.includes('Gaps')
    };

    // Click UK market button on Demand page if present
    await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      const ukBtn = btns.find(b => b.innerText && (b.innerText.includes('UK') || b.innerText.includes('United Kingdom')));
      if (ukBtn) ukBtn.click();
    });
    await sleep(1500);

    const ukDemandText = await page.evaluate(() => document.body.innerText);
    auditLog.uiVerifications.demand.ukGating = {
      hasGatingMessage: ukDemandText.includes('UK demand intelligence is scheduled for subsequent sprint release') || ukDemandText.includes('UK_DEMAND_DATA_NOT_PUBLISHED') || ukDemandText.includes('not published') || ukDemandText.includes('Gated'),
    };
    const ss5 = path.join(TARGET_DIR, '05_demand_page.png');
    await page.screenshot({ path: ss5 });
    auditLog.screenshots.push(ss5);

    // Save summary before closing
    console.log('\n=== AUDIT RESULTS SUMMARY ===');
    console.log('Routes tested:', auditLog.routesTested);
    console.log('Total network requests:', auditLog.networkRequests.length);
    console.log('Backend requests to staging:', auditLog.backendRequests.length);
    console.log('Production leak attempts:', auditLog.productionLeakAttempts.length);
    console.log('Console errors count:', auditLog.consoleErrors.length);
    console.log('Page errors count:', auditLog.pageErrors.length);
    console.log('UI verifications:', JSON.stringify(auditLog.uiVerifications, null, 2));

    fs.writeFileSync(
      'reports/figures/staging_audit/audit_summary.json',
      JSON.stringify(auditLog, null, 2)
    );
    console.log('Audit log saved to reports/figures/staging_audit/audit_summary.json');

  } catch (err) {
    console.error('Audit execution error:', err);
    auditLog.fatalError = err.message;
    fs.writeFileSync(
      'reports/figures/staging_audit/audit_summary.json',
      JSON.stringify(auditLog, null, 2)
    );
  } finally {
    try {
      await browser.close();
    } catch (e) {}
    process.exit(0);
  }
}

run();
