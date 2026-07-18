from typing import List
from google.adk.skills import Skill
from skills.registry import ALL_SKILLS

def detect_skills(text: str) -> List[Skill]:
    """Dynamically load skills based on keywords in the requirement or task description."""
    detected = []
    text_lower = text.lower()
    
    # Keyword mappings to skills
    mapping = {
        "java-skill": ["java", "jdk", "jvm", "maven", "gradle", "pojo"],
        "spring-skill": ["spring", "boot", "controller", "service", "jpa", "beans", "autowired", "restcontroller"],
        "api-skill": ["api", "rest", "endpoint", "http", "json", "dto", "request", "response", "controller"],
        "logging-skill": ["log", "logging", "slf4j", "logback", "trace", "warn", "error", "debug"],
        "testing-skill": ["test", "testing", "junit", "mockito", "assert", "mock", "coverage"],
        "security-skill": ["security", "auth", "login", "encrypt", "owasp", "cors", "csrf", "bcrypt", "password"],
        "git-skill": ["git", "commit", "branch", "push", "pull request", "pr", "merge", "repo"],
        "documentation-skill": ["doc", "docs", "documentation", "readme", "javadoc", "markdown", "comment"],
        "review-skill": ["review", "code smell", "standards", "compliance", "audit", "feedback"],
        "architecture-skill": ["architecture", "design", "mermaid", "diagram", "sequence", "table", "schema", "class"]
    }
    
    for skill_key, keywords in mapping.items():
        if any(kw in text_lower for kw in keywords):
            skill = ALL_SKILLS.get(skill_key)
            if skill and skill not in detected:
                detected.append(skill)
                
    # Default to Java if nothing detected
    if not detected:
        detected.append(ALL_SKILLS["java-skill"])
        
    return detected
