from google.adk.skills import Skill

code_review_skill = Skill(
    name="review-skill",
    description="Rules and checklists for evaluating code quality, security, and standard compliance.",
    instructions="""
Follow code review best practices and checklists.

- Readability: Check if variables, methods, and classes have clear names. Are methods small and cohesive?
- SOLID principles: Ensure single responsibility and check if interface implementation is correct.
- Security: Scan for SQL injections, hardcoded credentials, unchecked inputs, or information disclosures.
- Performance: Check for N+1 queries, unclosed resources, memory leaks, or inefficient collections usage.
- Logging: Are exceptions logged properly? Are sensitive details skipped in parameters?
- Error Handling: Is there a fallback for exceptions? Are custom exception types defined?
- Standards: Verify compliance with the target language style guide (e.g., Google Java style guide).
""",
    frontmatter={
        "name": "review-skill",
        "description": "Rules and checklists for evaluating code quality, security, and standard compliance."
    }
)
