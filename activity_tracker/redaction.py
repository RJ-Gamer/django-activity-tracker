REDACTION_VALUE = "***REDACTED***"


def redact_diff(diff: dict, sensitive_fields: set | None = None) -> dict:
    """
    Redact sensitive fields in a diff structure.

    Expected diff format:
    {
        "field_name": {"old": ..., "new": ...},
        ...
    }
    """
    if not diff:
        return diff

    if not sensitive_fields:
        return diff

    redacted = {}

    for field, change in diff.items():
        if field in sensitive_fields:
            redacted[field] = {
                "old": REDACTION_VALUE,
                "new": REDACTION_VALUE,
            }
        else:
            redacted[field] = change

    return redacted
