import pytest
from skills.registry import ALL_SKILLS, get_skill
from skills.loader import detect_skills

def test_skills_registered():
    assert "java-skill" in ALL_SKILLS
    assert "spring-skill" in ALL_SKILLS
    assert "api-skill" in ALL_SKILLS
    assert "logging-skill" in ALL_SKILLS
    assert "testing-skill" in ALL_SKILLS

def test_get_skill():
    java = get_skill("java")
    assert java is not None
    assert java.name == "java-skill"
    
    invalid = get_skill("invalid_random_skill")
    assert invalid is None

def test_detect_skills_matching():
    skills_detected = detect_skills("I want to build a Java REST controller with logging.")
    skill_names = [s.name for s in skills_detected]
    
    assert "java-skill" in skill_names
    assert "spring-skill" in skill_names
    assert "api-skill" in skill_names
    assert "logging-skill" in skill_names

def test_skill_instructions():
    java_skill = get_skill("java")
    assert java_skill is not None
    assert java_skill.instructions is not None
    assert len(java_skill.instructions) > 0
    assert "Java" in java_skill.instructions
