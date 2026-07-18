import json
import logging
from typing import Tuple
from session import active_session
from session.models import ApprovalRequest

logger = logging.getLogger("skillforge.tools.approval")

def check_approval(tool_name: str, arguments: dict) -> Tuple[bool, str]:
    """
    Checks if a tool execution is approved by the user.
    Returns:
        (is_approved, status_message)
    """
    sprint_id = active_session.active_sprint_id
    sm = active_session.session_manager
    
    if sprint_id is None or sm is None:
        # If no database or session context exists (e.g., CLI testing), allow by default
        return True, "APPROVED"

    db = sm.get_db()
    # Normalize arguments to ensure stable JSON matching
    arg_str = json.dumps(arguments, sort_keys=True)
    
    # Query for an existing request
    req = db.query(ApprovalRequest).filter(
        ApprovalRequest.sprint_id == sprint_id,
        ApprovalRequest.tool_name == tool_name,
        ApprovalRequest.arguments == arg_str
    ).first()

    if req:
        if req.status == 'APPROVED':
            return True, "APPROVED"
        elif req.status == 'REJECTED':
            return False, f"REJECTED: User rejected this action. Feedback: {req.feedback}"
        else:
            return False, f"ACTION_REQUIRED: Tool '{tool_name}' is pending human approval. Please approve it in the dashboard."
            
    # If no request exists, register a new pending request
    sm.create_approval_request(sprint_id, tool_name, arguments)
    return False, f"ACTION_REQUIRED: Tool '{tool_name}' requires human approval. Created approval request. Please approve it in the dashboard."
