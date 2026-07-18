"""
Helper module to run ADK agents using the Runner API (ADK v2.5+).

In ADK v2.5, Agent.run() is a low-level async generator that requires
a Context and node_input. The correct high-level API is Runner.run(),
which manages sessions, message formatting, and event collection.
"""
import logging
import uuid
from typing import Optional

from google.adk import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

logger = logging.getLogger("skillforge.workflow.adk_runner")

# Shared session service for all runner invocations
_session_service = InMemorySessionService()

APP_NAME = "skillforge"


def run_agent(agent: Agent, prompt: str, user_id: str = "default_user",
              session_id: Optional[str] = None) -> str:
    """
    Run an ADK agent with a text prompt and return the final text output.

    Args:
        agent: The ADK Agent instance to run.
        prompt: The user prompt / input text.
        user_id: User identifier for the session.
        session_id: Optional session ID. A new one is generated if not provided.

    Returns:
        The concatenated text output from the agent's response events.
    """
    if session_id is None:
        session_id = str(uuid.uuid4())

    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=_session_service,
    )

    # Construct the Content message
    user_message = types.Content(
        role="user",
        parts=[types.Part(text=prompt)]
    )

    logger.debug(f"Running agent '{agent.name}' with prompt length={len(prompt)}")

    # Runner.run() is a synchronous generator that yields Events
    final_text_parts = []
    for event in runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=user_message,
    ):
        # Collect text from events that have output
        if event.output is not None:
            final_text_parts.append(str(event.output))
        elif hasattr(event, "content") and event.content:
            # Some events carry content with parts
            if hasattr(event.content, "parts") and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        final_text_parts.append(part.text)

    result_text = "\n".join(final_text_parts) if final_text_parts else ""

    if not result_text:
        logger.warning(f"Agent '{agent.name}' produced no text output.")

    return result_text
