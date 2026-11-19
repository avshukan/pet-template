"""Generate both examples and compare proposed symlinks in disposable Git repos."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("triage", "task-readiness")
PROJECTS = ("Dental Memo", "Chessboard Playback")


def run(*args, cwd=None):
    result = subprocess.run(
        args, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if result.returncode:
        raise AssertionError(
            f"Command failed: {args}\n{result.stdout}\n{result.stderr}"
        )
    return result.stdout.strip()


def commit_all(repository):
    run("git", "add", ".", cwd=repository)
    run(
        "git", "-c", "user.name=Template test", "-c",
        "user.email=template-test@example.invalid", "-c", "commit.gpgsign=false",
        "commit", "-qm", "Test fixture", cwd=repository,
    )


class TemplateSmokeTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="pet-template-")
        self.addCleanup(self.temporary.cleanup)
        self.scratch = Path(self.temporary.name)

    def source(self, model=None, preserve=False):
        source = self.scratch / "source"
        source.mkdir()
        shutil.copy2(ROOT / "copier.yml", source / "copier.yml")
        shutil.copytree(ROOT / "template", source / "template", symlinks=True)
        if preserve:
            with (source / "copier.yml").open("a") as config:
                config.write("\n_preserve_symlinks: true\n")
        if model:
            for client in (".claude", ".agents"):
                skills = source / "template" / client / "skills"
                skills.parent.mkdir()
                if model == "whole-directory":
                    skills.symlink_to("../skills", target_is_directory=True)
                else:
                    skills.mkdir()
                    for name in SKILLS:
                        (skills / name).symlink_to(
                            f"../../skills/{name}", target_is_directory=True
                        )
        run("git", "init", "-q", str(source))
        commit_all(source)
        return source

    def generate(self, source, name):
        destination = self.scratch / name.lower().replace(" ", "-")
        run(
            sys.executable, "-m", "copier", "copy", "--defaults",
            "--vcs-ref=HEAD", "--data", f"project_name={name}",
            str(source), str(destination),
        )
        self.assertIn(f"Project: {name}\n", (destination / "AGENTS.md").read_text())
        self.assertEqual((destination / "CLAUDE.md").read_text(), "@AGENTS.md\n")
        answers = yaml.safe_load((destination / ".copier-answers.yml").read_text())
        self.assertEqual(answers["project_name"], name)
        self.assertEqual(answers["_src_path"], str(source))
        self.assertEqual(
            run("git", "rev-parse", answers["_commit"], cwd=source),
            run("git", "rev-parse", "HEAD", cwd=source),
        )
        for skill in SKILLS:
            path = destination / "skills" / skill / "SKILL.md"
            _, frontmatter, body = path.read_text().split("---", 2)
            metadata = yaml.safe_load(frontmatter)
            self.assertEqual(metadata["name"], skill)
            self.assertTrue(metadata["description"])
            self.assertTrue(body.strip())
        return destination

    def check_links(self, root, model, preserved):
        for client in (".claude", ".agents"):
            base = root / client / "skills"
            if model == "whole-directory":
                self.assertEqual(base.is_symlink(), preserved)
                if preserved:
                    self.assertEqual(base.readlink(), Path("../skills"))
            for name in SKILLS:
                folder = base / name
                if model == "individual-directory":
                    self.assertEqual(folder.is_symlink(), preserved)
                    if preserved:
                        self.assertEqual(folder.readlink(), Path(f"../../skills/{name}"))
                canonical = root / "skills" / name / "SKILL.md"
                discovered = folder / "SKILL.md"
                self.assertEqual(discovered.read_text(), canonical.read_text())
                self.assertEqual(discovered.resolve() == canonical.resolve(), preserved)

    def git_roundtrip(self, root, model, clone, subdirectory=Path(".")):
        if not (root / ".git").exists():
            run("git", "init", "-q", str(root))
            commit_all(root)
        for client in (".claude", ".agents"):
            base = subdirectory / client / "skills"
            paths = (
                [str(base)] if model == "whole-directory"
                else [str(base / name) for name in SKILLS]
            )
            for path in paths:
                entry = run("git", "ls-files", "--stage", "--", path, cwd=root)
                self.assertTrue(entry.startswith("120000 "), entry)
                self.assertEqual(
                    run("git", "show", f"HEAD:{path}", cwd=root),
                    str((root / path).readlink()),
                )
        run("git", "clone", "-q", "--no-hardlinks", str(root), str(clone))
        self.check_links(clone / subdirectory, model, preserved=True)

    def test_generated_projects(self):
        source = self.source()
        outputs = []
        for name in PROJECTS:
            with self.subTest(project=name):
                destination = self.generate(source, name)
                outputs.append(destination)
                # Discovery layout remains an owner decision, absent in the template.
                self.assertFalse((destination / ".claude").exists())
                self.assertFalse((destination / ".agents").exists())
        first = outputs[0] / "skills" / "triage" / "SKILL.md"
        second = outputs[1] / "skills" / "triage" / "SKILL.md"
        original = second.read_text()
        first.write_text("Independent project edit\n")
        self.assertEqual(second.read_text(), original)
        self.assertEqual((source / "template/skills/triage/SKILL.md").read_text(), original)

    def experiment(self, model, preserve):
        source = self.source(model, preserve)
        checkout = self.scratch / "checkout"
        self.git_roundtrip(source, model, checkout, Path("template"))
        for name in PROJECTS:
            with self.subTest(project=name):
                output = self.generate(checkout, name)
                self.check_links(output, model, preserved=preserve)
                if preserve:
                    self.git_roundtrip(
                        output, model, self.scratch / f"{output.name}-checkout"
                    )
                print(f"PASS: {model}, preserve={preserve}, {name}")

    def test_whole_directory_default(self):
        self.experiment("whole-directory", preserve=False)

    def test_individual_directory_default(self):
        self.experiment("individual-directory", preserve=False)

    def test_whole_directory_preserved(self):
        self.experiment("whole-directory", preserve=True)

    def test_individual_directory_preserved(self):
        self.experiment("individual-directory", preserve=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
