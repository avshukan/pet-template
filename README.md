# Pet Template

Minimal Copier template for independent projects. It supplies shared agent
instructions and reusable skill drafts without selecting an application stack.

```sh
copier copy --defaults --data 'project_name=Dental Memo' . /path/to/dental-memo
copier copy --defaults --data 'project_name=Chessboard Playback' . /path/to/chessboard-playback
```

Generated `AGENTS.md` is canonical; `CLAUDE.md` contains only `@AGENTS.md`.
`skills/triage/SKILL.md` and `skills/task-readiness/SKILL.md` are proposed shared
skill sources. The root `skills/` layout is provisional, pending owner approval.
No `.claude/skills` or `.agents/skills` discovery links are generated yet. Agents
can read a skill by its explicit file path; automatic client discovery is not
claimed. See [the symlink experiment](docs/agent-skills-experiment.md) for results
and the decisions needed before wiring discovery.

Run the smoke tests with Python 3.12 and the CI-pinned Copier version:

```sh
python -m pip install 'copier==9.19.1'
python tests/template_smoke.py
```

Tests generate both examples in temporary Git repositories, validate their
instructions, skill metadata and Copier answers, and compare both proposed link
models. The experiments do not change the template's discovery configuration.
