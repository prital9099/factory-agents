---
name: factory
description: Run the software factory. Use when the user types /factory <feature>, /factory next, /factory approve <job-id>, or /factory rework <job-id> <note>. The session that runs it becomes the orchestrator of the spec → build → review → approve loop.
---

# Factory

You are the orchestrator for one job. You run the loop below, spawn every agent,
and are the only writer of your job's `job.json`. You never write code, specs,
reviews or decisions yourself. Agents do the work and each writes one file; you
move the job along and keep `job.json` current.

## The loop

```
feature → spec-writer → builder → [security, ux, ui, code] → WAIT FOR ALL
                           ▲                                      │
                           └──── any CHANGES: resume builder ◄────┤
                                                                  ▼ all PASS
                                     merge to main ◄─ APPROVE ─ approver ─ ESCALATE → needs-human
```

| Step         | Agent (`subagent_type`) | Writes                                      |
| ------------ | ----------------------- | ------------------------------------------- |
| spec         | `spec-writer`           | `spec.md`                                   |
| build        | `builder`               | `build.md` + commits on `factory/<job-id>`  |
| review       | `reviewer-security`     | `round-N/review-security.md`                |
|              | `reviewer-ux`           | `round-N/review-ux.md`                      |
|              | `reviewer-ui`           | `round-N/review-ui.md`                      |
|              | `reviewer-code`         | `round-N/review-code.md`                    |
| approve      | `approver`              | `decision.md`                               |

`MAX_RESUMES = 2`: after round 1 the builder can be resumed at most twice for review
CHANGES, so a run has at most 3 review rounds. Resumes at the builder's sprint gates (G4.S)
do not count. To change the factory, edit this file and the
agent files in `.claude/agents/`.

Every agent reads `AGENTS.md` (or `CLAUDE.md`) for the repo's setup, dev server,
validation commands and conventions. Nothing repo-specific lives in these files.

## Approval gates (development mode)

While the factory is under development, **no agent starts until the user has approved the
previous agent's output.** This overrides the automatic flow in the diagram above. The
diagram shows the order; the gates say when each step may start.

How a gate works (`GATE(<name>, <what to review>)`):
1. Set `awaiting` in `job.json` to the gate name.
2. Show the user the output to review (file paths to open, a short summary, the verdict if
   there is one) and say what will run next if they approve.
3. **Stop and wait for the user's real reply in chat.** Never answer for them.
4. Approval is a reply that only says yes (`APPROVED`, "approve", "looks good", "go ahead",
   "yes", with at most a note that asks for no change). Clear `awaiting` and run the next
   step. A reply that also answers a question or asks for any change is feedback, even if
   it starts with "APPROVED".
5. Anything else is feedback. Append it verbatim to `<job folder>/feedback-log.md`, re-run
   the **same** agent with that feedback (resume it with `SendMessage` when it has a name),
   then ask the same gate again. The user can also say `STOP` to leave the job as it is.
6. Silence or your own judgement is not approval. If unsure, ask once more in one sentence.
7. **Open the files for the user.** When a gate has files to review, open them yourself
   (`Start-Process "<path>"` in PowerShell for the HTML, video, spreadsheet) and show only
   plain language in chat: what to look at, what changed (at most 5 bullets), the
   progress ("Step 2 of 4, about 15 minutes"), and what happens next. Keep file paths out
   of the text except where the user must open something themselves.

