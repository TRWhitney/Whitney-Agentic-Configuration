"use strict";

// Private observations of the rendered reference and application.
const { launch, projectPage } = require('./browser.cjs');

const button = (page, name) => page.getByRole('button', {name, exact:true});
const editor = page => page.getByRole('textbox', {name:'Document text', exact:true});
const documents = page => page.getByRole('region', {name:'Documents', exact:true});
const find = page => page.getByRole('searchbox', {name:'Find', exact:true});
function container(anchor, ...contents) {
  let ancestors = anchor.locator('xpath=ancestor::*');
  for (const content of contents) ancestors = ancestors.filter({has:content});
  return ancestors.last();
}
const pane = page => container(editor(page), button(page, 'Save'));
const title = page => pane(page).getByRole('heading', {level:2});

function preference(page, name) {
  const select = page.getByRole('combobox', {name, exact:true});
  const row = container(select, page.getByRole('button', {name:/^Appl(?:y|ied)$/}));
  return {select, action:row.getByRole('button', {name:/^Appl(?:y|ied)$/})};
}

async function observe(target, relationship = 'self') {
  return target.evaluate((element, relationship) => {
    if (relationship === 'label') {
      element = element.labels?.[0] || document.getElementById(element.getAttribute('aria-labelledby'));
      if (!element) throw new Error('A visible control label is required.');
    } else if (relationship === 'divider') {
      const heading = element;
      while (element && element.getAttribute('role') !== 'dialog') {
        const style = getComputedStyle(element);
        if (parseFloat(style.borderBottomWidth) > 0 && style.borderBottomStyle !== 'none') break;
        element = element.parentElement;
      }
      if (!element || element.getAttribute('role') === 'dialog') element = heading;
    }
    const r = element.getBoundingClientRect(), s = getComputedStyle(element);
    return {
      x:r.x, y:r.y, right:r.right, bottom:r.bottom, width:r.width, height:r.height,
      centerY:r.y + r.height / 2,
      visible:!!(r.width && r.height && s.visibility !== 'hidden' && s.display !== 'none'),
      padding:s.padding, fontSize:s.fontSize, lineHeight:s.lineHeight,
      fontFamily:s.fontFamily,
      monospace:(() => { const c=document.createElement('canvas').getContext('2d'); c.font=s.fontSize + ' ' + s.fontFamily; return Math.abs(c.measureText('iiiiiiii').width-c.measureText('WWWWWWWW').width)<0.1; })(),
      appearance:s.appearance, border:s.border, borderBottom:s.borderBottom,
      borderRadius:s.borderRadius, boxShadow:s.boxShadow,
      backgroundImage:s.backgroundImage, scrollbarGutter:s.scrollbarGutter,
      text:element.textContent,
    };
  }, relationship);
}

async function optionalObservation(target) {
  return await target.count() ? observe(target) : {visible:false, text:''};
}

async function anyVisible(target) {
  for (const item of await target.all()) if (await item.isVisible()) return true;
  return false;
}

async function take(page, images, name) {
  images.push({name, data_url:'data:image/png;base64,' + (await page.screenshot({fullPage:true})).toString('base64')});
}

async function toolbarGeometry(page) {
  return {
    create:await observe(button(page, 'New document')),
    rename:await observe(button(page, 'Rename')),
    label:await observe(find(page), 'label'),
    search:await observe(find(page)),
    clear:await observe(button(page, 'Clear')),
  };
}

