from google.adk.skills import Skill

logging_skill = Skill(
    name="logging-skill",
    description="SLF4J and Logback guidelines for structured, meaningful logs.",
    instructions="""
Follow SLF4J and Logback logging best practices.

- Use SLF4J Logger interface (typically via Lombok's @Slf4j or static instantiation).
- Choose the correct log levels:
  - ERROR: Actionable faults affecting system features (includes full exception stack traces).
  - WARN: Unexpected situations that do not halt operation (e.g. fallback activated).
  - INFO: High-level business milestones (e.g. user created, order shipped).
  - DEBUG: Detailed execution paths, parameters, payload inspections.
- Do NOT log sensitive information (passwords, credit cards, SSNs, personal identity details).
- Use parameterized logging (e.g. logger.info("User {} logged in from {}", username, ip)) instead of string concatenation.
- Make sure logs are structured and searchable.
""",
    frontmatter={
        "name": "logging-skill",
        "description": "SLF4J and Logback guidelines for structured, meaningful logs."
    }
)
