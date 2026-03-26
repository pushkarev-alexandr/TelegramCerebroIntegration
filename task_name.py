def sanitize_task_name(task_name: str) -> str:
    cleaned = "".join(ch for ch in task_name if ch not in "\\/#:?&'\"+|")
    return " ".join(cleaned.split())


def build_task_name(definition: str) -> str:
    """
    Temporary stub for task naming.
    Uses the first line as task name (max 40 chars).
    """
    first_line = definition.splitlines()[0].strip() if definition.strip() else ""
    if not first_line:
        return "Untitled task"

    raw_task_name = first_line[:40]
    sanitized_task_name = sanitize_task_name(raw_task_name)
    return sanitized_task_name or "Untitled task"
