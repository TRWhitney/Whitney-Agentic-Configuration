"""The agenda fixture separates working data flow from defective presentation."""

from __future__ import annotations

import json
import subprocess
import unittest

from pydantic import TypeAdapter

from evals.fixtures import make_workspace
from evals.gui import candidate_browser
from evals.models import load_cases
from evals.runner import Observation, check_result
from tests.test_eval_runner import SOURCE

DETAILS = r"""(() => {
 const paragraphs=SOURCE_DESCRIPTION.split('\n\n');
 const locationText=SOURCE_LOCATION;
 const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
 const nodes=[];let node;
 while(node=walker.nextNode()) {
  if(node.parentElement.closest('script,style,textarea')) continue;
  const range=document.createRange();range.selectNodeContents(node);
  if([...range.getClientRects()].some(r=>r.width>0&&r.height>0)) nodes.push(node);
 }
 const full=nodes.map(n=>n.textContent).join('');
 function span(text) {
  const at=full.indexOf(text);
  if(at<0)throw new Error('Visible source content absent: '+text);
  let offset=0,start,end;
  for(const n of nodes){const next=offset+n.textContent.length;
   if(start===undefined && at<next)start=[n,at-offset];
   if(at+text.length<=next){end=[n,at+text.length-offset];break;}offset=next;
  }
  const range=document.createRange();
  range.setStart(...start);range.setEnd(...end);return range;
 }
 const pairs=[];
 for(let i=0;i<paragraphs.length-1;i++){
  const before=span(paragraphs[i]);
  before.setStart(before.endContainer,before.endOffset-1);
  const after=span(paragraphs[i+1]);
  after.setEnd(after.startContainer,after.startOffset+1);
  const gap=after.getBoundingClientRect().top-before.getBoundingClientRect().top;
  const style=getComputedStyle(before.startContainer.parentElement);
  const line=parseFloat(style.lineHeight);
  pairs.push({gap,line});
 }
 const range=span(locationText),rects=[...range.getClientRects()].map(r=>r.toJSON());
 let clipped=false;
 const common=range.commonAncestorContainer;
 const ancestor=common.nodeType===1?common:common.parentElement;
 for(let e=ancestor;e;e=e.parentElement){
  const style=getComputedStyle(e),box=e.getBoundingClientRect();
  const outsideX=rects.some(r=>r.x<box.x-1||r.right>box.right+1);
  const outsideY=rects.some(r=>r.y<box.y-1||r.bottom>box.bottom+1);
  if(/hidden|clip/.test(style.overflowX)&&outsideX)clipped=true;
  if(/hidden|clip/.test(style.overflowY)&&outsideY)clipped=true;
 }
 return {
  paragraphsSeparate:pairs.length>0&&pairs.every(p=>p.gap>=p.line*1.5),
  fullLocationVisible:!clipped&&rects.every(r=>r.left>=-1&&r.right<=innerWidth+1)
 };
})()"""
FOCUS = """(() => {
 const r=document.activeElement.getBoundingClientRect();
 const nav=document.querySelector('nav').getBoundingClientRect();
 return {focusVisible:r.left>=Math.max(nav.left,0)-1 &&
 r.right<=Math.min(nav.right,innerWidth)+1 && r.top>=-1 && r.bottom<=innerHeight+1};
})()"""
NOTE_VALUE = "document.querySelector('textarea[aria-label^=\"Your notes for\"]').value"
NOTE = NOTE_VALUE + "==='Bring maps'"
ERROR_TEXT = 'document.querySelector("#load-error").textContent'
EVENT_TITLE = 'document.querySelector("#event-title").textContent'


