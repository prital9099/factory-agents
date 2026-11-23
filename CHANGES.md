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

## 5. Test cases: one sheet per role, one scenario per case
- `spec-testcases`: plans coverage first (roles, features, screens, allowed and blocked
  actions), then writes one sheet per role. Never mixes roles; a shared feature gets a
  case on each role's sheet.
- One test case = one action and one expected outcome. Navigation, options, saving,
  Cancel and editing are separate cases; setup goes in Prerequisite, Steps hold only the
  action (normally 1 to 3 lines).
- Short "Verify ..." titles (max 8 words), simple English, no technical words.
- Positive, negative and permission cases are separate cases.
- Workbook format follows the user's sample (`skills/factory/templates/testcase-format.xlsx`):
  columns A-I (Test Case Id, Test Case Scenario Id, Test Case Scenario/Description,
  Prerequisite, Test Data, Steps, Expected Result, Actual Result, Status), header on row 1,
  Arial 11, blue header, medium borders; one sheet per role. Scenario ids
  `TS_<ROLE>_<SCREEN>_01` carry the role and screen. Prerequisites are written in full
  (no "same as above"). Coverage goes to `spec/testcase-coverage.md`.
- A self-check script flags mixed roles, multi-outcome results, long steps, jargon,
  duplicates and gaps before the agent finishes.
- `run_tests.py` and the builder's runner read columns by header name and run each case
  as its sheet's role.
- `spec-requirements`: the brief now lists, per role, the screens, the allowed actions and
  what the role must not do.

## 6. Complete coverage, checked by a tool
The test-case step no longer stops when it has written cases. It stops when a coverage check
passes.
- New `skills/factory/tools/tc_inventory.py`: opens the final mockup as every role, on every
  screen and every declared state, and lists every button, link, menu item, tab, dropdown
  (all options and default), field (required, min, max, length, format), checkbox, radio,
  table, count, message and empty state, and whether each control is enabled or disabled
  in each state.
- New `skills/factory/tools/tc_coverage.py`: from the inventory and `coverage-model.json`
  (rules, enable/disable conditions, calculations, cross-screen and cross-role flows,
  messages, exclusions with reasons, questions) it works out every required check:
  shown, works, default, each option, no selection, valid, empty, wrong format, each
  boundary, enabled and disabled, counts, messages, empty states, blocked pages and menu
  items per role, and desktop, tablet and mobile checks per screen and role. It matches
  `testcase-map.csv`, checks the writing rules, and writes `coverage-matrix.xlsx` and
  `coverage-gaps.json`. Exit 0 complete, 1 gaps or problems, 3 open questions.
- `spec-testcases`: 11-step order (analyse, roles, screens, controls, states, scenarios,
  calculations and flows, screen sizes, generate, validate, fill gaps), loops until the
  check passes, asks the user instead of guessing (`NEEDS_INPUT`), maps every case to its
  source requirement.
- `spec-visualizer`: test hooks in the page contract (`window.__mock` with roles, screens,
  states; `data-screen`, `data-nav`, `data-testid` on every control, `data-calc`,
  `data-msg`, `data-empty`; real limits and `disabled` states); `Mode: final` must pass the
  inventory.
- `spec-requirements`: asks about controls and their states, counts, effects on other
  screens and roles, and screen sizes; the brief has sections for them.
- `spec-writer`: handles `NEEDS_INPUT` and `BLOCKED` from the test-case step; Gate B shows the
  coverage summary and never opens with gaps.
- `builder`: reads the coverage files; runs screen-size and flow cases as written.

## 7. Only the test case workbook, page-wise
- `testcases.xlsx` is the only file the user gets. Coverage matrix, model, map and inventory
  are working files in `spec/.work/` and are never shown or listed.
- Layout follows the user's `Attendance_Testcases_v2.xlsx`: one sheet per role, cases grouped
  by page under a bold heading row `Feature: <feature> | Screen: <page>` in column C,
  `Save confirmation box` and `Access restrictions` as their own pages, Status `Not run`,
  full sentences, scenario ids `TS_<R><PAGE>_01`, titles up to 12 words.
- `tc_coverage.py`: takes `--cases`, skips heading rows, allows 12-word titles.

## 8. Not changed
The four reviewers, `approver` and `render_video.py`.

## Notes
- Not yet run end to end on a new job. Worked examples (jobs 001 and 002) are not in this repo.
