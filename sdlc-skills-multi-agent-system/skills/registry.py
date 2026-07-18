from typing import Dict
from google.adk.skills import Skill
from skills.java_skill import java_skill
from skills.spring_skill import spring_skill
from skills.api_skill import api_skill
from skills.logging_skill import logging_skill
from skills.testing_skill import testing_skill
from skills.security_skill import security_skill
from skills.git_skill import git_skill
from skills.documentation_skill import documentation_skill
from skills.code_review_skill import code_review_skill
from skills.architecture_skill import architecture_skill

ALL_SKILLS: Dict[str, Skill] = {
    "java-skill": java_skill,
    "spring-skill": spring_skill,
    "api-skill": api_skill,
    "logging-skill": logging_skill,
    "testing-skill": testing_skill,
    "security-skill": security_skill,
    "git-skill": git_skill,
    "documentation-skill": documentation_skill,
    "review-skill": code_review_skill,
    "architecture-skill": architecture_skill
}

def get_skill(name: str) -> Skill:
    """Retrieve a skill by its name or key."""
    # Normalize name to kebab-case
    key = name.lower().strip().replace("_", "-")
    if not key.endswith("-skill"):
        key += "-skill"
    return ALL_SKILLS.get(key)
