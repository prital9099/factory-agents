# Changes on branch `ba-workflow`

Based on `approval-gates`. Install with `install.ps1`, then start a new Claude Code session.

## 1. The reader is a business analyst (BA), not a junior person
- `spec-writer` and `spec-requirements` now write for a BA who decides every requirement
  alone. Business terms and light technical terms are allowed; no file paths in text.
- The manager routing is removed: no "Ask your manager" tag, no `manager-questions.md`.
  Every question is tagged "You can answer".
- `skills/factory/packs/attendance.md`: the `[manager]` tags became `[you]`.

## 2. Spec order is now HTML -> test cases -> video
| Gate | The user approves | Next |
|---|---|---|
| G1 | Draft HTML mockup and answers | Final HTML, then test cases from it |
| G2 | Final HTML and test cases (with `spec.md`) | Guide video is built |
| G3 | Guide video | Prompt improver, spec done |

- `spec-visualizer`: `final` mode builds HTML and `spec.md` only. New `video` mode renders
  `guide.mp4` from the frozen HTML and must not change anything the test cases use.
- `spec-testcases`: runs after the final HTML and before any video exists.
- `spec-writer`: phases 3 to 5 follow the new order; video feedback only re-renders the video.
- `skills/factory/SKILL.md`: gate table, "what to open" order and step text updated; question
  packs added under `skills/factory/packs/`.

## 3. Not changed
`builder`, the four reviewers, `approver` and `render_video.py`.

## Notes
- Not yet run end to end on a new job. Worked examples (jobs 001 and 002) are not in this repo.