async function inspect(browser, root, directory, scenario) {
  const page = await projectPage(browser, {viewport:{width:1000,height:900}, reducedMotion:'reduce'});
  page.setDefaultTimeout(5000);
  const images = [], values = {};
  try {
    await page.goto(new URL(directory + '/index.html', process.env.EVAL_BROWSER_ORIGIN).href);
    const capture = name => take(page, images, directory + '/' + name);
    const naming = async () => {
      for (const action of ['new','rename']) {
        await button(page, action === 'new' ? 'New document' : 'Rename').click();
        const dialog = page.getByRole('dialog');
        values[action + '/frame'] = await observe(dialog);
        values[action + '/heading'] = await observe(dialog.getByRole('heading'), 'divider');
        values[action + '/mark'] = await optionalObservation(dialog.getByText('F', {exact:true}));
        await capture(action);
        await button(dialog, 'Cancel').click();
      }
    };
    const rendering = async () => {
      await editor(page).fill(Array(80).fill('Field observation: record water level and weather.').join('\n'));
      values.editor = await observe(editor(page));
      values.format = await observe(preference(page, 'Format').select);
      await editor(page).evaluate(element => { element.scrollTop = 160; });
      values.editorScroll = await editor(page).evaluate(element => element.scrollTop);
      await preference(page, 'Format').select.selectOption({label:'Field report with observations'});
      await preference(page, 'Sharing and review permissions').select.selectOption({label:'Field team and visiting researchers'});
      await capture('rendered-preferences-and-editor');
    };
    const transitions = async () => {
      await button(page, 'New document').click();
      await page.getByRole('textbox', {name:'Document name', exact:true}).fill('River transect');
      await button(page.getByRole('dialog'), 'Create').click();
      await button(page, 'New document').click();
      const dialog = page.getByRole('dialog'), confirm = button(dialog, 'Create');
      values.beforeValidation = await observe(confirm);
      await confirm.click();
      values.withValidation = await observe(confirm);
      values.validationText = await dialog.getByRole('alert', {includeHidden:true}).innerText();
      await capture('validation');
      await dialog.getByRole('textbox', {name:'Document name', exact:true}).fill('Estuary notes');
      values.correctedValidation = await observe(confirm);
      values.correctedText = await dialog.getByRole('alert', {includeHidden:true}).innerText();
      await button(dialog, 'Cancel').click();
      values.beforeSearch = await observe(documents(page));
      await find(page).fill('unmatched document');
      values.emptySearch = await observe(documents(page));
      values.emptyText = await documents(page).innerText();
      await capture('empty-search');
      await find(page).fill('River transect');
      values.restoredSearch = await observe(documents(page));
      values.restoredText = await documents(page).innerText();
      await button(page, 'Clear').click();
    };
    const composition = async () => {
      await button(page, 'Split view').click();
      await button(page, 'Save').click();
      const notice = container(button(page, 'Retry'), page.getByText(/^The notebook service could not accept the document\./));
      const details = (await notice.innerText()).split('\n').map(t => t.trim()).filter(t => t && t !== 'Save failed' && t !== 'Retry');
      values.failedEditor = await observe(editor(page));
      values.failedPane = await observe(pane(page));
      values.failedFooter = await observe(container(pane(page).getByText('Saved locally', {exact:true}), page.getByText('Plain text', {exact:true})));
      values.failedNotice = await observe(notice);
      if (scenario === 'composition') await capture('split-failure');
      await button(page, 'Retry').click();
      values.retryGlobal = {visible:await anyVisible(page.getByText(/(?:last save failed|^Save failed$)/i))};
      values.retryFooter = await optionalObservation(pane(page).getByText('Saved locally', {exact:true}));
      let visibleDetail = false;
      for (const detail of details) {
        if (await anyVisible(page.getByText(detail))) visibleDetail = true;
      }
      values.retryDetail = {visible:visibleDetail};
      values.retryLabel = await pane(page).getByText('Saving', {exact:true}).innerText();
      await capture('split-retry');
      await button(page, 'Split view').click();
    };
    const layout = async () => {
      const format = preference(page, 'Format');
      let sharing = preference(page, 'Sharing and review permissions');
      values.wideToolbar = await toolbarGeometry(page);
      values.preferenceRows = [];
      for (const {select, action} of [format, sharing]) {
        values.preferenceRows.push({label:await observe(select, 'label'), select:await observe(select), action:await observe(action)});
      }
      await format.action.click();
      values.appliedRows = [];
      for (const {select, action} of [format, sharing]) {
        values.appliedRows.push({selectRight:(await observe(select)).right, actionLeft:(await observe(action)).x});
      }
      if (scenario === 'layout') await capture('repeated-rows');
      await page.setViewportSize({width:390,height:1100});
      values.narrowToolbar = await toolbarGeometry(page);
      await format.select.selectOption({label:'Field report with observations'});
      await sharing.select.selectOption({label:'Field team and visiting researchers'});
      const longLabel = 'Sharing and review permissions for visiting researchers and field teams';
      await sharing.select.evaluate((element, text) => {
        const label = element.labels?.[0] || document.getElementById(element.getAttribute('aria-labelledby'));
        if (!label) throw new Error('The sharing control needs its visible label.');
        label.textContent = text;
      }, longLabel);
      sharing = preference(page, longLabel);
      values.narrowFind = await observe(find(page), 'label');
      values.narrowSearch = await observe(find(page));
      values.narrowClear = await observe(button(page, 'Clear'));
      values.narrowLabel = await observe(sharing.select, 'label');
      values.narrowSharing = await observe(sharing.select);
      values.narrowApply = await observe(sharing.action);
      await capture('narrow-long-content');
    };
    if (scenario === 'design') await naming();
    else if (scenario === 'rendering') await rendering();
    else if (scenario === 'transitions') await transitions();
    else if (scenario === 'composition') await composition();
    else if (scenario === 'layout' || scenario === 'shared-views') await layout();
    else if (scenario === 'audit' || scenario === 'clean') {
      await transitions();
      await composition();
      await layout();
    } else throw new Error('Unknown GUI scenario: ' + scenario);
    if (scenario === 'shared-views') {
      values.archiveRows = [];
      for (const width of [1000,390]) {
        await page.setViewportSize({width,height:1100});
        await page.goto(new URL(directory + '/archive.html', process.env.EVAL_BROWSER_ORIGIN).href);
        const {select,action} = preference(page, 'Format');
        values.archiveRows.push({width,label:await observe(select,'label'),select:await observe(select),action:await observe(action)});
        await capture('archive-' + width);
      }
      if (directory === 'app') {
        await preference(page, 'Format').select.selectOption({label:'Field report with observations'});
        await preference(page, 'Format').action.click();
        await page.goto(new URL('app/index.html', process.env.EVAL_BROWSER_ORIGIN).href);
        values.archivePreference = await preference(page, 'Format').select.inputValue();
      }
    }
    return {values, images};
  } finally { await page.context().close(); }
}

