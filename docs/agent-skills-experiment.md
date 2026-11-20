# Shared agent skills and the symlink experiment

## Accepted layout

The owner selected Variant A for PR #3. Copier generates a canonical `skills/`
directory at the project root, with `.claude/skills` and `.agents/skills` both
pointing to `../skills`. The template enables `_preserve_symlinks: true` so the
two clients share the same definitions. Each generated project owns its copy of
the canonical files and can customize them independently.

## Historical comparison

| Property | A: whole directory | B: individual skill directories |
| --- | --- | --- |
| Claude links | `.claude/skills -> ../skills` | `.claude/skills/<name> -> ../../skills/<name>` |
| Codex links | `.agents/skills -> ../skills` | `.agents/skills/<name> -> ../../skills/<name>` |
| Links for two skills and two clients | 2 | 4 |
| Adding another shared skill | Both paths expose it through existing links | Add a link for each client |
| Client-specific selection | Both paths expose the entire directory | Each client can expose a subset |
| Git storage and local clone checkout | Mode `120000`; relative target preserved | Mode `120000`; relative target preserved |
| Copier default (`_preserve_symlinks: false`) | Readable copies, no shared source at discovery paths | Readable copies, no shared source at discovery paths |
| Copier with `_preserve_symlinks: true` | Relative links and shared source preserved | Relative links and shared source preserved |

The comparison runs in disposable Git repositories. It generates Dental Memo
and Chessboard Playback for each layout with Copier defaults and with symlink
preservation enabled. It reads both skills through both client paths, checks
whether those paths refer to the canonical files, and verifies the Git modes and
targets after a clone for preserved links.

## Discovery evidence

The discovery experiments used isolated repositories containing `triage` and
`task-readiness`. The owner confirmed both layouts in Claude Code and Codex,
including their VSCode interfaces. The recorded versions were Claude Code
`2.1.327` and Codex extension `26.1111.21308` on VSCode `1.144.0` (macOS arm64).
An independent probe of the extension's bundled Codex backend
`0.169.0-alpha.11.1` returned both skills as enabled repository skills through
`skills/list` for both variants. Neither skill appeared in the control, which
contained the same canonical files without discovery links. The discovery
checks did not require running either skill procedure.

## Regression checks

Run `python tests/template_smoke.py` with Python 3.12 and Copier 9.19.1, the
versions used by the Ubuntu GitHub Actions workflow. The baseline test renders
both projects from the checked-out template and verifies the actual links, both
skills, and the links after Git checkout. It also checks that editing one
project's canonical skill is visible through both of its client paths and leaves
the other project and template source intact. The four A/B tests reproduce the
historical filesystem comparison. CI covers generation and Git checkout.
Client discovery was checked separately in the experiments above.
