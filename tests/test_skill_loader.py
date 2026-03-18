from pathlib import Path

from src.audit_service.skill_loader import (
    Skill,
    build_system_prompt,
    load_skill_from_dir,
    load_skill_from_file,
    load_skills,
)


def test_load_skill_from_file(tmp_path: Path):
    md = tmp_path / "test-skill.md"
    md.write_text(
        "---\nname: test-skill\ndescription: A test skill\n---\n\nYou are a tester.",
        encoding="utf-8",
    )
    skill = load_skill_from_file(md)
    assert skill.name == "test-skill"
    assert skill.description == "A test skill"
    assert "You are a tester." in skill.prompt


def test_load_skill_from_file_uses_filename_as_fallback_name(tmp_path: Path):
    md = tmp_path / "my-skill.md"
    md.write_text("---\ndescription: desc\n---\n\nContent here.", encoding="utf-8")
    skill = load_skill_from_file(md)
    assert skill.name == "my-skill"


def test_load_skill_from_dir(tmp_path: Path):
    skill_dir = tmp_path / "my-audit"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: My Audit\ndescription: Full audit\n---\n\nAudit all the things.",
        encoding="utf-8",
    )
    refs = skill_dir / "references"
    refs.mkdir()
    (refs / "CHECKLIST.md").write_text("# Checklist\n- Item 1", encoding="utf-8")

    res = skill_dir / "resources"
    res.mkdir()
    (res / "template.md").write_text("# Template\n## Findings", encoding="utf-8")

    skill = load_skill_from_dir(skill_dir)
    assert skill.name == "My Audit"
    assert skill.description == "Full audit"
    assert "Audit all the things." in skill.prompt
    assert "CHECKLIST.md" in skill.references
    assert "template.md" in skill.resources
    assert skill.skill_dir == skill_dir


def test_load_skill_from_dir_nested_references(tmp_path: Path):
    skill_dir = tmp_path / "deep-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("---\nname: deep\n---\n\nPrompt.", encoding="utf-8")

    nested = skill_dir / "references" / "sub"
    nested.mkdir(parents=True)
    (nested / "DEEP.md").write_text("Deep reference", encoding="utf-8")

    skill = load_skill_from_dir(skill_dir)
    assert "sub/DEEP.md" in skill.references


def test_load_skills_directory_format(tmp_path: Path):
    # Directory-based skill
    s1 = tmp_path / "alpha"
    s1.mkdir()
    (s1 / "SKILL.md").write_text("---\nname: Alpha\n---\n\nAlpha.", encoding="utf-8")

    # Legacy file-based skill
    (tmp_path / "beta.md").write_text("---\nname: Beta\n---\n\nBeta.", encoding="utf-8")

    skills = load_skills(str(tmp_path))
    assert "alpha" in skills
    assert "beta" in skills
    assert skills["alpha"].name == "Alpha"


def test_load_skills_directory_takes_precedence(tmp_path: Path):
    # Both dir and file with same name — dir wins
    s1 = tmp_path / "audit"
    s1.mkdir()
    (s1 / "SKILL.md").write_text("---\nname: Dir Audit\n---\n\nDir.", encoding="utf-8")
    (tmp_path / "audit.md").write_text("---\nname: File Audit\n---\n\nFile.", encoding="utf-8")

    skills = load_skills(str(tmp_path))
    assert skills["audit"].name == "Dir Audit"


def test_load_skills_empty_dir(tmp_path: Path):
    skills = load_skills(str(tmp_path))
    assert skills == {}


def test_load_skills_nonexistent_dir():
    skills = load_skills("/nonexistent/path")
    assert skills == {}


def test_build_system_prompt_basic():
    skill = Skill(
        name="test", description="", prompt="You are an auditor.", skill_dir=Path("/tmp")
    )
    result = build_system_prompt(skill)
    assert result == "You are an auditor."


def test_build_system_prompt_with_references_and_resources():
    skill = Skill(
        name="test",
        description="",
        prompt="Main prompt.",
        skill_dir=Path("/tmp"),
        references={"CHECKLIST.md": "# Checklist\n- A"},
        resources={"template.md": "# Template"},
    )
    result = build_system_prompt(skill)
    assert "Main prompt." in result
    assert "# Reference Documents" in result
    assert "CHECKLIST.md" in result
    assert "# Checklist" in result
    assert "# Resources" in result
    assert "template.md" in result
