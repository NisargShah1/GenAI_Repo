import random

# In-memory mock storage for tickets during run
_MOCK_TICKETS = {}

def create_jira_ticket(title: str, description: str, issue_type: str = "Story") -> str:
    """
    Create a mock ticket in the Jira project board.
    Args:
        title: Title of the Jira issue.
        description: Description details of the issue.
        issue_type: Type of ticket ('Epic', 'Story', 'Task', 'Bug').
    """
    ticket_id = random.randint(100, 999)
    key = f"SF-{ticket_id}"
    _MOCK_TICKETS[key] = {
        "key": key,
        "title": title,
        "description": description,
        "type": issue_type,
        "status": "TO DO"
    }
    return f"Success: Created Jira ticket {key} [{issue_type}] - Title: '{title}'"

def update_jira_ticket_status(ticket_key: str, status: str) -> str:
    """
    Update status of a mock Jira ticket.
    Args:
        ticket_key: Jira ticket ID (e.g. 'SF-101').
        status: Target status ('TO DO', 'IN PROGRESS', 'DONE').
    """
    key = ticket_key.upper().strip()
    if key in _MOCK_TICKETS:
        _MOCK_TICKETS[key]["status"] = status
        return f"Success: Updated Jira ticket {key} status to '{status}'"
    # Create on the fly if not found to simulate existence
    _MOCK_TICKETS[key] = {
        "key": key,
        "title": "Ad-hoc Sprint Item",
        "description": "Generated dynamically during orchestration.",
        "type": "Task",
        "status": status
    }
    return f"Success: Jira ticket {key} status updated to '{status}'"

def get_jira_ticket(ticket_key: str) -> str:
    """
    Retrieve details of a mock Jira ticket.
    Args:
        ticket_key: Jira ticket ID (e.g. 'SF-101').
    """
    key = ticket_key.upper().strip()
    ticket = _MOCK_TICKETS.get(key)
    if not ticket:
        return f"Jira Error: Ticket {key} not found."
    return (
        f"Ticket: {ticket['key']}\n"
        f"Type: {ticket['type']}\n"
        f"Title: {ticket['title']}\n"
        f"Status: {ticket['status']}\n"
        f"Description: {ticket['description']}"
    )
