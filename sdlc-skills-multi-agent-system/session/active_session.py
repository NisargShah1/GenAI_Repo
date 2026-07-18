from typing import Optional
from session.session_manager import SessionManager

# Shared global state for the active local session
active_sprint_id: Optional[int] = None
session_manager: Optional[SessionManager] = None
