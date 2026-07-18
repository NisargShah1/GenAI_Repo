from google.adk.skills import Skill

api_skill = Skill(
    name="api-skill",
    description="Best practices and standards for RESTful API design.",
    instructions="""
Follow RESTful API design best practices.

- Use nouns for resource paths, not verbs (e.g. /api/users, not /api/getUsers).
- Use plural nouns for resource collections (e.g. /users, not /user).
- Use appropriate HTTP methods: GET (read), POST (create), PUT (replace), PATCH (update), DELETE (remove).
- Return correct HTTP status codes:
  - 200 OK for successful reads/updates
  - 201 Created for successful creation
  - 204 No Content for successful deletes
  - 400 Bad Request for validation errors
  - 401 Unauthorized for authentication failure
  - 403 Forbidden for authorization failure
  - 404 Not Found if resource doesn't exist
  - 500 Internal Server Error for unhandled exceptions.
- Always return errors in a standard error payload format (timestamp, status, error, path, message).
- Use camelCase for JSON keys in request/response payloads.
""",
    frontmatter={
        "name": "api-skill",
        "description": "Best practices and standards for RESTful API design."
    }
)
