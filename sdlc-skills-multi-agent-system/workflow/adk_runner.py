"""
Centralized management for running ADK agents (ADK v2.5+).

In ADK v2.5, ``Runner.run()`` resolves the target session through its
``SessionService`` and raises ``SessionNotFoundError`` when the session was
never registered. The previous implementation invented a random ``session_id``
per call and never created the session, so every agent invocation crashed.

``ADKRunnerManager`` fixes this by owning a single ``SessionService`` and a
runner cache, and by maintaining exactly one ADK session per sprint. The ADK
session id is persisted on the sprint (via ``SessionManager``) so that the
in-memory session, the persisted sprint state, and the app-level memory stay in
sync across restarts.
"""
import logging
import uuid
from typing import Dict, Optional

from google.adk import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from session import active_session

logger = logging.getLogger("skillforge.workflow.adk_runner")

APP_NAME = "skillforge"


class ADKRunnerManager:
    """Owns the single ADK ``SessionService`` and coordinates agent execution."""

    def __init__(self):
        self._session_service = InMemorySessionService()
        # Cache of Runner instances keyed by the agent object's identity.
        self._runners: Dict[int, Runner] = {}
        # Cache of ADK session ids keyed by sprint id.
        self._sprint_sessions: Dict[int, str] = {}

    # ------------------------------------------------------------------ #
    # Session handling
    # ------------------------------------------------------------------ #
    def _create_session(self, user_id: str, session_id: str) -> str:
        self._session_service.create_session_sync(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
        return session_id

    def get_or_create_session(self, sprint_id: Optional[int], user_id: str) -> str:
        """Return a valid ADK session id, creating and persisting it if needed.

        - ``sprint_id is None`` yields a fresh transient session (no persistence).
        - Otherwise the sprint's session id is reused (from cache or the DB) and
          transparently recreated in the volatile session service after a
          restart.
        """
        if sprint_id is None:
            return self._create_session(user_id, str(uuid.uuid4()))

        session_manager = active_session.session_manager

        session_id = self._sprint_sessions.get(sprint_id)
        if session_id is None and session_manager is not None:
            session_id = session_manager.get_adk_session_id(sprint_id)

        if session_id is not None:
            existing = self._session_service.get_session_sync(
                app_name=APP_NAME, user_id=user_id, session_id=session_id
            )
            if existing is None:
                # Persisted id but the in-memory service lost it (e.g. restart).
                self._create_session(user_id, session_id)
            self._sprint_sessions[sprint_id] = session_id
            return session_id

        # Brand-new sprint session.
        session_id = self._create_session(user_id, str(uuid.uuid4()))
        self._sprint_sessions[sprint_id] = session_id
        if session_manager is not None:
            session_manager.set_adk_session_id(sprint_id, session_id)
        return session_id

    def clear_session(self, sprint_id: int, user_id: str = "default_user"):
        """Drop the ADK session bound to a sprint (used on reset)."""
        session_id = self._sprint_sessions.pop(sprint_id, None)
        session_manager = active_session.session_manager
        if session_id is None and session_manager is not None:
            session_id = session_manager.get_adk_session_id(sprint_id)
        if session_id is not None:
            try:
                self._session_service.delete_session_sync(
                    app_name=APP_NAME, user_id=user_id, session_id=session_id
                )
            except Exception as e:  # pragma: no cover - best-effort cleanup
                logger.debug(f"Could not delete ADK session {session_id}: {e}")
        if session_manager is not None:
            session_manager.set_adk_session_id(sprint_id, None)

    # ------------------------------------------------------------------ #
    # Runner handling
    # ------------------------------------------------------------------ #
    def _get_runner(self, agent: Agent) -> Runner:
        runner = self._runners.get(id(agent))
        if runner is None:
            runner = Runner(
                agent=agent,
                app_name=APP_NAME,
                session_service=self._session_service,
            )
            self._runners[id(agent)] = runner
        return runner

    def run(self, agent: Agent, prompt: str, sprint_id: Optional[int] = None,
            user_id: str = "default_user") -> str:
        """Run an ADK agent with a text prompt and return its final text output."""
        session_id = self.get_or_create_session(sprint_id, user_id)
        runner = self._get_runner(agent)

        user_message = types.Content(role="user", parts=[types.Part(text=prompt)])

        logger.debug(
            f"Running agent '{agent.name}' (sprint={sprint_id}, session={session_id}) "
            f"with prompt length={len(prompt)}"
        )

        final_text_parts = []
        for event in runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=user_message,
        ):
            text = self._extract_text(event)
            if text:
                final_text_parts.append(text)

        result_text = "\n".join(final_text_parts) if final_text_parts else ""

        if not result_text:
            logger.warning(f"Agent '{agent.name}' produced no text output.")

        return result_text

    @staticmethod
    def _extract_text(event) -> str:
        """Pull text out of an ADK event, preferring the model's content parts."""
        content = getattr(event, "content", None)
        if content is not None and getattr(content, "parts", None):
            parts = [p.text for p in content.parts if getattr(p, "text", None)]
            if parts:
                return "".join(parts)
        output = getattr(event, "output", None)
        if output is not None:
            return str(output)
        return ""


# Module-level singleton shared by the planner, executor, and coordinator.
_runner_manager: Optional[ADKRunnerManager] = None


def get_runner_manager() -> ADKRunnerManager:
    global _runner_manager
    if _runner_manager is None:
        _runner_manager = ADKRunnerManager()
    return _runner_manager


def run_agent(agent: Agent, prompt: str, sprint_id: Optional[int] = None,
              user_id: str = "default_user") -> str:
    """Backwards-compatible helper delegating to the shared ADKRunnerManager."""
    return get_runner_manager().run(
        agent, prompt, sprint_id=sprint_id, user_id=user_id
    )
