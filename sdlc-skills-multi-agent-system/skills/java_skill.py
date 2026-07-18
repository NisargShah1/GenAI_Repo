from google.adk.skills import Skill

java_skill = Skill(
    name="java-skill",
    description="Rules and patterns for building robust Java applications.",
    instructions="""
Follow Java 21 best practices and enterprise standards.

- Use strict Java types and interface-based design.
- Classes should follow camelCase naming conventions and start with uppercase (e.g. UserService).
- Methods and fields must be camelCase starting with lowercase.
- Prefer using standard collections (List, Map, Set) and generic types.
- Use standard Java exception handling. Avoid swallowing exceptions; always log or rethrow them.
- Keep classes cohesive and follow SOLID principles (Single Responsibility, Open-Closed, etc.).
- Ensure proper imports and avoid wildcard (*) imports.
- Prefer final fields and dependency injection (via constructor).
- Use records where appropriate.
- Prefer Optional over null.
""",
    frontmatter={
        "name": "java-skill",
        "description": "Rules and patterns for building robust Java applications."
    }
)
