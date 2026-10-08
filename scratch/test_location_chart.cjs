const puppeteer = require('./frontend/node_modules/puppeteer-core');

async function test() {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1440,900']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  await page.goto('http://localhost:5173/explore', { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 2000));
  
  // Inspect SVG bars
  const barCount = await page.evaluate(() => {
    return document.querySelectorAll('.recharts-bar-rectangle').length;
  });
  console.log('Total SVG bar rectangles rendered on /explore (India):', barCount);
  
  await browser.close();
}

test().catch(err => {
  console.error(err);
  process.exit(1);
});
