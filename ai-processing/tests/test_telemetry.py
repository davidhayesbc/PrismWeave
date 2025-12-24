import os


def test_otlp_http_endpoint_for_signal_appends_v1_paths():
    from src.telemetry import _otlp_http_endpoint_for_signal

    assert _otlp_http_endpoint_for_signal("http://localhost:4318", "traces") == "http://localhost:4318/v1/traces"
    assert _otlp_http_endpoint_for_signal("http://localhost:4318/", "metrics") == "http://localhost:4318/v1/metrics"
    assert _otlp_http_endpoint_for_signal("http://localhost:4318", "logs") == "http://localhost:4318/v1/logs"


def test_otlp_http_endpoint_for_signal_preserves_full_path():
    from src.telemetry import _otlp_http_endpoint_for_signal

    assert (
        _otlp_http_endpoint_for_signal("http://localhost:4318/v1/traces", "traces") == "http://localhost:4318/v1/traces"
    )


def test_configure_telemetry_no_endpoint_does_not_crash(monkeypatch):
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)

    from src.telemetry import configure_telemetry

    configure_telemetry("ai-processing-test")


def test_configure_telemetry_with_endpoint_missing_deps_does_not_crash(monkeypatch):
    # Even if OpenTelemetry packages aren't installed yet, configure_telemetry must not crash.
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")

    from src.telemetry import configure_telemetry

    configure_telemetry("ai-processing-test")


def test_instrument_fastapi_no_endpoint_is_noop(monkeypatch):
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)

    from src.telemetry import instrument_fastapi

    class DummyApp:
        pass

    instrument_fastapi(DummyApp())


def test_instrument_fastapi_with_endpoint_missing_deps_does_not_crash(monkeypatch):
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")

    from src.telemetry import instrument_fastapi

    class DummyApp:
        pass

    instrument_fastapi(DummyApp())
