from google.adk.skills import Skill

spring_skill = Skill(
    name="spring-skill",
    description="Rules and design patterns for building Spring Boot Web applications.",
    instructions="""
Follow Spring Boot best practices and design patterns.

- Annotate configuration classes with @Configuration.
- Use @RestController for API controller endpoints.
- Use @Service for business logic classes.
- Use @Repository for database access classes.
- Use constructor-based dependency injection. Avoid @Autowired on fields directly.
- Use standard Spring Boot exception handler patterns (@RestControllerAdvice and @ExceptionHandler).
- Manage database transactions using @Transactional appropriately at service layer.
- Follow standard project layouts: controller, service, repository, model, dto, exception.
""",
    frontmatter={
        "name": "spring-skill",
        "description": "Rules and design patterns for building Spring Boot Web applications."
    }
)
