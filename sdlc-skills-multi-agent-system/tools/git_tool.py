import os
import git
from tools.approval import check_approval

WORKSPACE_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def git_status() -> str:
    """
    Get the current git status of the repository.
    """
    try:
        repo = git.Repo(WORKSPACE_ROOT)
        return repo.git.status()
    except git.exc.InvalidGitRepositoryError:
        return "Workspace is not initialized as a Git repository. Run 'git init' first."
    except Exception as e:
        return f"Git Status Error: {str(e)}"

def git_diff() -> str:
    """
    Show current unstaged/staged differences in the repository.
    """
    try:
        repo = git.Repo(WORKSPACE_ROOT)
        # Check staged and unstaged diffs
        diff_unstaged = repo.git.diff()
        diff_staged = repo.git.diff("--staged")
        return f"--- UNSTAGED CHANGES ---\n{diff_unstaged}\n\n--- STAGED CHANGES ---\n{diff_staged}"
    except git.exc.InvalidGitRepositoryError:
        return "Workspace is not initialized as a Git repository."
    except Exception as e:
        return f"Git Diff Error: {str(e)}"

def git_commit(message: str) -> str:
    """
    Stage all changes and commit them with a message. Requires user approval.
    Args:
        message: The commit message following conventional commit guidelines.
    """
    try:
        repo = git.Repo(WORKSPACE_ROOT)
        
        # Check human approval
        args = {"message": message}
        approved, status_msg = check_approval("git_commit", args)
        if not approved:
            return status_msg
            
        repo.git.add(A=True)
        if not repo.index.diff("HEAD"):
            return "No changes to commit."
            
        commit = repo.index.commit(message)
        return f"Success: Committed changes. Hash: {commit.hexsha}\nMessage: {message}"
    except git.exc.InvalidGitRepositoryError:
        return "Workspace is not initialized as a Git repository."
    except Exception as e:
        return f"Git Commit Error: {str(e)}"
