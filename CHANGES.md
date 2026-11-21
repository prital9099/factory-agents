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

## 3. Builder works in sprints and stops after each one
- `builder` now follows the steps used to build and test the attendance app:
  1. Plan (sprint 1): read the spec, brief, test cases, mockup and test data; gap analysis
     (missing, beyond requirements, conflicts between test cases and brief); open questions;
     `SPRINTS.md` sprint plan.
  2. Development sprints: one per run, rules before screens, names and messages taken from the
     test cases, automated tests, browser check at desktop and phone width, commit.
  3. Test preparation: optional test-only fixed date, test fixture reset before every case,
     Playwright runner on visible Chrome with a live banner, results written to a copy of the
     workbook in `test-results/`, runner checked against planted layout problems.
  4. Test sprints: one area of the test cases per run, results by role and screen, every failure
     explained (app bug, wrong test, conflict with the brief); conflict decisions recorded.
- The builder stops after every sprint with `STATUS: NEEDS_INPUT` in `build.md`. Nothing beyond
  the brief and the test cases is built; the brief wins every conflict.
- `skills/factory/SKILL.md`: new gate **G4.S** handles each builder sprint (resume with the
  user's reply verbatim; these resumes do not count toward `MAX_RESUMES`); `test-results/` added
  to the job files.

## 4. Not changed
The four reviewers, `approver` and `render_video.py`.

## Notes
- Not yet run end to end on a new job. Worked examples (jobs 001 and 002) are not in this repo.
