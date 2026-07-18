from google.adk.skills import Skill

git_skill = Skill(
    name="git-skill",
    description="Guidelines for version control commits, branches, and diff workflows.",
    instructions="""
Follow Git best practices and Conventional Commits format.

- Use Conventional Commits format:
  - feat: for new features
  - fix: for bug fixes
  - docs: for documentation changes
  - style: formatting changes (spaces, semicolons, etc.)
  - refactor: code restructures with no behavior change
  - test: adding or fixing tests
  - chore: builds, dependencies, or tool updates
- Keep the first line of commit message under 50 characters, and capitalized.
- Write commits in the imperative mood (e.g., 'add UserService' instead of 'added UserService').
- Separate header, body, and footer with blank lines when writing detailed commit messages.
- Ensure only relevant, formatted files are committed.
""",
    frontmatter={
        "name": "git-skill",
        "description": "Guidelines for version control commits, branches, and diff workflows."
    }
)
