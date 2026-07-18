import pytest
from session.session_manager import SessionManager
from session.state import SprintSessionState

def test_session_manager_crud():
    sm = SessionManager("sqlite:///:memory:")
    
    # 1. Create Sprint
    sprint_id = sm.create_sprint("Build user dashboard")
    
    # 2. Add tasks
    task_id1 = sm.add_task(sprint_id, "Design API", "design_agent", "Design specs", ["api-skill"], 0)
    task_id2 = sm.add_task(sprint_id, "Code Controller", "coding_agent", "Write Java controller", ["java-skill", "spring-skill"], 1)
    
    # 3. Load sprint state
    state = sm.load_sprint_state(sprint_id)
    assert isinstance(state, SprintSessionState)
    assert state.sprint_id == sprint_id
    assert len(state.tasks) == 2
    assert state.tasks[0].title == "Design API"
    assert "api-skill" in state.tasks[0].skills_needed
    
    # 4. Update task status
    sm.update_task_status(task_id1, "COMPLETED", "Mermaid specs output")
    state = sm.load_sprint_state(sprint_id)
    assert state.tasks[0].status == "COMPLETED"
    assert state.tasks[0].output == "Mermaid specs output"
    # Verify that api-skill is loaded in runtime now
    assert "api-skill" in state.loaded_skills
    
    # 5. File records
    sm.save_or_update_file(sprint_id, "src/UserController.java", "public class UserController {}")
    content = sm.get_file_content(sprint_id, "src/UserController.java")
    assert content == "public class UserController {}"
    
    # 6. Approvals
    req_id = sm.create_approval_request(sprint_id, "write_file", {"path": "test.txt", "content": "hello"})
    pending = sm.get_pending_approvals(sprint_id)
    assert len(pending) == 1
    assert pending[0].tool_name == "write_file"
    
    # Handle approval
    sm.handle_approval(req_id, True)
    pending = sm.get_pending_approvals(sprint_id)
    assert len(pending) == 0