// Production behavior has its own oracle. The presentation prototype has no notebook store.
async function inspectNotebook(browser) {
  const page = await projectPage(browser, {viewport:{width:1000,height:900}});
  page.setDefaultTimeout(5000);
  const measurements = [], images = [];
  const check = (name, expected, actual) => measurements.push({name:'notebook/' + name, expected, actual, matched:expected === actual});
  const create = async name => {
    await button(page, 'New document').click();
    await page.getByRole('textbox', {name:'Document name', exact:true}).fill(name);
    await button(page.getByRole('dialog'), 'Create').click();
  };
  const select = async name => {
    const link = documents(page).getByRole('link', {name, exact:true});
    if (await link.count()) await link.click();
    else check('document-available/' + name, true, false);
  };
  try {
    await page.goto(new URL('app/index.html', process.env.EVAL_BROWSER_ORIGIN).href);
    const current = await title(page).innerText();
    const names = await documents(page).getByRole('link').allTextContents();
    check('initial-document-available', true, names.includes(current));
    const other = names.find(name => name !== current);
    if (other) {
      await editor(page).fill('An observation belonging to the first document.');
      await select(other);
      check('existing-document-selected', other, await title(page).innerText());
      check('existing-documents-have-separate-text', true, (await editor(page).inputValue()) !== 'An observation belonging to the first document.');
    }
    await create('Upstream station');
    check('new-document-empty', '', await editor(page).inputValue());
    await editor(page).fill('Water level 1.4m\nNorth bank sample collected.');
    await preference(page, 'Format').select.selectOption({label:'Field report with observations'});
    await preference(page, 'Format').action.click();
    await create('Downstream station');
    check('second-document-empty', '', await editor(page).inputValue());
    await editor(page).fill('Water level 0.8m\nSouth bank sample collected.');
    await select('Upstream station');
    check('selected-document-title', 'Upstream station', await title(page).innerText());
    check('selected-document-text', 'Water level 1.4m\nNorth bank sample collected.', await editor(page).inputValue());
    check('selected-document-preference', 'Field report with observations', await preference(page, 'Format').select.inputValue());
    await button(page, 'Rename').click();
    check('rename-current-title', 'Upstream station', await page.getByRole('textbox', {name:'Document name', exact:true}).inputValue());
    await page.getByRole('textbox', {name:'Document name', exact:true}).fill('Upstream spring station');
    await button(page.getByRole('dialog'), 'Rename').click();
    check('renamed-result', 1, await documents(page).getByRole('link', {name:'Upstream spring station', exact:true}).count());
    check('old-title-removed', 0, await documents(page).getByRole('link', {name:'Upstream station', exact:true}).count());
    await find(page).fill('spring');
    check('search-renamed-document', 'Upstream spring station', await documents(page).innerText());
    await button(page, 'Clear').click();
    await select('Downstream station');
    await page.reload();
    check('reload-active-document', 'Downstream station', await title(page).innerText());
    check('reload-current-text', 'Water level 0.8m\nSouth bank sample collected.', await editor(page).inputValue());
    await select('Upstream spring station');
    check('reload-other-text', 'Water level 1.4m\nNorth bank sample collected.', await editor(page).inputValue());
    check('reload-applied-preference', 'Field report with observations', await preference(page, 'Format').select.inputValue());
    await button(page, 'Save').click();
    await button(page, 'Retry').click();
    await page.waitForTimeout(1350);
    check('retry-completes', 1, await pane(page).getByText('Saved', {exact:true}).count());
    check('retry-retains-text', 'Water level 1.4m\nNorth bank sample collected.', await editor(page).inputValue());
    await take(page, images, 'app/stored-notebook');
    return {measurements, images};
  } finally { await page.context().close(); }
}

