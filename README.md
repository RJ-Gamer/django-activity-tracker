# Django Activity Tracker

**An explicit, intent-aware activity & audit logging library for Django and Django REST Framework.**

This library helps you answer, reliably:

> **Who** did **what**, **when**, **where**, and **why** —
> across **Django Admin**, **DRF APIs**, and **custom workflows**.

It is designed for **correctness over magic**, and for systems where **audit data must be trustworthy**.

---

## ✨ Key Features

* ✅ Centralized activity logging via a single service
* ✅ Correct **actor attribution** (user / system / anonymous)
* ✅ Works with:

  * Django Admin
  * DRF ViewSets
  * APIView / GenericAPIView
  * JWT / OAuth authentication
* ✅ Field-level diffs (opt-in, PII-safe)
* ✅ Request context capture (IP, user-agent, path, method)
* ✅ Async-safe (uses `contextvars`)
* ✅ Zero duplicate logs (automatic signal suppression)
* ✅ Explicit > implicit (no guessing, no magic)

---

## ❌ What This Library Does *Not* Do (By Design)

* ❌ Automatically track bulk updates (`QuerySet.update`, `bulk_update`)
* ❌ Infer intent from raw SQL or database triggers
* ❌ Guess actors inside model signals
* ❌ Log sensitive fields unless you explicitly allow it

If a system claims to do these automatically, it is lying or unsafe.

---

## Installation

```bash
pip install django-activity-tracker
```

---

## Basic Setup

### 1️⃣ Add to `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    ...
    "activity_tracker",
]
```

### 2️⃣ Add Middleware (Required for actor + request context)

```python
MIDDLEWARE = [
    ...
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "activity_tracker.middleware.ActivityTrackerMiddleware",
    ...
]
```

> ⚠️ Must come **after** `AuthenticationMiddleware`.

### 3️⃣ Run migrations

```bash
python manage.py makemigrations activity_tracker
python manage.py migrate
```

---

## Core Concept (Important)

**Everything funnels through one function:**

```python
track_activity(...)
```

All integrations (Admin, DRF, signals, helpers) eventually call this.

This guarantees:

* consistent behavior
* predictable metadata
* easy future refactors

---

## Basic Usage

### Manual tracking (anywhere)

```python
from activity_tracker.services import track_activity

track_activity(
    action="CUSTOM_EVENT",
    actor=request.user,
    metadata={"reason": "manual_override"},
)
```

---

## Django Admin Integration (Recommended)

Admin is an **intent boundary** — we track there explicitly.

### Enable Admin auditing

```python
from django.contrib import admin
from activity_tracker.admin_mixins import AuditModelAdminMixin
from .models import Article


@admin.register(Article)
class ArticleAdmin(AuditModelAdminMixin, admin.ModelAdmin):
    pass
```

What you get:

* Correct actor (`request.user`)
* Exact field diffs via `form.changed_data`
* CREATE / UPDATE / DELETE events
* No duplicate signal logs

---

## Django REST Framework (DRF)

### ✅ Best Option: ViewSets (Recommended)

```python
from rest_framework.viewsets import ModelViewSet
from activity_tracker.drf_mixins import AuditModelViewSetMixin


class ArticleViewSet(AuditModelViewSetMixin, ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
```

This provides:

* Intent-level diffs (`serializer.validated_data`)
* Explicit actor
* Correct metadata
* No race conditions
* No signal duplication

---

### APIView / GenericAPIView (Explicit Helpers)

For APIs without lifecycle hooks, use helpers.

```python
from activity_tracker.helpers import audit_update

class ArticleUpdateAPI(UpdateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def perform_update(self, serializer):
        instance = self.get_object()
        validated_data = serializer.validated_data
        instance = serializer.save()

        audit_update(
            request=self.request,
            instance=instance,
            validated_data=validated_data,
        )
```

Helpers available:

* `audit_create`
* `audit_update`
* `audit_delete`

---

## JWT / OAuth Authentication

Stateless auth systems **do not emit Django login signals**.

You must log intent explicitly.

```python
from activity_tracker.drf import track_login, track_logout

track_login(request=request, user=user, auth_type="jwt")
track_logout(request=request, user=request.user, auth_type="jwt")
```

This is intentional and correct.

---

## CRUD Signals (Fallback Only)

Model signals exist as a **safety net**, not the primary mechanism.

### Opt-in via mixin

```python
from activity_tracker.model_signals import TrackModelActivityMixin

class Article(TrackModelActivityMixin, models.Model):
    title = models.CharField(max_length=255)
```

Signals are automatically **disabled per request** when:

* Admin mixins are used
* DRF ViewSet mixins are used

So you never get duplicates.

---

## Field-Level Diff Tracking (Advanced)

Diff tracking is **opt-in** and **PII-aware**.

```python
class Article(TrackModelActivityMixin, models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()

    TRACK_FIELDS = {"title", "body"}
    SENSITIVE_FIELDS = {"body"}
```

Resulting diff example:

```json
{
  "diff": {
    "title": {"old": "Old", "new": "New"},
    "body": {"old": "***REDACTED***", "new": "***REDACTED***"}
  }
}
```

---

## Metadata Model (How Data Is Stored)

Each activity record contains:

* `actor` (user or null)
* `action` (normalized string)
* `target` (generic FK, optional)
* `metadata` (JSON)
* `created_at`

Metadata automatically includes:

* IP address
* User agent
* HTTP method
* Request path

Explicit metadata **always overrides** automatic metadata.

---

## Philosophy (Read This)

> **Signals detect effects.
> Views and Admin express intent.
> Audit systems must prefer intent over inference.**

This library is explicit by design:

* Less magic
* More correctness
* Fewer legal surprises

---

## Common Pitfalls (Avoid These)

* ❌ Expecting signals to capture API intent
* ❌ Expecting bulk updates to be audited automatically
* ❌ Logging raw PII in diffs
* ❌ Relying on thread-locals

---

## Compatibility

* Python 3.9+
* Django 3.2+
* Django REST Framework (optional)

---

## License

MIT License

---

## Final Note

This library is built for:

* healthcare systems
* fintech platforms
* internal admin tools
* compliance-sensitive products

If you want “magic logging”, this is not it.
If you want **audit data you can defend**, you’re in the right place.

## `LICENSE` 
Use MIT

```text

MIT License

Copyright (c) 2024 Rajat Jog
```