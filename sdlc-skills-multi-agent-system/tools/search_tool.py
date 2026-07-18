import os
import fnmatch
from typing import List

WORKSPACE_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
IGNORE_DIRS = {'.git', '.venv', '__pycache__', '.gemini', 'node_modules', '.idea', '.vscode'}

def find_files(pattern: str) -> List[str]:
    """
    Find files in the workspace matching a glob pattern (e.g. '*.java' or '*.xml').
    Args:
        pattern: The glob pattern to search for.
    """
    matches = []
    for root, dirs, files in os.walk(WORKSPACE_ROOT):
        # Prune ignore dirs
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for filename in fnmatch.filter(files, pattern):
            rel_path = os.path.relpath(os.path.join(root, filename), WORKSPACE_ROOT)
            matches.append(rel_path)
    return matches

def search_content(query: str, case_sensitive: bool = False) -> str:
    """
    Search for text matches within project files.
    Args:
        query: The string query to search for in files.
        case_sensitive: Whether the search should be case sensitive.
    """
    results = []
    query_str = query if case_sensitive else query.lower()
    
    for root, dirs, files in os.walk(WORKSPACE_ROOT):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for filename in files:
            # Limit to searchable extensions
            if not filename.endswith(('.py', '.java', '.md', '.txt', '.xml', '.properties', '.json', '.yml')):
                continue
                
            abs_path = os.path.join(root, filename)
            rel_path = os.path.relpath(abs_path, WORKSPACE_ROOT)
            
            try:
                with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_no, line in enumerate(f, 1):
                        line_to_check = line if case_sensitive else line.lower()
                        if query_str in line_to_check:
                            results.append(f"{rel_path}:{line_no}: {line.strip()}")
            except Exception:
                pass
                
    if not results:
        return f"No matches found for '{query}' in workspace."
    return "\n".join(results[:50]) # cap results

def search_symbols(symbol: str) -> str:
    """
    Search for code declarations (classes, methods) containing the given symbol string.
    Args:
        symbol: The symbol string to look for (e.g. 'UserService').
    """
    results = []
    for root, dirs, files in os.walk(WORKSPACE_ROOT):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for filename in files:
            if not filename.endswith(('.py', '.java')):
                continue
            abs_path = os.path.join(root, filename)
            rel_path = os.path.relpath(abs_path, WORKSPACE_ROOT)
            try:
                with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_no, line in enumerate(f, 1):
                        line_stripped = line.strip()
                        is_symbol = False
                        if filename.endswith('.py'):
                            if line_stripped.startswith(('def ', 'class ')) and symbol in line_stripped:
                                is_symbol = True
                        elif filename.endswith('.java'):
                            if ('class ' in line_stripped or 'interface ' in line_stripped or 'void ' in line_stripped or 'public ' in line_stripped) and symbol in line_stripped:
                                if not line_stripped.startswith(('//', '*', 'import', 'System.out')):
                                    is_symbol = True
                        if is_symbol:
                            results.append(f"{rel_path}:{line_no}: {line_stripped}")
            except Exception:
                pass
    if not results:
        return f"No symbols found matching '{symbol}'."
    return "\n".join(results)