function compare(reference, application, scenario) {
  const measurements = [];
  function check(name, expected, actual, tolerance = 0) {
    const matched = typeof expected === 'number' && typeof actual === 'number'
      ? Math.abs(expected - actual) <= tolerance : expected === actual;
    measurements.push({name, expected, actual, matched});
  }
  const a = application.values, r = reference.values;
  if (scenario === 'design') {
    for (const action of ['new', 'rename']) {
      for (const style of ['padding', 'border', 'borderRadius', 'boxShadow']) check(action + '/frame/' + style, r[action + '/frame'][style], a[action + '/frame'][style]);
      check(action + '/mark-visible', r[action + '/mark'].visible, a[action + '/mark'].visible);
      check(action + '/heading-divider', r[action + '/heading'].borderBottom, a[action + '/heading'].borderBottom);
    }
  }
  if (scenario === 'rendering') {
    for (const style of ['fontSize','lineHeight','padding','scrollbarGutter']) check('editor/' + style, r.editor[style], a.editor[style]);
    // The reference's monospace role allows equivalent installed monospace fonts.
    check('editor/monospace-role', true, a.editor.monospace);
    for (const style of ['appearance','backgroundImage','height','padding']) check('selector/' + style, r.format[style], a.format[style], style === 'height' ? 1 : 0);
    check('editor/scrolls-internally', true, a.editorScroll > 0);
  }
  if (['transitions','audit','clean'].includes(scenario)) {
    const displacement = (first, second) => second.y - first.y;
    check('validation/action-displacement', displacement(r.beforeValidation,r.withValidation), displacement(a.beforeValidation,a.withValidation), 1);
    check('validation/corrected-displacement', displacement(r.beforeValidation,r.correctedValidation), displacement(a.beforeValidation,a.correctedValidation), 1);
    check('validation/error-visible', true, a.validationText.length > 0);
    check('validation/corrected-error-cleared', '', a.correctedText);
    check('search/empty-height', r.emptySearch.height, a.emptySearch.height, 1);
    check('search/restored-height', r.restoredSearch.height, a.restoredSearch.height, 1);
    check('search/empty-feedback', true, /No documents/.test(a.emptyText));
    check('search/restored-result', true, /River transect/.test(a.restoredText));
  }
  if (['composition','audit','clean'].includes(scenario)) {
    check('split/writing-area-minimum', true, a.failedEditor.height >= 80);
    check('split/footer-inside-pane', true, a.failedFooter.y + a.failedFooter.height <= a.failedPane.y + a.failedPane.height - 15);
    check('split/notice-height', true, a.failedNotice.height <= 85);
    check('retry/global-failure-visible', false, a.retryGlobal.visible);
    check('retry/old-footer-status-visible', false, a.retryFooter.visible && /Saved/.test(a.retryFooter.text));
    check('retry/previous-detail-visible', false, a.retryDetail.visible);
    check('retry/status', 'Saving', a.retryLabel);
  }
  if (['layout','audit','clean','shared-views'].includes(scenario)) {
    for (const width of ['wideToolbar','narrowToolbar']) {
      const ar=a[width], rr=r[width];
      for (const member of ['rename','search','clear']) {
        const anchor=member === 'rename' ? 'create' : 'label';
        check(width + '/' + member + '/relative-row', rr[member].centerY-rr[anchor].centerY,
          ar[member].centerY-ar[anchor].centerY, 1);
        check(width + '/' + member + '/relative-spacing', rr[member].x-rr[anchor].x,
          ar[member].x-ar[anchor].x, 1);
      }
    }
    for (let i=0; i<r.preferenceRows.length; i++) {
      const rr=r.preferenceRows[i], ar=a.preferenceRows[i];
      check('preferences/' + i + '/action-alignment', rr.action.centerY-rr.select.centerY, ar.action.centerY-ar.select.centerY, 1);
      check('preferences/' + i + '/column-alignment', rr.select.x-r.preferenceRows[0].select.x, ar.select.x-a.preferenceRows[0].select.x, 1);
    }
    check('preferences/after-apply/select-edges', 0, a.appliedRows[0].selectRight-a.appliedRows[1].selectRight, 1);
    check('preferences/after-apply/action-edges', 0, a.appliedRows[0].actionLeft-a.appliedRows[1].actionLeft, 1);
    check('wrap/long-label-really-wraps', true, a.narrowLabel.height >= 40);
    check('wrap/find-label-with-field', r.narrowFind.centerY-r.narrowSearch.centerY, a.narrowFind.centerY-a.narrowSearch.centerY, 1);
    check('wrap/clear-with-field', r.narrowClear.centerY-r.narrowSearch.centerY, a.narrowClear.centerY-a.narrowSearch.centerY, 1);
    check('wrap/label-control-spacing', r.narrowSharing.y-r.narrowLabel.y-r.narrowLabel.height, a.narrowSharing.y-a.narrowLabel.y-a.narrowLabel.height, 1);
    check('wrap/preference-action-alignment', r.narrowApply.centerY-r.narrowSharing.centerY, a.narrowApply.centerY-a.narrowSharing.centerY, 1);
  }
  if (scenario === 'shared-views') {
    for (let i=0; i<r.preferenceRows.length; i++) {
      const rr=r.preferenceRows[i], ar=a.preferenceRows[i];
      check('workspace/' + i + '/label-column', rr.select.x-rr.label.x, ar.select.x-ar.label.x, 1);
      check('workspace/' + i + '/control-width', rr.select.width, ar.select.width, 1);
    }
    for (let i=0; i<r.archiveRows.length; i++) {
      const rr=r.archiveRows[i], ar=a.archiveRows[i];
      check('archive/' + rr.width + '/label-column', rr.select.x-rr.label.x, ar.select.x-ar.label.x, 1);
      check('archive/' + rr.width + '/action-alignment', rr.action.centerY-rr.select.centerY, ar.action.centerY-ar.select.centerY, 1);
      check('archive/' + rr.width + '/control-width', rr.select.width, ar.select.width, 1);
    }
    check('archive/applied-preference-in-workspace', 'Field report with observations', a.archivePreference);
  }
  return measurements;
}

