SECRET_KEY = "test"

ACTIVITY_TRACKER = {
    "ENABLED": True,
    "PERSIST": True,
    "TRACK_ANONYMOUS": True,
}

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "activity_tracker",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

MIDDLEWARE = [
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "activity_tracker.middleware.ActivityTrackerMiddleware",
]

USE_TZ = True
