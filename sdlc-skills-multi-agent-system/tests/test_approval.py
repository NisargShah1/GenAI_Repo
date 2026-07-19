import json
import os

import pytest

from session import active_session
from session.session_manager import SessionManager
from tools.approval import check_approval
from tools.filesystem_tool import write_file, _safe_path
from tools.dispatch import execute_approved_action


@pytest.fixture
def active_sprint():
    sm = SessionManager("sqlite:///:memory:")
    sprint_id = sm.create_sprint("Build API")
    active_session.session_manager = sm
    active_session.active_sprint_id = sprint_id
    yield sm, sprint_id
    active_session.session_manager = None
    active_session.active_sprint_id = None


def test_write_file_defers_until_approved_then_writes(active_sprint):
    sm, sprint_id = active_sprint
    rel_path = "tests/_tmp_approval_output.md"
    abs_path = _safe_path(rel_path)
    if os.path.exists(abs_path):
        os.remove(abs_path)

    try:
        # 1. First call creates a pending approval and does NOT touch disk.
        result = write_file(rel_path, "# Hello")
        assert "ACTION_REQUIRED" in result
        assert not os.path.exists(abs_path)
        assert len(sm.get_pending_approvals(sprint_id)) == 1

        # 2. Re-invoking with the same args must MATCH the existing request
        #    (regression: multi-key args used to mismatch and pile up duplicates).
        approved, _ = check_approval("write_file", {"path": rel_path, "content": "# Hello"})
        assert approved is False
        assert len(sm.get_pending_approvals(sprint_id)) == 1

        # 3. Approve, then execute the approved action -> file lands on disk.
        req = sm.get_pending_approvals(sprint_id)[0]
        sm.handle_approval(req.id, True)
        exec_result = execute_approved_action("write_file", json.loads(req.arguments))
        assert "Success" in exec_result
        assert os.path.exists(abs_path)
        with open(abs_path, encoding="utf-8") as f:
            assert f.read() == "# Hello"
    finally:
        if os.path.exists(abs_path):
            os.remove(abs_path)


def test_create_approval_request_uses_sorted_keys(active_sprint):
    sm, sprint_id = active_sprint
    sm.create_approval_request(sprint_id, "write_file", {"path": "a.md", "content": "x"})
    req = sm.get_pending_approvals(sprint_id)[0]
    assert req.arguments == json.dumps({"path": "a.md", "content": "x"}, sort_keys=True)
