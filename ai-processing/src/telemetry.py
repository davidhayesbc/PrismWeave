from __future__ import annotations

import importlib
import logging
import os
from typing import Any
from urllib.parse import urlparse

_logger = logging.getLogger("prismweave.telemetry")
_is_configured = False


def _get_service_name(default: str) -> str:
    return os.getenv("OTEL_SERVICE_NAME") or default


def _otlp_http_endpoint_for_signal(endpoint_base: str, signal: str) -> str:
    """Normalize an OTLP HTTP endpoint base to a per-signal endpoint.

    Aspire typically sets `OTEL_EXPORTER_OTLP_ENDPOINT` to an OTLP HTTP base URL
    like `http://localhost:4318`. The OTLP HTTP exporters expect per-signal
    endpoints (e.g. `/v1/traces`, `/v1/metrics`, `/v1/logs`) when explicitly
    provided.

    If the provided endpoint already includes a non-trivial path, it is assumed
    to be a complete endpoint and returned as-is.
    """

    base = (endpoint_base or "").strip()
    if not base:
        return base

    parsed = urlparse(base)

    # If user supplied a full path (e.g. http://host:4318/v1/traces), trust it.
    if parsed.path and parsed.path not in ("/", ""):
        return base

    return base.rstrip("/") + f"/v1/{signal}"


def configure_telemetry(service_name: str, *, service_version: str | None = None) -> None:
    """Configure OpenTelemetry for traces, metrics, and logs.

    Aspire sets OpenTelemetry environment variables (notably OTEL_EXPORTER_OTLP_ENDPOINT)
    when orchestrating the app. This function is safe to call multiple times.

    If OTEL_EXPORTER_OTLP_ENDPOINT is not set, telemetry export is disabled and this
    function becomes a no-op (aside from basic logging setup).
    """

    global _is_configured
    if _is_configured:
        return

    otlp_endpoint_base = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not otlp_endpoint_base:
        # No exporter configured (common when running outside Aspire). Keep app running.
        _logger.debug("OTEL_EXPORTER_OTLP_ENDPOINT not set; OpenTelemetry export disabled")
        _is_configured = True
        return

    try:
        # Dynamic imports keep OpenTelemetry optional and avoid static import errors.
        otel_metrics = importlib.import_module("opentelemetry.metrics")
        otel_trace = importlib.import_module("opentelemetry.trace")
        otel_logs_api = importlib.import_module("opentelemetry._logs")

        trace_exporter_mod = importlib.import_module("opentelemetry.exporter.otlp.proto.http.trace_exporter")
        metric_exporter_mod = importlib.import_module("opentelemetry.exporter.otlp.proto.http.metric_exporter")
        log_exporter_mod = importlib.import_module("opentelemetry.exporter.otlp.proto.http._log_exporter")

        instrumentation_logging_mod = importlib.import_module("opentelemetry.instrumentation.logging")
        instrumentation_requests_mod = importlib.import_module("opentelemetry.instrumentation.requests")

        sdk_logs_mod = importlib.import_module("opentelemetry.sdk._logs")
        sdk_logs_export_mod = importlib.import_module("opentelemetry.sdk._logs.export")
        sdk_metrics_mod = importlib.import_module("opentelemetry.sdk.metrics")
        sdk_metrics_export_mod = importlib.import_module("opentelemetry.sdk.metrics.export")
        sdk_resources_mod = importlib.import_module("opentelemetry.sdk.resources")
        sdk_trace_mod = importlib.import_module("opentelemetry.sdk.trace")
        sdk_trace_export_mod = importlib.import_module("opentelemetry.sdk.trace.export")

        otlp_span_exporter = trace_exporter_mod.OTLPSpanExporter
        otlp_metric_exporter = metric_exporter_mod.OTLPMetricExporter
        otlp_log_exporter = log_exporter_mod.OTLPLogExporter

        logging_instrumentor = instrumentation_logging_mod.LoggingInstrumentor
        requests_instrumentor = instrumentation_requests_mod.RequestsInstrumentor

        logger_provider_cls = sdk_logs_mod.LoggerProvider
        logging_handler_cls = sdk_logs_mod.LoggingHandler
        batch_log_record_processor_cls = sdk_logs_export_mod.BatchLogRecordProcessor

        meter_provider_cls = sdk_metrics_mod.MeterProvider
        periodic_exporting_metric_reader_cls = sdk_metrics_export_mod.PeriodicExportingMetricReader
        resource_cls = sdk_resources_mod.Resource

        tracer_provider_cls = sdk_trace_mod.TracerProvider
        batch_span_processor_cls = sdk_trace_export_mod.BatchSpanProcessor

        resource_attributes: dict[str, Any] = {"service.name": _get_service_name(service_name)}
        if service_version:
            resource_attributes["service.version"] = service_version

        resource = resource_cls.create(resource_attributes)

        tracer_provider = tracer_provider_cls(resource=resource)
        tracer_provider.add_span_processor(
            batch_span_processor_cls(
                otlp_span_exporter(endpoint=_otlp_http_endpoint_for_signal(otlp_endpoint_base, "traces"))
            )
        )
        otel_trace.set_tracer_provider(tracer_provider)

        metric_reader = periodic_exporting_metric_reader_cls(
            otlp_metric_exporter(endpoint=_otlp_http_endpoint_for_signal(otlp_endpoint_base, "metrics"))
        )
        otel_metrics.set_meter_provider(meter_provider_cls(resource=resource, metric_readers=[metric_reader]))

        logger_provider = logger_provider_cls(resource=resource)
        logger_provider.add_log_record_processor(
            batch_log_record_processor_cls(
                otlp_log_exporter(endpoint=_otlp_http_endpoint_for_signal(otlp_endpoint_base, "logs"))
            )
        )
        otel_logs_api.set_logger_provider(logger_provider)

        # Bridge stdlib logging -> OpenTelemetry logs.
        root_logger = logging.getLogger()
        root_logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

        otel_handler = logging_handler_cls(level=logging.NOTSET, logger_provider=logger_provider)
        # Avoid duplicate handlers if user code configured logging already.
        if not any(isinstance(h, logging_handler_cls) for h in root_logger.handlers):
            root_logger.addHandler(otel_handler)

        # Auto-instrument common libraries.
        requests_instrumentor().instrument()
        logging_instrumentor().instrument(set_logging_format=False)

        _logger.info("OpenTelemetry configured (OTLP endpoint base: %s)", otlp_endpoint_base)
        _is_configured = True

    except Exception:
        # Never crash the service if telemetry wiring fails.
        _logger.exception("Failed to configure OpenTelemetry; continuing without telemetry")
        _is_configured = True


def instrument_fastapi(app: Any) -> None:
    """Instrument a FastAPI app for tracing.

    Safe to call even when OpenTelemetry isn't configured.
    """

    if not os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        return

    try:
        fastapi_instrumentation_mod = importlib.import_module("opentelemetry.instrumentation.fastapi")
        fastapi_instrumentation_mod.FastAPIInstrumentor.instrument_app(app)
    except Exception:
        _logger.exception("Failed to instrument FastAPI")
