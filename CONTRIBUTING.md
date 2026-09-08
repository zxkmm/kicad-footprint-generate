# Contributing

The whole design of this repo assumes it keeps changing. See
[`docs/SELF_ITERATION.md`](docs/SELF_ITERATION.md) for the protocol the agent
follows; this file is the human-facing summary.

## Fork, but send it back

Forking is fine and expected — pin a version, add house rules, whatever you need.
**Please open a PR here anyway** for anything that is not specific to you:

- a doc line that was wrong
- KiCad / kipy behaviour you measured (version numbers, please)
- a fix in `kicad_harness/`
- a footprint rule or template for a package family that was missing
- a prompt-level lesson: what made the agent get it right, or reliably wrong

PRs go to [`zxkmm/kicad-harness`](https://github.com/zxkmm/kicad-harness).
An observation you are not fully sure about is still worth a PR — say so in the
description. Half of the value in `docs/CAPABILITIES.md` is
"we tried it, it does not work", which nobody can find by reading source.

## What a good PR looks like

- One topic. Doc correction and a CLI change are two PRs.
- Says **what you observed**, on which KiCad version, with the command you ran.
- Puts the finding in the right file — the table in
  [`docs/SELF_ITERATION.md`](docs/SELF_ITERATION.md) says which.
- Keeps the SKILL.md files thin. They are read on every invocation; decisions go
  there, detail goes in `docs/`.
- No board files, renders, netlists or generated output.

## Not sure it is a fix?

Open an issue, or add an entry to [`ISSUES.md`](ISSUES.md) in a PR: severity,
what you hit, and what you would do about it. That file is the running log of
things found while actually using this, and a well-written open entry is worth
more than a guess at a patch.
