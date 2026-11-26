"""Celery task tests (Sprint 01B)."""

from api.tasks import probe


def test_probe_task_executes_eagerly():
    result = probe.apply()
    assert result.get() == {"status": "ok", "message": "probe"}


def test_probe_task_returns_expected_shape():
    result = probe.apply(args=["hello"])
    assert result.get()["message"] == "hello"
