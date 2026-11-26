"""Django settings for local development (Sprint 01B)."""

import os

os.environ.setdefault("APP_DEBUG", "true")

from .base import *  # noqa: E402,F401,F403

DEBUG = True
