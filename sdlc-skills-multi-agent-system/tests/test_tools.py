import pytest
import os
from tools.filesystem_tool import _safe_path, read_file
from tools.jira_tool import create_jira_ticket, update_jira_ticket_status, get_jira_ticket

def test_filesystem_sandbox_checks():
    # Relative path within workspace is fine
    p = _safe_path("src/Main.java")
    assert p.endswith(os.path.join("src", "Main.java"))
    
    # Path outside workspace should raise PermissionError
    with pytest.raises(PermissionError):
        _safe_path("../../../Windows/System32")
        
def test_read_non_existent_file():
    res = read_file("non_existent_file_xyz.txt")
    assert "Error" in res

def test_jira_mock_operations():
    res_create = create_jira_ticket("Implement OAuth2", "Add oauth verification provider", "Story")
    assert "Success" in res_create
    assert "SF-" in res_create
    
    # Extract ticket ID
    ticket_key = [t for t in res_create.split() if t.startswith("SF-")][0]
    
    res_get = get_jira_ticket(ticket_key)
    assert "OAuth2" in res_get
    assert "TO DO" in res_get
    
    res_update = update_jira_ticket_status(ticket_key, "IN PROGRESS")
    assert "Success" in res_update
    
    res_get2 = get_jira_ticket(ticket_key)
    assert "IN PROGRESS" in res_get2
