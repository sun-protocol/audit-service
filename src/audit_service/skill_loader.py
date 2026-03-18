from dataclasses import dataclass, field
from pathlib import Path

import frontmatter

DEFAULT_REPORT_PATH = ".audit/Audit-Report.md"


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    prompt: str
    skill_dir: Path
    report_path: str = DEFAULT_REPORT_PATH
    references: dict[str, str] = field(default_factory=dict)  # filename -> content
    resources: dict[str, str] = field(default_factory=dict)  # filename -> content


def _read_md_files(directory: Path) -> dict[str, str]:
    """Read all markdown files from a directory recursively, keyed by relative path."""
    if not directory.is_dir():
        return {}
    result: dict[str, str] = {}
    for md_file in sorted(directory.rglob("*.md")):
        rel_path = str(md_file.relative_to(directory))
        result[rel_path] = md_file.read_text(encoding="utf-8")
    return result


def load_skill_from_dir(skill_path: Path) -> Skill:
    """Load a skill from a directory containing SKILL.md + references/ + resources/."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"SKILL.md not found in {skill_path}")

    post = frontmatter.load(str(skill_md))
    name = post.metadata.get("name", skill_path.name)
    description = post.metadata.get("description", "")
    report_path = post.metadata.get("report_path", DEFAULT_REPORT_PATH)

    references = _read_md_files(skill_path / "references")
    resources = _read_md_files(skill_path / "resources")

    return Skill(
        name=name,
        description=description,
        prompt=post.content,
        skill_dir=skill_path,
        report_path=report_path,
        references=references,
        resources=resources,
    )


def load_skill_from_file(file_path: Path) -> Skill:
    """Load a skill from a single .md file (legacy format)."""
    post = frontmatter.load(str(file_path))
    name = post.metadata.get("name", file_path.stem)
    description = post.metadata.get("description", "")
    return Skill(
        name=name, description=description, prompt=post.content, skill_dir=file_path.parent
    )


def load_skills(skills_dir: str) -> dict[str, Skill]:
    """Load all skills from the given directory.

    Supports two formats:
    1. Directory-based: skills/<skill-name>/SKILL.md (+ references/, resources/)
    2. File-based (legacy): skills/<skill-name>.md
    """
    skills_path = Path(skills_dir)
    if not skills_path.is_dir():
        return {}

    result: dict[str, Skill] = {}

    # Directory-based skills (subdirectories with SKILL.md)
    for entry in sorted(skills_path.iterdir()):
        if entry.is_dir() and (entry / "SKILL.md").exists():
            skill = load_skill_from_dir(entry)
            result[entry.name] = skill

    # File-based skills (legacy .md files at top level)
    for md_file in sorted(skills_path.glob("*.md")):
        skill = load_skill_from_file(md_file)
        key = md_file.stem
        if key not in result:  # directory-based takes precedence
            result[key] = skill

    return result


def build_system_prompt(skill: Skill) -> str:
    """Build the full system prompt from skill prompt + references + resources."""
    parts = [skill.prompt]

    if skill.references:
        parts.append("\n\n---\n\n# Reference Documents\n")
        for name, content in skill.references.items():
            parts.append(f"\n## {name}\n\n{content}")

    if skill.resources:
        parts.append("\n\n---\n\n# Resources\n")
        for name, content in skill.resources.items():
            parts.append(f"\n## {name}\n\n{content}")

    return "\n".join(parts)
