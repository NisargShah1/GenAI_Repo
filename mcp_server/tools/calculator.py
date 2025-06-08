from simpleeval import simple_eval

def calculate_if_needed(prompt: str):
    try:
        if "calculate" in prompt.lower():
            expr = prompt.lower().replace("calculate", "").strip()
            result = simple_eval(expr)
            return result
    except Exception:
        return None
