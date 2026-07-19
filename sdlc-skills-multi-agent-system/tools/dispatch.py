"""Dispatch approved tool actions to their real implementations.

Approval-gated tools return early with an ``ACTION_REQUIRED`` message on their
first invocation, before performing any side effect. Once the user approves the
request, the action must actually be executed. This module maps a stored
approval (``tool_name`` + ``arguments``) back to the concrete tool call so the
side effect (e.g. writing a file to disk) finally happens.
"""
import logging
from typing import Callable, Dict

from tools.filesystem_tool import write_file, delete_file
from tools.shell_tool import execute_command
from tools.git_tool import git_commit

logger = logging.getLogger("skillforge.tools.dispatch")

_DISPATCH: Dict[str, Callable[[dict], str]] = {
    "write_file": lambda args: write_file(args["path"], args["content"]),
    "delete_file": lambda args: delete_file(args["path"]),
    "execute_command": lambda args: execute_command(args["command"]),
    "git_commit": lambda args: git_commit(args["message"]),
}


def execute_approved_action(tool_name: str, arguments: dict) -> str:
    """Re-invoke an approved tool so its side effect is performed.

    The tool re-runs ``check_approval``, which now finds the APPROVED request and
    lets the action through.
    """
    handler = _DISPATCH.get(tool_name)
    if handler is None:
        return f"Error: no dispatcher registered for tool '{tool_name}'."
    try:
        result = handler(arguments)
        logger.info(f"Executed approved action '{tool_name}': {result[:120]}")
        return result
    except KeyError as e:
        return f"Error: missing argument {e} for approved tool '{tool_name}'."
