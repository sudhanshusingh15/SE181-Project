const { chromium } = require('playwright');
(async () => {
  const [,, inPath, outPath] = process.argv;
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.goto('file://' + inPath, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: outPath, format: 'Letter', printBackground: true, displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-family:Inter,sans-serif;font-size:7.5px;color:#898781;width:100%;text-align:center;">Confirm or Release &nbsp;·&nbsp; page <span class="pageNumber"></span> of <span class="totalPages"></span></div>',
    margin: { top: '0.65in', bottom: '0.7in', left: '0.75in', right: '0.75in' } });
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
