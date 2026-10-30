'use strict';

const {projectPage} = require('./browser.cjs');

async function inspectKeyboard(browser, take) {
  const page = await projectPage(browser, {viewport:{width:1000,height:900}});
  page.setDefaultTimeout(5000);
  const measurements = [], images = [];
  const check = (name, actual) => measurements.push({name:'keyboard/'+name, expected:true, actual:!!actual, matched:!!actual});
  const focused = locator => locator.evaluate(element => element === document.activeElement);
  const appearance = locator => locator.evaluate(element => {
    const s=getComputedStyle(element);
    return {outline:s.outlineStyle !== 'none' && parseFloat(s.outlineWidth)>0 && s.outlineColor !== 'rgba(0, 0, 0, 0)', shadow:s.boxShadow, border:s.border, background:s.backgroundColor, color:s.color, decoration:s.textDecoration};
  });
  const tabTo = async locator => {
    if (!await locator.count()) return false;
    for (let i=0; i<24; i++) {
      await page.keyboard.press('Tab');
      if (await focused(locator)) return true;
    }
    return false;
  };
  try {
    for (const name of ['New document','Rename']) {
      for (const key of ['Enter','Space']) {
        await page.goto(new URL('app/index.html',process.env.EVAL_BROWSER_ORIGIN).href);
        const prefix=name+'/'+key, trigger=page.getByRole('button',{name,exact:true});
        if (!await trigger.count()) { check(prefix+'/reachable',false); continue; }
        const baseline=await appearance(trigger);
        const reached=await tabTo(trigger);
        check(prefix+'/reachable',reached);
        const active=await appearance(trigger);
        check(prefix+'/focus-visible',reached && (active.outline || Object.keys(baseline).some(k=>k!=='outline' && baseline[k]!==active[k])));
        await take(page,images,'app/keyboard-focus-'+name+'-'+key);
        await page.keyboard.press(key);
        const dialog=page.getByRole('dialog');
        const opened=await dialog.count() && await dialog.isVisible();
        check(prefix+'/activate',opened);
        // Continue observation of dialog focus even when activation itself failed.
        if (!opened) await trigger.click();
        if (!await dialog.count() || !await dialog.isVisible()) continue;
        const field=dialog.getByRole('textbox',{name:'Document name',exact:true});
        check(prefix+'/field-focused',await field.count() && await focused(field));
        await take(page,images,'app/keyboard-dialog-'+name+'-'+key);
        const cancel=dialog.getByRole('button',{name:'Cancel',exact:true});
        const cancelReached=await tabTo(cancel);
        check(prefix+'/cancel-reachable',cancelReached);
        if (cancelReached) await page.keyboard.press('Enter');
        check(prefix+'/cancel-closes',!await dialog.isVisible());
        check(prefix+'/cancel-focus-restored',await focused(trigger));
        if (await dialog.isVisible()) await cancel.click();
        if (await dialog.isVisible()) continue;
        await trigger.click();
        if (await field.count()) {
          await field.fill(name==='New document' ? 'Keyboard station' : 'Renamed station');
          await field.press('Enter');
          check(prefix+'/submit-closes',!await dialog.isVisible());
          check(prefix+'/submit-focus-restored',await focused(trigger));
        }
      }
    }
    return {measurements,images};
  } finally {await page.context().close();}
}
module.exports = {inspectKeyboard};
