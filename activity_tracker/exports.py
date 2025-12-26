import csv
import io
import json

from .redaction import redact_diff


def export_audit_logs(
    queryset, *, format="csv", redact_sensitive=True, include_metadata=True
):
    if format not in ("csv", "json"):
        raise ValueError("Format must be 'csv' or 'json'")

    rows = []

    for log in queryset.select_related("user", "content_type"):
        metadata = log.metadata if log.metadata else {}

        if redact_sensitive and "diff" in metadata:
            model = log.content_type.model_class() if log.content_type else None
            sensitive_fields = (
                getattr(model, "SENSITIVE_FIELDS", set()) if model else set()
            )
            metadata = metadata.copy()
            metadata["diff"] = redact_diff(metadata["diff"], sensitive_fields)

        row = {
            "id": log.id,
            "created_at": log.created_at.isoformat(),
            "actor_id": log.actor_id,
            "actor_repr": str(log.actor) if log.actor else None,
            "action": log.action,
            "target_type": log.content_type.model if log.content_type else None,
            "target_id": log.object_id,
            "target_repr": log.object_repr,
            "metadata": metadata if include_metadata else None,
        }
        rows.append(row)

    if format == "json":
        return json.dumps(rows, indent=2), "application/json"

    return _export_csv(rows), "text/csv"


def _export_csv(rows):
    if not rows:
        return ""

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()
