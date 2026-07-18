import os
from typing import Optional
from tools.approval import check_approval

WORKSPACE_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def _safe_path(path: str) -> str:
    """Resolve absolute path and verify it is within the workspace root."""
    abs_path = os.path.abspath(os.path.join(WORKSPACE_ROOT, path))
    if not abs_path.startswith(WORKSPACE_ROOT):
        raise PermissionError(f"Access denied: path '{path}' is outside workspace root.")
    return abs_path

def read_file(path: str) -> str:
    """
    Read the contents of a file.
    Args:
        path: Path to the file relative to the workspace.
    """
    try:
        abs_path = _safe_path(path)
        if not os.path.exists(abs_path):
            return f"Error: File not found at '{path}'"
        with open(abs_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(path: str, content: str) -> str:
    """
    Create or overwrite a file with the given content. Requires user approval.
    Args:
        path: Path to the file relative to the workspace.
        content: The text content to write.
    """
    try:
        abs_path = _safe_path(path)
        # Check human approval
        args = {"path": path, "content": content}
        approved, status_msg = check_approval("write_file", args)
        if not approved:
            return status_msg

        # Perform action
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        # Update session manager file record if possible
        from session import active_session
        if active_session.session_manager and active_session.active_sprint_id:
            active_session.session_manager.save_or_update_file(
                active_session.active_sprint_id, path, content
            )
            
        return f"Success: Wrote to file '{path}' successfully."
    except Exception as e:
        return f"Error writing file: {str(e)}"

def delete_file(path: str) -> str:
    """
    Delete a file. Requires user approval.
    Args:
        path: Path to the file relative to the workspace.
    """
    try:
        abs_path = _safe_path(path)
        if not os.path.exists(abs_path):
            return f"Error: File not found at '{path}'"
            
        # Check human approval
        args = {"path": path}
        approved, status_msg = check_approval("delete_file", args)
        if not approved:
            return status_msg

        os.remove(abs_path)
        return f"Success: Deleted file '{path}' successfully."
    except Exception as e:
        return f"Error deleting file: {str(e)}"
