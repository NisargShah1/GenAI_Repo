import subprocess
import logging
from tools.approval import check_approval

logger = logging.getLogger("skillforge.tools.shell")

def execute_command(command: str) -> str:
    """
    Execute a shell command in the workspace. Requires user approval.
    Args:
        command: The shell command to run.
    """
    try:
        # Check human approval
        args = {"command": command}
        approved, status_msg = check_approval("execute_command", args)
        if not approved:
            return status_msg

        logger.info(f"Executing approved command: {command}")
        
        # Run command synchronously with a timeout
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=90
        )
        
        output = (
            f"Exit Code: {result.returncode}\n"
            f"--- STDOUT ---\n{result.stdout}\n"
            f"--- STDERR ---\n{result.stderr}"
        )
        return output
        
    except subprocess.TimeoutExpired:
        return "Error: Command execution timed out (90s limit)."
    except Exception as e:
        return f"Error executing shell command: {str(e)}"