async function main() {
  const [root, scenario] = process.argv.slice(2);
  if (!root || !scenario) throw new Error('Expected project root and GUI scenario.');
  const browser = await launch();
  try {
    const visualScenario = scenario === 'keyboard' ? 'design'
      : scenario === 'display-settings' ? 'rendering' : scenario;
    const reference = await inspect(browser, root, 'design', visualScenario);
    const application = await inspect(browser, root, 'app', visualScenario);
    const notebook = await inspectNotebook(browser);
    const keyboard = scenario === 'keyboard'
      ? await require('./gui_keyboard.cjs').inspectKeyboard(browser, take)
      : {measurements:[],images:[]};
    let display = {measurements:[],images:[]};
    if (scenario === 'display-settings') {
      const {inspectDisplay,compareDisplay} = require('./gui_display.cjs');
      const expected = await inspectDisplay(browser, 'design', take);
      const actual = await inspectDisplay(browser, 'app', take);
      display = {measurements:compareDisplay(expected,actual),images:[...expected.images,...actual.images]};
    }
    const measurements = [...compare(reference, application, visualScenario), ...notebook.measurements, ...keyboard.measurements, ...display.measurements];
    if (!measurements.length) throw new Error('No GUI contract measurements were produced.');
    process.stdout.write(JSON.stringify({matched:measurements.every(m => m.matched), measurements, images:[...reference.images,...application.images,...notebook.images,...keyboard.images,...display.images]}));
  } finally { await browser.close(); }
}

main().catch(error => { console.error(error.stack || String(error)); process.exitCode = 1; });
