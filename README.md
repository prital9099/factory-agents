# Factory agents for Claude Code

A team of Claude Code agents plus a `/factory` skill that takes a feature from request to
merged code: **spec -> sprint plan -> build -> four reviews -> approval -> merge**.

## What is inside
| Agents (`agents/`) | Role |
|---|---|
| `spec-writer` | Coordinates the spec stage and runs the four `spec-*` helpers below |
| `spec-requirements` | Gathers requirements and asks questions; never assumes |
| `spec-visualizer` | Builds a clickable HTML mockup and `spec.md`; renders the narrated guide video last |
| `spec-testcases` | Writes Excel test cases, runs them on the mockup, records pass/fail |
| `spec-prompt-improver` | Rewrites the intake prompt for next time |
| `sprint-planner` | Plans feature-wise sprints in Excel after the HTML and video are approved; every test case covered |
| `builder` | Runs the approved sprint plan on its own branch: develops, tests and deploys each sprint before the next |
| `reviewer-security`, `reviewer-ux`, `reviewer-ui`, `reviewer-code` | Four review lenses |
| `approver` | Final gate: APPROVE (merge) or ESCALATE (human) |

The skill is `skills/factory/` (`/factory`), with a video helper in `skills/factory/tools/` and
question packs in `skills/factory/packs/`. See `CHANGES.md` for the latest changes.

## Install
1. Unzip this folder.
2. Run: `powershell -ExecutionPolicy Bypass -File install.ps1`
   (it copies everything into `%USERPROFILE%\.claude` and backs up files it would overwrite).
3. Run: `pip install -r requirements.txt`
4. Start a **new** Claude Code session.

## Approval gates (development mode)
No agent starts until you approve the previous agent's output. Reply `APPROVED` (or a plain yes) to
move on; anything else is treated as feedback and the **same** agent is re-run with it.
Say `STOP` to leave the job where it is.

| Gate | The user approves | Next |
|---|---|---|
| G1 | The draft HTML mockup and the answers to the questions | Final HTML is built, then the test cases from it |
| G2 | The final HTML and the test cases (with `spec.md`) | Only now the guide video is built |
| G3 | The guide video | `spec-prompt-improver` runs by itself, spec is done |
| G4 | Spec done (final HTML and video approved) | `sprint-planner` |
| G4.P | The sprint plan (`sprint-plan.xlsx`), every test case covered | `builder` |
| G4.S | Each builder sprint, after it is developed, tested and deployed | the builder's next sprint |
| G5 | `builder` (each round) | the four reviewers |
| G6 | the four reviews | `approver`, or the builder's rework |
| G7 | `approver` decision | merge to local `main` |

The spec order is fixed: **HTML -> test cases -> video**. G1 to G3 are asked by `spec-writer`.

Approvals are recorded in `factory/jobs/<job-id>/job.json` (`approvals`, `awaiting`).
To go back to a faster flow later, remove the "Approval gates" section from
`skills/factory/SKILL.md` and `agents/spec-writer.md`.

## Needs
- Windows (the guide video uses the built-in Windows voice), Chrome, Python 3, Claude Code.
- In each project: a git repo with a **`main`** branch, and an `AGENTS.md` (or `CLAUDE.md`)
  giving setup, test commands and conventions. Agents read it first.

## Use
In the project, start Claude Code and type:

    /factory <describe the feature>

It stops after every agent and asks for your approval (see Approval gates). Nothing is approved for
you. After the last gate it merges to a local `main` (nothing is pushed).

You can also ask Claude to use a single agent, e.g. "use the reviewer-security agent on this branch".

## Edit
Each agent is one Markdown file in `agents/`. Change its `model:`, `tools:` or instructions.
Agents are read when a session starts, so restart Claude Code after editing.

## Notes
- Job files go in `factory/jobs/` inside each project; add it to `.gitignore`.
- The test cases run on the HTML mockup, not on the finished software.
- Tested so far on one small Python project. Try a small feature first.
