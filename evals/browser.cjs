/* Browser operations shared by disposable GUI projects and private observations. */
const fs = require('fs');
const path = require('path');

async function launch() {
  if (!process.env.EVAL_PLAYWRIGHT_MODULE || !process.env.EVAL_BROWSER_EXECUTABLE)
    throw new Error('An existing Playwright package and Chromium executable are required.');
  const { chromium } = require(process.env.EVAL_PLAYWRIGHT_MODULE);
  const browser = await chromium.launch({ executablePath: process.env.EVAL_BROWSER_EXECUTABLE,
    headless: true, args: ['--no-sandbox'] });
  const stop = async () => { await browser.close(); process.exit(143); };
  process.once('SIGTERM', stop);
  browser.once('disconnected', () => process.removeListener('SIGTERM', stop));
  return browser;
}

async function projectPage(browser, options = {}) {
  const origin = process.env.EVAL_BROWSER_ORIGIN;
  if (!origin) throw new Error('Missing local project browser origin.');
  const context = await browser.newContext({...options, serviceWorkers:'block'});
  await context.route('**/*', route => {
    const url = new URL(route.request().url());
    return url.origin === new URL(origin).origin ? route.continue() : route.abort();
  });
  await context.routeWebSocket('**/*', socket => socket.close());
  await context.addInitScript(() => {
    for (const key of ['RTCPeerConnection', 'webkitRTCPeerConnection', 'WebTransport'])
      Object.defineProperty(globalThis, key, {value:undefined, configurable:false});
  });
  return context.newPage();
}

async function inspect(page) {
  return page.evaluate(() => ({
    html: document.documentElement.outerHTML,
    elements: [...document.querySelectorAll('body *')].map(el => {
      const r = el.getBoundingClientRect(), s = getComputedStyle(el);
      return { tag: el.tagName, id: el.id, class: el.className,
        text: el.children.length ? null : el.textContent,
        rect: { x:r.x, y:r.y, width:r.width, height:r.height },
        style: { display:s.display, visibility:s.visibility, font:s.font,
          lineHeight:s.lineHeight, overflow:s.overflow, gap:s.gap,
          alignItems:s.alignItems, padding:s.padding, margin:s.margin } };
    })
  }));
}

async function run(scenarioPath, output) {
  const scenario = JSON.parse(fs.readFileSync(scenarioPath, 'utf8'));
  fs.mkdirSync(output, {recursive:true});
  const browser = await launch();
  const captures = [], observations = [], completed = [];
  let failure = null;
  try {
    const page = await projectPage(browser, {
      viewport: scenario.viewport || {width:1100,height:760},
      colorScheme: scenario.media?.colorScheme || 'light',
    });
    page.setDefaultTimeout(5000);
    const url = new URL(scenario.page, process.env.EVAL_BROWSER_ORIGIN);
    if (url.origin !== new URL(process.env.EVAL_BROWSER_ORIGIN).origin)
      throw new Error('Page leaves the project.');
    await page.goto(url.href);
    for (const [i, step] of scenario.steps.entries()) {
      if (step.action === 'click') await page.locator(step.selector).click();
      else if (step.action === 'fill') await page.locator(step.selector).fill(step.value);
      else if (step.action === 'select') await page.locator(step.selector).selectOption(step.value);
      else if (step.action === 'press') {
        if (step.selector) await page.locator(step.selector).press(step.key);
        else await page.keyboard.press(step.key);
      }
      else if (step.action === 'resize') await page.setViewportSize({width:step.width,height:step.height});
      else if (step.action === 'media') await page.emulateMedia({colorScheme:step.colorScheme});
      else if (step.action === 'evaluate') observations.push(await page.evaluate(step.script));
      else if (step.action === 'wait') await page.waitForTimeout(step.ms);
      else if (step.action === 'capture') {
        const name = `${i}-${String(step.name || 'view').replace(/[^a-zA-Z0-9_-]/g,'_')}`;
        const png = await page.screenshot({fullPage:true});
        const target = path.join(output, name + '.png');
        fs.writeFileSync(target, png);
        const structure = await inspect(page);
        fs.writeFileSync(path.join(output,name + '.json'),JSON.stringify(structure,null,2));
        captures.push({ name, data_url:'data:image/png;base64,' + png.toString('base64') });
        observations.push({capture:name, ...structure});
      } else throw new Error('Unsupported browser action: ' + step.action);
      completed.push(step);
    }
    const results = observations.map(o => o && o.capture ? {capture:o.capture,
      screenshot:path.join(output,o.capture+'.png'), structure:path.join(output,o.capture+'.json')} : o);
    console.log(JSON.stringify({output, captures:captures.map(c=>c.name), observations:results}));
  } catch (error) {
    failure = String(error.message || error);
    throw error;
  } finally {
    const receipt = {origin:'candidate_browser', request_id:process.env.EVAL_BROWSER_REQUEST_ID, page:scenario.page,
      viewport:scenario.viewport, media:scenario.media, requested_steps:scenario.steps,
      steps:completed, observations, images:captures,
      status:failure ? 'failed' : 'completed', error:failure};
    const journal = process.env.EVAL_BROWSER_JOURNAL;
    try {
      if (journal) fs.appendFileSync(journal, JSON.stringify(receipt) + '\n');
    } finally { await browser.close(); }
  }
}
module.exports = {launch, projectPage, inspect, run};
if (require.main === module) {
  if (process.argv.length !== 4) {console.error('Usage: browser-run SCENARIO_JSON OUTPUT_DIR');process.exit(2);}
  run(process.argv[2],process.argv[3]).catch(error=>{console.error(error.stack);process.exitCode=1;});
}
