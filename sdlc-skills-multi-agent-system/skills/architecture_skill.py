from google.adk.skills import Skill

architecture_skill = Skill(
    name="architecture-skill",
    description="System architecture patterns, database design, and sequence diagram guidelines.",
    instructions="""
Follow system architecture and design best practices.

- Multi-tier Design: Structure systems with clear presentation, business logic, and data access layers.
- Database Normalization: Design tables with primary keys, foreign keys, constraints, and index guidelines. Follow 3NF unless denormalization is justified.
- Diagramming: Generate clear Mermaid diagrams (e.g. sequenceDiagram, classDiagram, erDiagram) to visualize flows.
- Coupling & Cohesion: Aim for high cohesion within components and loose coupling between them.
- Design Patterns: Use standard enterprise integration patterns (DTO, Repository, Service Locator, Factory, Builder, Observer).
- Scalability: Account for statelessness, session caching, and concurrency issues.
""",
    frontmatter={
        "name": "architecture-skill",
        "description": "System architecture patterns, database design, and sequence diagram guidelines."
    }
)
