from google.adk.skills import Skill

security_skill = Skill(
    name="security-skill",
    description="Secure coding guidelines, OWASP standards, and encryption principles.",
    instructions="""
Follow secure coding guidelines and OWASP standards.

- Input Validation: Always validate all incoming inputs using @Valid and annotations like @NotNull, @Size, @Pattern.
- SQL Injection: Use Spring Data JPA or parameterized JDBC queries. NEVER concatenate user inputs into SQL strings.
- Sensitive Data: Hash passwords using bcrypt/argon2. NEVER store passwords in plain text.
- Authentication & Authorization: Use standard Spring Security config, configure CORS, and restrict routes with roles/authorities.
- XSS/CSRF: Secure response headers, sanitize output, and configure CSRF protection appropriately.
- Error Handling: Avoid returning raw stack traces in HTTP responses (prevents information disclosure).
- Secrets Management: Never commit raw credentials, tokens, or private keys to source control. Load them from env vars or vaults.
""",
    frontmatter={
        "name": "security-skill",
        "description": "Secure coding guidelines, OWASP standards, and encryption principles."
    }
)
