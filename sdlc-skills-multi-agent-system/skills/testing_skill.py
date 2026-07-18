from google.adk.skills import Skill

testing_skill = Skill(
    name="testing-skill",
    description="Standards and patterns for JUnit, Mockito, and Spring Boot testing.",
    instructions="""
Follow JUnit 5 and Mockito testing best practices.

- Write clear unit tests targeting individual public methods.
- Use Mockito to isolate dependencies. Avoid instantiating actual dependencies in unit tests.
- Use JUnit 5 annotations (@Test, @BeforeEach, @AfterEach, @ExtendWith(MockitoExtension.class)).
- Follow the Arrange-Act-Assert pattern.
- Test names should be descriptive (e.g. shouldReturnUserWhenUserExists or userNotFound_ShouldThrowException).
- Assert using modern assertions (e.g. Assertions.assertEquals, assertThrows, or AssertJ's assertThat).
- Ensure coverage for edge cases, null inputs, and expected exceptions.
- For integration tests, use @SpringBootTest, @ActiveProfiles("test"), and MockMvc for Web layers.
""",
    frontmatter={
        "name": "testing-skill",
        "description": "Standards and patterns for JUnit, Mockito, and Spring Boot testing."
    }
)
