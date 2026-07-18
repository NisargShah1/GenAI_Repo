import pytest

from session import active_session
from session.session_manager import SessionManager
from workflow.adk_runner import ADKRunnerManager, APP_NAME


class _FakePart:
    def __init__(self, text):
        self.text = text


class _FakeContent:
    def __init__(self, text):
        self.parts = [_FakePart(text)]


class _FakeEvent:
    def __init__(self, text):
        self.content = _FakeContent(text)
        self.output = None


class _FakeRunner:
    """Runner double that asserts the session was registered before running."""

    def __init__(self, session_service, reply="hello"):
        self._session_service = session_service
        self._reply = reply

    def run(self, *, user_id, session_id, new_message):
        # Mirror ADK behavior: the session must already exist.
        session = self._session_service.get_session_sync(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )
        if session is None:
            raise AssertionError("Runner.run invoked with an unregistered session")
        yield _FakeEvent(self._reply)


class _FakeAgent:
    def __init__(self, name="Assistant"):
        self.name = name


@pytest.fixture
def session_manager():
    sm = SessionManager("sqlite:///:memory:")
    active_session.session_manager = sm
    yield sm
    active_session.session_manager = None
    active_session.active_sprint_id = None


def _patch_runner(manager, monkeypatch, reply="hello"):
    fake = _FakeRunner(manager._session_service, reply=reply)
    monkeypatch.setattr(manager, "_get_runner", lambda agent: fake)


def test_get_or_create_session_creates_and_persists(session_manager):
    manager = ADKRunnerManager()
    sprint_id = session_manager.create_sprint("Build API")

    session_id = manager.get_or_create_session(sprint_id, "default_user")

    # Session is registered in the ADK service...
    assert manager._session_service.get_session_sync(
        app_name=APP_NAME, user_id="default_user", session_id=session_id
    ) is not None
    # ...and persisted on the sprint.
    assert session_manager.get_adk_session_id(sprint_id) == session_id


def test_get_or_create_session_reuses_same_id(session_manager):
    manager = ADKRunnerManager()
    sprint_id = session_manager.create_sprint("Build API")

    first = manager.get_or_create_session(sprint_id, "default_user")
    second = manager.get_or_create_session(sprint_id, "default_user")

    assert first == second


def test_recreates_persisted_session_after_restart(session_manager):
    sprint_id = session_manager.create_sprint("Build API")
    # Simulate a prior run that persisted an id whose in-memory session is gone.
    session_manager.set_adk_session_id(sprint_id, "persisted-id-123")

    manager = ADKRunnerManager()  # fresh, volatile session service
    session_id = manager.get_or_create_session(sprint_id, "default_user")

    assert session_id == "persisted-id-123"
    assert manager._session_service.get_session_sync(
        app_name=APP_NAME, user_id="default_user", session_id=session_id
    ) is not None


def test_run_creates_session_and_returns_text(session_manager, monkeypatch):
    manager = ADKRunnerManager()
    sprint_id = session_manager.create_sprint("Build API")
    _patch_runner(manager, monkeypatch, reply="agent output")

    # Would raise SessionNotFoundError-equivalent if the session was not created.
    result = manager.run(_FakeAgent(), "hi", sprint_id=sprint_id)

    assert result == "agent output"


def test_run_without_sprint_uses_transient_session(monkeypatch):
    active_session.session_manager = None
    manager = ADKRunnerManager()
    _patch_runner(manager, monkeypatch, reply="transient")

    result = manager.run(_FakeAgent(), "hi", sprint_id=None)

    assert result == "transient"


def test_clear_session_removes_mapping(session_manager):
    manager = ADKRunnerManager()
    sprint_id = session_manager.create_sprint("Build API")
    session_id = manager.get_or_create_session(sprint_id, "default_user")

    manager.clear_session(sprint_id)

    assert session_manager.get_adk_session_id(sprint_id) is None
    assert manager._session_service.get_session_sync(
        app_name=APP_NAME, user_id="default_user", session_id=session_id
    ) is None