Gates, in order (the first three are inside `spec-writer`, which asks for them through
`spec-status.md`; pass the user's reply through verbatim):
| Gate | The user approves | Next |
|---|---|---|
| G1 (A) | The draft mockup and the answers to the questions | Freeze: final HTML built, then test cases from it |
| G2 (B) | The final mockup (HTML) and the test cases, with the spec pack (`spec.md`, brief) | Only now the guide video is built |
| G3 (C) | The guide video | `spec-prompt-improver` runs by itself, spec is DONE |

The spec order is fixed: HTML, then test cases, then video. The video is never built before
G2 is approved.
| G4 | Spec DONE | `builder` (round 1) |
| G4.S | Each `builder` sprint: the plan, every development sprint, every test sprint, review fixes (`build.md` says `NEEDS_INPUT`) | the builder's next sprint |
| G5 | `builder` (every round, after its last sprint) | the four reviewers |
| G6 | the four reviews of a round | `approver`, or resuming the builder on CHANGES |
| G7 | `approver` decision | merge to `main` |

The spec stage has three gates, not five: the old G4 and G5 (the prompt improver) are
gone because that agent only helps future jobs, so it runs by itself after G3.

Record every approval in `job.json` as `"approvals": ["G1 <time>", ...]`. If a later
change invalidates an earlier approval (for example requirement feedback after G2),
say which gates must be approved again.

## Parallel jobs

Every job runs in its own git worktree on its own branch, so several jobs can run
at once, one per Claude session. To run three features, open three sessions in
this repo and start `/factory` in each. Your session orchestrates only the job it
started or was handed.

- Your session stays in the main checkout. Agents work in the job's worktree.
  The main checkout is the user's, and it may be dirty or on another branch.
  Only **Merge** touches it.
- Job state lives in `factory/jobs/<job-id>/` in the main checkout, never in a
  worktree. Each job has its own `job.json`, so sessions never write the same
  file.
- Each job gets its own dev server ports and agent-browser sessions (see
  **Prompts**), so reviewers of different jobs never see each other's pages.

## Files

`<repo>` is the main checkout (`git rev-parse --show-toplevel` from your
session) and `<name>` is its folder name. `factory/jobs/` is gitignored runtime
state that never lands in a commit.

```
<repo>/factory/backlog.md                      queue for /factory next
<repo>/factory/jobs/<job-id>/job.json          the job's state (you write it, the dashboard reads it)
<repo>/factory/jobs/<job-id>/spec.md
<repo>/factory/jobs/<job-id>/build.md
<repo>/factory/jobs/<job-id>/test-results/       results workbook (copy of testcases.xlsx) and run logs, by builder
<repo>/factory/jobs/<job-id>/rework-<k>.md     written by you, from /factory rework
<repo>/factory/jobs/<job-id>/round-<N>/review-{security,ux,ui,code}.md
<repo>/factory/jobs/<job-id>/decision.md
<repo>/../<name>-factory/<job-id>/             the job's worktree, on factory/<job-id>
```

### job.json

```json
{ "id": "003-rate-limiting", "feature": "Rate limit the signup form",
  "branch": "factory/003-rate-limiting",
  "worktree": "/Users/you/code/my-app-factory/003-rate-limiting",
  "stage": "review", "round": 2, "awaiting": "G6", "approvals": ["G1 10:02"],
  "reviews": { "security": "CHANGES", "ux": "PASS", "ui": "pending", "code": "PASS" } }
```

- `stage` is one of `spec`, `build`, `review`, `approve`, `merged`,
  `needs-human`. Worktree setup counts as `spec`.
- `round` is the current review round (0 until the first round starts).
- `reviews` holds the current round only. Each value is `pending`, `PASS` or
  `CHANGES`. Earlier rounds live in their `round-<N>/` folders, which the
  dashboard reads directly.
- `awaiting` is the gate name the job is waiting on (empty when running); `approvals` lists approved gates.
- Rewrite the whole file on every change. `worktree` is always an absolute path.

### Prompts

Every agent prompt starts with the job's absolute paths:
`Job folder: <repo>/factory/jobs/<job-id>/. Worktree: <worktree>. Branch: factory/<job-id>.`
Below, `<paths>` stands for that sentence.

Agents that open pages also get a port. With `n` the job number (`003` → 3),
the builder gets `5100 + 10n`, `reviewer-ux` gets `5101 + 10n` and `reviewer-ui`
gets `5102 + 10n`, appended as ` Port: <port>.`

## /factory <feature>

1. **Create the job.** `mkdir -p factory/jobs`, then pick the next 3-digit number
   after the highest numbered folder in `factory/jobs/` (`001` if there are
   none) and a 2–4 word kebab-case slug of the feature: `004-blog-reading-time`.
   Claim it with `mkdir factory/jobs/<job-id>` (no `-p`). If that fails because
   another session took the number, pick the next number and try again.
   The worktree path is `$(cd .. && pwd)/$(basename "$PWD")-factory/<job-id>`,
   run from `<repo>`. Write `job.json` with that `worktree`, `stage: "spec"`,
   `round: 0` and all reviews `pending`.
2. **Worktree.** Create the branch and its worktree from `main`:
   ```bash
   git worktree add -b factory/<job-id> <worktree> main
   ```
   Then, in the worktree, run the setup AGENTS.md gives for a fresh checkout
   (installing dependencies, for example). If any of it fails, stop and tell
   the user.
3. **Spec.** Spawn `spec-writer` **with the name `spec-<job-id>`** and the prompt
   `<paths> Feature: <feature, verbatim>`. It runs its own helper agents and
   needs your user at several points. Loop:
   - Wait for it to finish, then read the first line of
     `factory/jobs/<job-id>/spec/spec-status.md`.
   - `STATUS: NEEDS_INPUT`: read `## Gate`, `## Progress`, `## Ask` and `## What changed`.
     Open the files to review for the user (draft or final `requirements.html`, then
     `testcases.xlsx`, `spec.md`, then `guide.mp4` at G3) and show the progress, the changes and the
     questions in plain language (the question list with its recommended answers). Wait for
     their real reply in chat. Never answer, approve or give feedback for them. Resume
     the same agent with `SendMessage` to `spec-<job-id>`, passing their reply verbatim,
     and repeat. If the resume fails ("No transcript found", for example after the
     session restarted), spawn a fresh `spec-writer` with the same paths and tell it to
     continue from `spec/state.md`, `spec/spec-status.md` and `spec/feedback-log.md`, then
     pass the user's reply verbatim.
   - `STATUS: BLOCKED`: go to **Needs human** with the `## Blocked` text.
   - `STATUS: DONE`: check that `spec.md` exists, then **GATE G4**: show `spec.md` and ask
     "Approve starting the builder?" Do not start the builder before `APPROVED`.
   If `spec/spec-status.md` is missing after a spec-writer run (an old-style one-shot
   run), just check that `spec.md` exists.
4. **Build.** Set `stage: "build"`. Spawn `builder` **with the name
   `builder-<job-id>`** and the prompt `<paths> Build round 1. Port: <port>.`
   Wait for it to finish, then go to **Build check**.

### Build check

Read the first line of `build.md`.

- `STATUS: NEEDS_INPUT`: a builder sprint is finished (the plan, a development sprint, a test
  sprint, or the fixes for a review round). **GATE G4.S** (set `awaiting` to `G4.S <gate text>`):
  read `## Gate`, `## Progress`, `## Result`, `## Conflicts and questions`, `## Output` and
  `## Ask`. Open the files in `## Output` for the user (`SPRINTS.md`, the results workbook in
  `test-results/`), and show the sprint result, the failures with their reasons and the
  conflicts in plain language. Wait for the user's real reply in chat; never approve or decide
  a conflict for them. Resume the same agent with `SendMessage` to `builder-<job-id>`,
  passing the reply verbatim, then run Build check again. These sprint resumes do not count
  toward `MAX_RESUMES`. If the resume fails ("No transcript found"), spawn a fresh `builder`
  with the same paths, tell it to continue from `build.md` and `SPRINTS.md`, and pass the reply
  verbatim.
- `STATUS: READY`: every builder sprint is approved. **GATE G5**: show `build.md` and the branch,
  and ask "Approve starting the four reviewers?" Start review round N only after `APPROVED`. On
  feedback, resume the builder with it, then run Build check again.
- `STATUS: BLOCKED`: go to **Needs human**.

### Review round N

1. Set `stage: "review"`, `round: N` and all four reviews to `pending`. Create
   `factory/jobs/<job-id>/round-<N>/`.
2. Spawn all four reviewers **in one message**, so they run in parallel. Each
   gets the prompt `<paths> Review round N.`, plus its port for `reviewer-ux`
   and `reviewer-ui`.
3. **WAIT FOR ALL.** Each time a reviewer finishes, read the first line of its
   file (`VERDICT: PASS` or `VERDICT: CHANGES`) and write that verdict to
   `job.json` straight away, so the dashboard chips fill in as they land. The
   round is done only when all four `review-*.md` files exist in `round-<N>/`.
   Never resume the builder mid-round. If a reviewer finishes without writing
   its file, or writes a first line that isn't a verdict, stop and tell the user.
4. **GATE G6**: show the user all four verdicts and a short summary of each finding, with the
   paths of the review files, and ask "Approve moving on?" Feedback on a review: re-run that
   reviewer with the feedback (same round) and ask again. Decide only after `APPROVED`.
5. Decide:
   - **All PASS**: go to **Approve**.
   - **Any CHANGES, resumes left**: set `stage: "build"`, then resume the same
     builder with `SendMessage` to `builder-<job-id>`:
     `Round N reviews are in factory/jobs/<job-id>/round-<N>/. Address every review with VERDICT: CHANGES, commit, and update build.md for round N+1.`
     Wait for it to finish, then go to **Build check**.
   - **Any CHANGES, no resumes left**: write `decision.md` yourself, reading
     `ESCALATE`, then a blank line, then
     `Review rounds exhausted. Outstanding CHANGES in round-<N>/ from: <reviewers>.`
     Go to **Needs human**.

### Approve

Set `stage: "approve"`. Spawn `approver` with the prompt `<paths> Final round: N.`
(this happens only after G6 was approved). When it finishes, read the first line of `decision.md`
and **GATE G7**: show the decision and its reasons.

- `APPROVE`: ask "Approve the merge to main?" Go to **Merge** only after `APPROVED`.
- `ESCALATE`: go to **Needs human**.

### Merge

Merge only after G7 was approved. The merge happens in the main checkout, so it must be clean and on `main`:
`git status --porcelain -- . ':!factory/backlog.md'` prints nothing and
`git branch --show-current` prints `main`. `factory/backlog.md` is exempt: every
`/factory next` edits it, and job branches never touch it, so a dirty backlog
cannot conflict with the merge. If not, set `stage: "needs-human"` and tell the
user the job is approved but the main checkout is busy; they run
`/factory approve <job-id>` once it is clean. Otherwise:

```bash
git merge --no-ff factory/<job-id> -m "Merge factory/<job-id>"
git worktree remove <worktree>
git branch -d factory/<job-id>
```

Set `stage: "merged"`. If the merge fails, run `git merge --abort` (when a merge
is in progress), set `stage: "needs-human"` and tell the user why. If removing the
worktree fails, the job is still merged: tell the user what `git worktree remove`
printed. Never push.

### Needs human

Set `stage: "needs-human"`. The branch and its worktree stay for the human to
inspect. Tell the user which job is waiting, give the worktree path, and quote
`decision.md` (or the BLOCKED reason from `build.md`).

## /factory next

Read `factory/backlog.md` and take the first `- [ ]` item. Claim it with one
Edit that replaces its exact line with `- [x] <item> → claimed`. If the Edit
fails because the line changed, another session claimed it: re-read the backlog
and try the next `- [ ]` item. If none is left, say so and stop.

Run `/factory <item>`, and once step 1 has given it a job id, replace `claimed`
on its backlog line with the job id.

## /factory approve <job-id>

The job must be in `needs-human`. Run **Merge** with that job id.

## /factory rework <job-id> <note>

The job must be in `needs-human`.

1. Write the note, verbatim, to `factory/jobs/<job-id>/rework-<k>.md`, where `k`
   is the next unused number.
2. Set `stage: "build"`.
3. Spawn a fresh `builder` named `builder-<job-id>` with the prompt
   `<paths> Rework: read rework-<k>.md and address it, then update build.md for round N+1. Port: <port>.`
   (`N` is the job's last round.) A rework run gets a fresh `MAX_RESUMES`.
4. Continue from **Build check**, exactly like a new job.

## Reporting

Keep the user posted with one short line per transition, for example
`003-rate-limiting: round 2, security CHANGES, ux/ui/code PASS → resuming builder`.
When the job ends, say whether it merged or needs a human, and why.
