"""Navigation receipts at the external Chromium protocol boundary."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from pydantic import JsonValue, TypeAdapter

MODULE = Path(__file__).resolve().parents[1] / "evals/browser_navigation.cjs"
PROTOCOL = """
const {EventEmitter} = require('events');
const {observeNavigation} = require(MODULE);
class Protocol extends EventEmitter {
  constructor() {
    super(); this.frame = {id:'main', loaderId:'blank', url:'about:blank'};
  }
  async send(method) {
    if (this.fail) throw Error('protocol unavailable');
    if (method === 'Page.enable' && this.duringEnable) this.duringEnable();
    return {frameTree:{frame:this.frame}};
  }
  async detach() {}
  commit(loaderId, url, frameId='main') {
    const frame={id:frameId, loaderId, url};
    if (frameId === 'main') this.frame=frame;
    this.emit('Page.frameNavigated',{frame});
  }
  load(loaderId, frameId='main') {
    this.emit('Page.lifecycleEvent',{frameId,loaderId,name:'load'});
  }
}
const session=new Protocol();
const page={context:()=>({newCDPSession:async()=>session})};
""".replace("MODULE", json.dumps(str(MODULE)))


class BrowserNavigationProtocolTests(unittest.TestCase):
    def observe(self, script: str) -> dict[str, JsonValue]:
        result = subprocess.run(
            [
                "node",
                "-e",
                PROTOCOL
                + "\n(async()=>{"
                + script
                + "})().catch(error=>{console.error(error);process.exitCode=1});",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return TypeAdapter(dict[str, JsonValue]).validate_json(result.stdout)

    def test_delayed_initial_load_keeps_its_commit_attribution(self) -> None:
        receipt = self.observe(
            """
const observer=await observeNavigation(page);
session.commit('initial','http://local/page');
observer.setActionIndex(4);
session.load('initial');
session.commit('child','http://local/frame','child-frame');
session.load('child','child-frame');
session.emit('Page.navigatedWithinDocument',{frameId:'main',url:'http://local/page#part'});
session.load('initial');
await observer.finish(); console.log(JSON.stringify(observer.navigation));
"""
        )
        self.assertEqual(receipt["status"], "complete")
        events = TypeAdapter(list[dict[str, JsonValue]]).validate_python(
            receipt["events"]
        )
        self.assertEqual(
            [event["kind"] for event in events],
            [
                "main_document_commit",
                "main_document_load",
                "same_document_navigation",
            ],
        )
        self.assertTrue(all(event["document_sequence"] == 1 for event in events))
        self.assertTrue(
            all(event["committed_during_action_index"] is None for event in events)
        )
        self.assertEqual(events[1]["observed_during_action_index"], 4)

    def test_interrupted_load_does_not_gain_a_completed_load(self) -> None:
        receipt = self.observe(
            """
const observer=await observeNavigation(page);
session.commit('first','http://local/first'); session.load('first');
observer.setActionIndex(2);
session.commit('interrupted','http://local/interrupted');
session.emit('Network.loadingFailed',{type:'Document',canceled:true});
observer.setActionIndex(3);
session.commit('last','http://local/last'); session.load('last');
await observer.finish(); console.log(JSON.stringify(observer.navigation));
"""
        )
        self.assertEqual(receipt["status"], "complete")
        events = TypeAdapter(list[dict[str, JsonValue]]).validate_python(
            receipt["events"]
        )
        self.assertEqual(
            [event["document_sequence"] for event in events], [1, 1, 2, 3, 3]
        )
        self.assertEqual(events[2]["kind"], "main_document_commit")
        self.assertEqual(events[2]["committed_during_action_index"], 2)

    def test_unavailable_observer_is_not_an_empty_complete_recording(self) -> None:
        receipt = self.observe(
            """
session.fail=true;
const observer=await observeNavigation(page);
await observer.finish(); console.log(JSON.stringify(observer.navigation));
"""
        )
        self.assertEqual(receipt["status"], "unavailable")
        self.assertEqual(receipt["events"], [])
        self.assertIn(
            "protocol unavailable", TypeAdapter(str).validate_python(receipt["error"])
        )

    def test_protocol_loss_preserves_events_and_marks_partial(self) -> None:
        receipt = self.observe(
            """
const observer=await observeNavigation(page);
session.commit('first','http://local/first');
session.fail=true;
await observer.finish(); console.log(JSON.stringify(observer.navigation));
"""
        )
        self.assertEqual(receipt["status"], "partial")
        self.assertEqual(
            len(
                TypeAdapter(list[dict[str, JsonValue]]).validate_python(
                    receipt["events"]
                )
            ),
            1,
        )
        self.assertIn(
            "protocol unavailable", TypeAdapter(str).validate_python(receipt["error"])
        )

    def test_setup_event_loss_cannot_be_overwritten_by_successful_enable(self) -> None:
        receipt = self.observe(
            """
session.duringEnable=()=>session.emit('Page.frameNavigated',{frame:{id:'main',url:'http://local/page'}});
const observer=await observeNavigation(page);
await observer.finish(); console.log(JSON.stringify(observer.navigation));
"""
        )
        self.assertIn(receipt["status"], ["partial", "unavailable"])
        self.assertIn(
            "loader identity", TypeAdapter(str).validate_python(receipt["error"])
        )

    def test_unobserved_main_document_cannot_look_like_no_navigation(self) -> None:
        receipt = self.observe(
            """
const observer=await observeNavigation(page);
session.frame={id:'main',loaderId:'unobserved',url:'http://local/page'};
await observer.finish(); console.log(JSON.stringify(observer.navigation));
"""
        )
        self.assertEqual(receipt["status"], "partial")
        self.assertEqual(receipt["events"], [])
        self.assertIn("commit", TypeAdapter(str).validate_python(receipt["error"]))

    def test_known_loader_keeps_document_identity_at_same_url(self) -> None:
        receipt = self.observe(
            """
const observer=await observeNavigation(page);
session.commit('original','http://local/page'); session.load('original');
observer.setActionIndex(2);
session.commit('original','http://local/page'); session.load('original');
observer.setActionIndex(3);
session.commit('fresh-reload','http://local/page'); session.load('fresh-reload');
await observer.finish(); console.log(JSON.stringify(observer.navigation));
"""
        )
        events = TypeAdapter(list[dict[str, JsonValue]]).validate_python(
            receipt["events"]
        )
        self.assertEqual(
            [event["document_sequence"] for event in events], [1, 1, 1, 2, 2]
        )
        self.assertEqual(events[2]["committed_during_action_index"], 2)
        self.assertEqual(events[3]["committed_during_action_index"], 3)

    def test_missing_reactivation_of_known_document_marks_partial(self) -> None:
        receipt = self.observe(
            """
const observer=await observeNavigation(page);
session.commit('first','http://local/first'); session.load('first');
session.commit('second','http://local/second'); session.load('second');
session.frame={id:'main',loaderId:'first',url:'http://local/first'};
await observer.finish(); console.log(JSON.stringify(observer.navigation));
"""
        )
        self.assertEqual(receipt["status"], "partial")
        self.assertIn("commit", TypeAdapter(str).validate_python(receipt["error"]))
        events = TypeAdapter(list[dict[str, JsonValue]]).validate_python(
            receipt["events"]
        )
        self.assertEqual([event["document_sequence"] for event in events], [1, 1, 2, 2])
