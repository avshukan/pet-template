# Shared agent skills: provisional layout and symlink experiment

## Status

`AGENTS.md` is the canonical instruction file, with `CLAUDE.md` referencing it.
The two skill drafts have one source each under `template/skills/`. This proposes
a generated root `skills/` directory; its final location still needs owner
approval. Neither discovery links nor `_preserve_symlinks` have been added to
the actual template. Both are confined to disposable test fixtures.

## Models compared

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

The filesystem checks read both `SKILL.md` files through both client paths,
compare their contents and resolved paths with the canonical source, inspect Git
index modes and stored link targets, and clone both template fixtures and linked
generated projects. Both Dental Memo and Chessboard Playback are generated for
each Copier setting and link model. The baseline examples are also generated
without discovery links, and editing one project's skill leaves the other
project and template source unchanged.

## Evidence and limits

- Local macOS / Python 3.9.6 / Copier 9.10.3: all five smoke tests passed (ten
  generations). This is supplemental evidence: local Python cannot install the
  CI-pinned Copier 9.19.1. Both skill drafts also passed the skill format validator.
- `.github/workflows/template-test.yml` runs the same tests on `ubuntu-latest`
  with Python 3.12 and Copier 9.19.1. Check the implementation branch's Actions
  result for authoritative evidence for that environment. It retains only
  `contents: read` permission and disables persisted checkout credentials.
- Filesystem success does not establish client discovery. Installed versions are
  Claude Code 2.1.311 and Codex CLI 0.141.0. A Codex app-server discovery probe
  could not initialize under local sandbox restrictions; no `skills/list` result
  was obtained. Claude discovery was not exercised: the installed CLI help did
  not expose a discovery-only command, and no model calls were made. Actual
  discovery for either layout remains unverified in both clients.

To repeat the filesystem experiment, install the CI-pinned Copier version using
Python 3.12 and run `python tests/template_smoke.py`. Each variant is built,
committed, cloned and generated in temporary directories; tests leave the real
template's layout unchanged.

## Owner decisions and next step

1. Approve or revise the proposed root `skills/` location.
2. Choose A or B after checking actual client discovery. If a linked model is
   adopted, approve enabling Copier's `_preserve_symlinks: true` so generated
   discovery paths retain one shared source.

Recommendation: keep discovery wiring deferred while reviewing these drafts.
Provisionally prefer A for its fewer links and automatic inclusion of new shared
skills, provided both clients discover it. B is useful if client-specific skill
selection is needed. This recommendation is a proposal, not an accepted layout.

After approval, add the selected links and Copier setting in a focused follow-up,
run the smoke tests, and verify both skills appear in each client's skill list in
a generated project. Record the client versions and observed discovery results;
opening files through symlinks alone is insufficient evidence.
