# Factory agents for Claude Code

A team of Claude Code agents plus a `/factory` skill that takes a feature from request to
merged code: **spec -> build -> four reviews -> approval -> merge**.

## What is inside
| Agents (`agents/`) | Role |
|---|---|
| `spec-writer` | Coordinates the spec stage and runs the four `spec-*` helpers below |
| `spec-requirements` | Gathers requirements and asks questions; never assumes |
| `spec-visualizer` | Builds a clickable HTML mockup, a narrated guide video and `spec.md` |
| `spec-testcases` | Writes Excel test cases, runs them on the mockup, records pass/fail |
| `spec-prompt-improver` | Rewrites the intake prompt for next time |
| `builder` | Implements the spec on its own branch and tests it |
| `reviewer-security`, `reviewer-ux`, `reviewer-ui`, `reviewer-code` | Four review lenses |
| `approver` | Final gate: APPROVE (merge) or ESCALATE (human) |

The skill is `skills/factory/` (`/factory`), with a video helper in `skills/factory/tools/`.

## Install
1. Unzip this folder.
2. Run: `powershell -ExecutionPolicy Bypass -File install.ps1`
   (it copies everything into `%USERPROFILE%\.claude` and backs up files it would overwrite).
3. Run: `pip install -r requirements.txt`
4. Start a **new** Claude Code session.

## Needs
- Windows (the guide video uses the built-in Windows voice), Chrome, Python 3, Claude Code.
- In each project: a git repo with a **`main`** branch, and an `AGENTS.md` (or `CLAUDE.md`)
  giving setup, test commands and conventions. Agents read it first.

## Use
In the project, start Claude Code and type:

    /factory <describe the feature>

The spec stage will stop and ask you questions, then ask you to approve the mockup/video/spec
and the test cases. Reply in chat. Nothing is approved for you. After the spec is approved
it builds, reviews and merges to a local `main` (nothing is pushed).

You can also ask Claude to use a single agent, e.g. "use the reviewer-security agent on this branch".

## Edit
Each agent is one Markdown file in `agents/`. Change its `model:`, `tools:` or instructions.
Agents are read when a session starts, so restart Claude Code after editing.

## Notes
- Job files go in `factory/jobs/` inside each project; add it to `.gitignore`.
- The test cases run on the HTML mockup, not on the finished software.
- Tested so far on one small Python project. Try a small feature first.
