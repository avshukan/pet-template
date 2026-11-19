# Pet Template

Minimal Copier template for independent projects with shared agent instructions
and reusable skills.

```sh
copier copy --defaults --data 'project_name=Dental Memo' . /path/to/dental-memo
copier copy --defaults --data 'project_name=Chessboard Playback' . /path/to/chessboard-playback
```

Generated `AGENTS.md` holds the shared instructions, and `CLAUDE.md` references
it with `@AGENTS.md`. The canonical definitions for `triage` and `task-readiness`
live in each generated project's root `skills/` directory. Claude Code discovers
them through `.claude/skills -> ../skills`, and Codex uses
`.agents/skills -> ../skills`. Copier preserves both relative symlinks with
`_preserve_symlinks: true`.

Edit or add a shared skill under `skills/` in the generated project. Both clients
use those files, and each project's changes stay local to that project. Use a
filesystem and Git checkout that support symlinks.

Run the smoke tests with Python 3.12 and the CI-pinned Copier version:

```sh
python -m pip install 'copier==9.19.1'
python tests/template_smoke.py
```

The smoke tests generate both examples from the checked-out template, verify
that both discovery paths link to the same skill files, and check that the links
survive Git checkout. The A/B comparison still runs in disposable fixtures.
See [the symlink experiment](docs/agent-skills-experiment.md) for the results.