class VisualStateSelectionTests(unittest.TestCase):
    def test_note_check_accepts_compatibility_and_rejects_lost_existing_notes(
        self,
    ) -> None:
        case = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "gui-state-selection"
        )
        check = next(
            check
            for step in case.steps
            for check in step.checks
            if check.kind == "python_check"
        )
        for variant in ("compatible", "labelled", "fallback", "migration", "lost"):
            with (
                self.subTest(variant=variant),
                make_workspace(SOURCE, case) as workspace,
            ):
                if variant == "labelled":
                    app = workspace.file("app/app.mjs")
                    app.write_text(
                        app.read_text()
                        .replace(
                            "const label=document.createElement('label');",
                            "const label=document.createElement('div');"
                            "label.id='notes-'+session.id;",
                        )
                        .replace(
                            "input.setAttribute('aria-label','Your notes for '"
                            "+session.title)",
                            "input.setAttribute('aria-labelledby',label.id)",
                        )
                        .replace(
                            "label.append(input); card.append(heading,details,label);",
                            "card.append(heading,details,label,input);",
                        )
                    )
                elif variant != "compatible":
                    model = workspace.file("app/model.mjs")
                    model.write_text(
                        model.read_text().replace(
                            "'agenda-note:'+session.id", "'new-note:'+session.id"
                        )
                    )
                    app = workspace.file("app/app.mjs")
                    if variant == "fallback":
                        app.write_text(
                            app.read_text().replace(
                                "localStorage.getItem(noteKey(session))||''",
                                "localStorage.getItem(noteKey(session))??"
                                "localStorage.getItem('agenda-note:'+session.id)??''",
                            )
                        )
                    elif variant == "migration":
                        app.write_text(
                            app.read_text().replace(
                                "let selected=0;",
                                "for(const day of agenda.days){"
                                "for(const session of day.sessions){"
                                "const old=localStorage.getItem(\n"
                                "'agenda-note:'+session.id);"
                                "if(old!==null&&"
                                "localStorage.getItem(noteKey(session))===null)"
                                "localStorage.setItem(noteKey(session),old);}}"
                                "let selected=0;",
                            )
                        )
                worker = workspace.browser_worker
                assert worker is not None
                request = workspace.home / "candidate-inspection.json"
                request.write_text(json.dumps({"page": "app/index.html", "steps": []}))
                self.assertEqual(worker._execute(request)["returncode"], 0)
                before = candidate_browser(workspace)
                passed, detail = check_result(
                    check, Observation(), workspace, "main", []
                )
                self.assertEqual(passed, variant != "lost", detail)
                receipts = candidate_browser(workspace)
                self.assertTrue(receipts)
                self.assertEqual(receipts, before)

    def test_data_checks_miss_rendered_defects_and_repairs_preserve_notes(self) -> None:
        case = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "gui-state-selection"
        )
        event = json.loads(case.files["examples/river-conference.json"])
        session = event["days"][0]["sessions"][0]
        detail_query = DETAILS.replace(
            "SOURCE_DESCRIPTION", json.dumps(session["description"])
        ).replace("SOURCE_LOCATION", json.dumps(session["location"]))
        for variant in ("initial", "scrolling", "wrapped"):
            finished = variant != "initial"
            with (
                self.subTest(variant=variant),
                make_workspace(SOURCE, case) as workspace,
            ):
                if finished:
                    files = json.loads(
                        (
                            SOURCE / "evals/cases/fixtures/agenda-finished.json"
                        ).read_text()
                    )
                    for path, text in files.items():
                        workspace.file(path).write_text(text)
                    if variant == "wrapped":
                        css = workspace.file("app/app.css")
                        css.write_text(
                            css.read_text()
                            + "\n#days {flex-wrap:wrap; overflow:visible;}"
                            + "\n.description {white-space:normal;}\n"
                        )
                        app = workspace.file("app/app.mjs")
                        app.write_text(
                            app.read_text().replace(
                                "description.textContent=session.description;",
                                "const parts=session.description.split('\\n\\n');"
                                "for(const text of parts){"
                                "const p=document.createElement('p');"
                                "p.textContent=text;description.append(p);}",
                            )
                        )
                checked = subprocess.run(
                    ["node", "checks/agenda.mjs"],
                    cwd=workspace.root,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                self.assertEqual(checked.returncode, 0, checked.stderr)
                steps = [
                    {"action": "click", "selector": "#load-panel summary"},
                    {
                        "action": "fill",
                        "selector": "#agenda-input",
                        "value": json.dumps(event),
                    },
                    {"action": "click", "selector": "#load"},
                    {"action": "click", "selector": "#load-panel summary"},
                    {
                        "action": "press",
                        "selector": "[role=tab]:first-child",
                        "key": "End",
                    },
                    {"action": "evaluate", "script": FOCUS},
                    {"action": "click", "selector": ".session summary"},
                    {"action": "evaluate", "script": detail_query},
                    {
                        "action": "fill",
                        "selector": 'textarea[aria-label^="Your notes for"]',
                        "value": "Bring maps",
                    },
                    {
                        "action": "press",
                        "selector": "[role=tab]:first-child",
                        "key": "Home",
                    },
                    {
                        "action": "evaluate",
                        "script": "({otherNoteEmpty:!" + NOTE_VALUE + "})",
                    },
                    {
                        "action": "press",
                        "selector": "[role=tab]:first-child",
                        "key": "End",
                    },
                    {"action": "evaluate", "script": "({noteRetained:" + NOTE + "})"},
                    {"action": "evaluate", "script": "location.reload()"},
                    {"action": "wait", "ms": 250},
                    {
                        "action": "press",
                        "selector": "[role=tab]:first-child",
                        "key": "End",
                    },
                    {"action": "evaluate", "script": "({noteRetained:" + NOTE + "})"},
                    {"action": "click", "selector": "#load-panel summary"},
                    {
                        "action": "fill",
                        "selector": "#agenda-input",
                        "value": "not event json",
                    },
                    {"action": "click", "selector": "#load"},
                    {
                        "action": "evaluate",
                        "script": "({noteRetained:"
                        + NOTE
                        + ",errorShown:!!"
                        + ERROR_TEXT
                        + ",eventRetained:"
                        + EVENT_TITLE
                        + "==="
                        + json.dumps(event["title"])
                        + "})",
                    },
                ]
                request = workspace.home / "fixture-check.json"
                request.write_text(
                    json.dumps(
                        {
                            "page": "app/index.html",
                            "viewport": {"width": 390, "height": 420},
                            "steps": steps,
                        }
                    )
                )
                worker = workspace.browser_worker
                assert worker is not None
                result = worker._execute(request)
                self.assertEqual(result["returncode"], 0, result.get("stderr"))
                response = result["result"]
                assert isinstance(response, dict)
                observations = response["observations"]
                assert isinstance(observations, list)
                measured = TypeAdapter(list[dict[str, bool]]).validate_python(
                    [o for o in observations if o is not None]
                )
                self.assertEqual(
                    measured[:2],
                    [
                        {"focusVisible": finished},
                        {
                            "paragraphsSeparate": finished,
                            "fullLocationVisible": finished,
                        },
                    ],
                )
                for values in measured[2:]:
                    self.assertTrue(all(values.values()), values)


if __name__ == "__main__":
    unittest.main()
