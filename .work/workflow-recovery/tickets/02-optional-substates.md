# 02 Preserve optional wayfinding substates

**What to build:** Enter wayfinding optionally and restore its discussion after temporary work.

**Blocked by:** [Navigation records](01-navigation-records.md).

**Status:** blocked

- [ ] States may declare optional substates with guidance, an entry cue, related procedures,
      and formats. Only wayfinding is introduced as a substate.
- [ ] Enter and leave commands save the selected substate and return the appropriate guidance.
- [ ] Restoring planning reloads active wayfinding guidance and its format.
- [ ] Research and prototypes preserve active wayfinding and print its return command.
- [ ] Invalid entry, overlapping substates, and leaving the parent with an active substate fail
      without changing saved progress.
- [ ] Wayfinding retains its existing discussion format and covers the full agreed scope.
- [ ] Ordinary procedures and states without substates retain their current behavior.
- [ ] CLI tests cover restart during wayfinding, temporary research, optional entry, and leave.

## Accepted sources

[Optional substates](../spec.md#optional-substates).

## Completion evidence

Pending implementation.
