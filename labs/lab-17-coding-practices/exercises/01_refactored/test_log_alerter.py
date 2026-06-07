"""
Tests para log_alerter — demuestra que el código es testeable gracias a DIP.
Correr: python -m pytest test_log_alerter.py -v
O sin pytest: python test_log_alerter.py
"""

import tempfile
import os
from log_alerter import Config, parse_errors, format_summary, run_alerter, StdoutNotifier


def test_parse_errors_finds_errors():
    """parse_errors extrae solo líneas con ERROR."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write("2026-05-26 INFO Starting app\n")
        f.write("2026-05-26 ERROR Connection timeout to db-primary\n")
        f.write("2026-05-26 WARN Slow query detected\n")
        f.write("2026-05-26 ERROR OOM killed worker-3\n")
        f.name
    
    errors = parse_errors(f.name)
    os.unlink(f.name)
    
    assert len(errors) == 2
    assert "Connection timeout" in errors[0]
    assert "OOM killed" in errors[1]


def test_parse_errors_missing_file():
    """parse_errors maneja archivo inexistente sin crashear."""
    errors = parse_errors("/nonexistent/file.log")
    assert errors == []


def test_format_summary_no_errors():
    """Sin errores = mensaje positivo."""
    result = format_summary([])
    assert "No errors" in result


def test_format_summary_with_errors():
    """Con errores = muestra conteo y sample."""
    errors = [f"Error {i}" for i in range(10)]
    result = format_summary(errors, max_display=3)
    assert "10 errors" in result
    assert "Error 0" in result
    assert "Error 2" in result
    assert "7 more" in result


def test_format_summary_few_errors():
    """Pocos errores = no muestra 'and X more'."""
    errors = ["Error A", "Error B"]
    result = format_summary(errors, max_display=5)
    assert "2 errors" in result
    assert "more" not in result


def test_run_alerter_integration():
    """Integration test: todo el flujo con StdoutNotifier (mock)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write("ERROR test error line\n")
        f.write("INFO normal line\n")
    
    config = Config(
        log_file=f.name,
        webhook_url="http://fake",
        max_errors=5,
    )
    
    # DIP en acción: inyectamos StdoutNotifier en vez de WebhookNotifier
    notifier = StdoutNotifier()
    run_alerter(config, notifier)  # No crashea, no hace HTTP
    
    os.unlink(f.name)


if __name__ == "__main__":
    # Correr sin pytest
    tests = [
        test_parse_errors_finds_errors,
        test_parse_errors_missing_file,
        test_format_summary_no_errors,
        test_format_summary_with_errors,
        test_format_summary_few_errors,
        test_run_alerter_integration,
    ]
    for test in tests:
        try:
            test()
            print(f"  ✅ {test.__name__}")
        except AssertionError as e:
            print(f"  ❌ {test.__name__}: {e}")
    
    print(f"\n{'='*40}")
    print(f"  {len(tests)} tests completed")
