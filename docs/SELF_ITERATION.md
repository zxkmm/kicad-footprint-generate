# Self-iteration

**This repo is meant to be edited by the agent that uses it.**

Every session that uses these skills is also a session that can improve them.
A skill that never changes rots: KiCad ships a new version, an API moves, a doc
line turns out to be wrong, a footprint family needs a rule nobody wrote down.
The only way this stays useful is that whoever notices, fixes it — and the one
who notices is usually the agent, mid-task, at the exact moment it hurt.

So: **notice → fix the repo → commit → push (or PR).** In the same session.
Not "I should mention this to the user"; write it into the repo.

## What counts as worth writing down

Anything that cost you time and would cost the next run the same time.

- A doc line that is **wrong** or now out of date — correct it, don't work around it.
- A command that failed in a way the docs did not predict — say what actually happens.
- A KiCad / kipy / pcbnew behaviour discovered by experiment — that is the most
  valuable content here, because it cannot be guessed from source.
- A bug in `kicad_harness/` — fix the code, not just the prose.
- A footprint family or datasheet quirk the generator got wrong the first time —
  add the rule to the footprint skill's docs, or a template.
- A missing capability you had to hand-roll — turn it into a `kh` subcommand or an
  entry in [`ISSUES.md`](../ISSUES.md) if it is too big for the session.

## Where it goes

| What you learned | Where it belongs |
|---|---|
| a decision that changes how the agent works | `SKILL.md` |
| measured KiCad behaviour, what the API can't do | `docs/CAPABILITIES.md` |
| the kipy object model | `docs/LIVE_API.md` |
| a worked example worth repeating | `docs/RECIPES.md` |
| editing a schematic a human drew | `docs/SCHEMATIC_EDITS.md` |
| a fix to the tool itself | `kicad_harness/` |
| footprint math, pad rules, package conventions | `docs/footprints/` |
| a reusable wizard blueprint | `templates/` |
| something broken you did **not** fix | `ISSUES.md`, with severity and what you'd do |

Keep `SKILL.md` thin. It is read on every invocation — it holds the decisions
("look every id up", "always render and look", "measure the drawing"), and the
details live in `docs/`.

## The loop, concretely

```bash
git -C <repo> status                 # 1. know what you already changed
#    ... do the KiCad work ...
#    ... something surprises you ...
#    2. edit the doc / the code, right then
git -C <repo> add -A
git -C <repo> commit -m "sview: sub-sheets render blank without --all"
git -C <repo> push                   # 3. or open a PR, see below
```

Rules for the commits:

- **One topic per commit.** A doc correction and an unrelated CLI fix are two commits.
- **The message states the finding**, not the file. `"live save drops locked
  graphics"` beats `"update SKILL.md"`.
- Never commit board files, renders, netlists, or anything from the user's own
  project — only the repo's own files. `.gitignore` covers the usual output
  (`*.png`, `*.svg`, `*.net`, `*.csv`); check `git status` before `add -A` anyway.
- If the repo has unrelated dirty state, commit only your paths.
- Don't rewrite history and don't force-push.

## Who pushes where

**Repo owner** — the skill directory is a symlink to the checkout, so edits are
already in the repo. Commit and push to `main` as part of finishing the task. No
need to ask first; that is the standing instruction. Say in your final message
what you committed.

**Everyone else** — fork freely, that is what forks are for. But **please send it
back**: open a PR against
[`zxkmm/kicad-harness`](https://github.com/zxkmm/kicad-harness). A fix that stays
in your fork helps one person; the same fix upstream helps every agent that
installs this. If you are unsure whether a finding generalises, open the PR anyway
and say so in the description — a wrong-but-documented observation is easier to
correct than an absence.

Agents working in someone else's fork: check `git remote -v` first. If you cannot
push, commit on a branch and tell the user the PR is ready to open, or open it with
`gh pr create` if that is available.

## Don't

- Don't invent findings to have something to commit. A session that learned
  nothing new commits nothing.
- Don't paste session transcripts into the docs. Write the rule, not the story.
- Don't delete an existing caveat because it did not bite you this time — the
  caveats here were paid for. Correct them with evidence, or leave them.
