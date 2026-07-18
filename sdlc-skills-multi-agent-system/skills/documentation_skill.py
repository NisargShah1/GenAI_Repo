from google.adk.skills import Skill

documentation_skill = Skill(
    name="documentation-skill",
    description="Standards for code documentation, README formatting, and API reference guides.",
    instructions="""
Follow documentation best practices for code and projects.

- Document public APIs, controller routes, and services with clean comments / JavaDocs.
- JavaDocs should describe the purpose, @param variables, @return type, and @throws clauses.
- Maintain a clean, structured README.md with clear 'Getting Started', 'Prerequisites', 'API Documentation', and 'Running Tests' sections.
- Use Markdown formatting features (code blocks, tables, checklists, bold/italic text, alerts) to improve readability.
- Ensure documentation is accurate, matching the actual codebase implementation.
""",
    frontmatter={
        "name": "documentation-skill",
        "description": "Standards for code documentation, README formatting, and API reference guides."
    }
)
