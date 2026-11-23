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

## 4. New sprint-planner agent
- `agents/sprint-planner.md`: plans the development sprints after the spec is done.
  - Starts only when the final HTML and the guide video are approved (Gates B and C); otherwise BLOCKED.
  - Writes `sprint-plan.xlsx` with exactly two columns, Sprint Name and Sprint Description.
  - Sprints are feature-wise, never role-wise; login is left out of the plan.
  - A coverage check must show every test case in exactly one sprint (login cases listed apart)
    before the plan goes to the user; development starts only after approval, one sprint at a time.
- Wired into `/factory`: new stage `plan` and gate **G4.P** between the spec (G4) and the build.
  The sprint planner runs after G4; once the user approves the plan it writes `DONE` and the
  builder starts. A requirement change after G2 makes the plan stale and it is planned again.
- `agents/builder.md`: no longer makes its own sprint plan. Phase 1 checks the approved plan; the
  development sprints are the plan's sprints (same names, same order, each a whole feature for
  every role), with one test sprint per plan sprint from `sprint-coverage.md`. If the app needs
  sign-in, the builder asks at its first gate instead of adding a sprint.
- `agents/spec-writer.md` and `README.md`: step 4 is now sprint planning.
- The last sprint-planner rule now covers the whole process: each sprint is developed, tested
  and deployed, and the next sprint starts only when all three are done and the user approves.
  `agents/builder.md` follows it: Phase 1 checks the plan and finds the deployment target,
  Phase 2 prepares the test run once, Phase 3 runs every sprint as develop → test (its own cases,
  plus the earlier sprints' cases again) → deploy → gate. With no deploy target in AGENTS.md, a
  sprint is deployed locally; production is never a sprint deployment.

## 5. Not changed
The four reviewers, `approver` and `render_video.py`.

## Notes
- Not yet run end to end on a new job. Worked examples (jobs 001 and 002) are not in this repo.
