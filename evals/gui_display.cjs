'use strict';

const {projectPage} = require('./browser.cjs');

async function inspectDisplay(browser, directory, take) {
  const page = await projectPage(browser, {viewport:{width:1000,height:900},colorScheme:'light'});
  page.setDefaultTimeout(5000);
  const images=[], values={};
  const button=(name,scope=page)=>scope.getByRole('button',{name,exact:true});
  const input=()=>page.getByRole('textbox',{name:'Document name',exact:true});
  const dialog=()=>page.getByRole('dialog');
  const colors=locator=>locator.evaluate(element=>{
    const style=getComputedStyle(element);
    const border=['Top','Right','Bottom','Left'].map(side=>{
      const visible=parseFloat(style[`border${side}Width`])>0
        && !['none','hidden'].includes(style[`border${side}Style`]);
      return visible?style[`border${side}Color`]:'none';
    }).join('|');
    return {color:style.color,background:style.backgroundColor,border,image:style.backgroundImage,
      visible:!!element.getBoundingClientRect().width && style.visibility!=='hidden'};
  });
  try {
    await page.goto(new URL(directory+'/index.html',process.env.EVAL_BROWSER_ORIGIN).href);
    await button('New document').click();
    for (const appearance of ['light','dark','light']) {
      await page.emulateMedia({colorScheme:appearance});
      const key=Object.keys(values).length===2?'restored':appearance;
      await input().fill('');
      await button('Create',dialog()).click();
      values[key]={
        page:await colors(page.locator('html')),
        editor:await colors(page.getByRole('textbox',{name:'Document text',exact:true})),
        select:await colors(page.getByRole('combobox',{name:'Format',exact:true})),
        trigger:await colors(button('New document')),
        dialog:await colors(dialog()),
        field:await colors(input()),
        feedback:await colors(dialog().getByRole('alert')),
        feedbackVisible:await dialog().getByRole('alert').isVisible(),
        feedbackText:await dialog().getByRole('alert').innerText(),
      };
      await input().fill('Unfinished field note');
      await take(page,images,directory+'/appearance-'+key);
      // Change the live setting with an unsaved field, without reopening the dialog.
      await page.emulateMedia({colorScheme:appearance==='light'?'dark':'light'});
      values[key].retainedText=await input().inputValue();
      values[key].dialogOpen=await dialog().isVisible();
    }
    return {values,images};
  } finally {await page.context().close();}
}

function compareDisplay(reference,application) {
  const measurements=[];
  const check=(name,expected,actual)=>measurements.push({name:'appearance/'+name,expected,actual,matched:expected===actual});
  for (const mode of ['light','dark','restored']) {
    const expected=reference.values[mode], actual=application.values[mode];
    for (const element of ['page','editor','select','trigger','dialog','field','feedback']) {
      for (const style of ['color','background','border','image','visible']) {
        check(mode+'/'+element+'/'+style,expected[element][style],actual[element][style]);
      }
    }
    check(mode+'/error-visible',true,actual.feedbackVisible && actual.feedbackText.trim().length>0);
    check(mode+'/unsaved-text','Unfinished field note',actual.retainedText);
    check(mode+'/open-dialog',true,actual.dialogOpen);
  }
  return measurements;
}
module.exports={inspectDisplay,compareDisplay};
