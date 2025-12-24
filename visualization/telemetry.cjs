/* eslint-disable no-console */

// Preload hook for Vite dev server.
// This keeps Vite logs out of the Aspire dashboard unless OTEL_EXPORTER_OTLP_ENDPOINT is set.

const endpointBase = process.env.OTEL_EXPORTER_OTLP_ENDPOINT;
if (!endpointBase) {
  module.exports = {};
  return;
}

(async () => {
  try {
    const { diag, DiagConsoleLogger, DiagLogLevel } = require('@opentelemetry/api');
    const { NodeSDK } = require('@opentelemetry/sdk-node');
    const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
    const { Resource } = require('@opentelemetry/resources');
    const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
    const { OTLPMetricExporter } = require('@opentelemetry/exporter-metrics-otlp-http');
    const { PeriodicExportingMetricReader } = require('@opentelemetry/sdk-metrics');

    const { logs, SeverityNumber } = require('@opentelemetry/api-logs');
    const { LoggerProvider, BatchLogRecordProcessor } = require('@opentelemetry/sdk-logs');
    const { OTLPLogExporter } = require('@opentelemetry/exporter-logs-otlp-http');

    if (process.env.OTEL_DIAGNOSTIC_LOG_LEVEL === 'DEBUG') {
      diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.DEBUG);
    }

    const resource = new Resource({
      'service.name': process.env.OTEL_SERVICE_NAME || 'visualization',
    });

    const sdk = new NodeSDK({
      resource,
      traceExporter: new OTLPTraceExporter({ url: new URL('/v1/traces', endpointBase).toString() }),
      metricReader: new PeriodicExportingMetricReader({
        exporter: new OTLPMetricExporter({ url: new URL('/v1/metrics', endpointBase).toString() }),
      }),
      instrumentations: [getNodeAutoInstrumentations()],
    });

    const loggerProvider = new LoggerProvider({ resource });
    loggerProvider.addLogRecordProcessor(
      new BatchLogRecordProcessor(
        new OTLPLogExporter({ url: new URL('/v1/logs', endpointBase).toString() }),
      ),
    );
    logs.setGlobalLoggerProvider(loggerProvider);

    const otelLogger = logs.getLogger('visualization');

    const passthrough = process.env.PRISMWEAVE_OTEL_CONSOLE_PASSTHROUGH !== '0';
    const originalConsole = {
      log: console.log.bind(console),
      info: console.info.bind(console),
      warn: console.warn.bind(console),
      error: console.error.bind(console),
      debug: console.debug ? console.debug.bind(console) : console.log.bind(console),
    };

    function emitConsole(severityNumber, severityText, method, args) {
      try {
        const body = args
          .map((a) => {
            if (typeof a === 'string') return a;
            try {
              return JSON.stringify(a);
            } catch {
              return String(a);
            }
          })
          .join(' ');

        otelLogger.emit({
          severityNumber,
          severityText,
          body,
          attributes: {
            component: 'console',
            'console.method': method,
          },
        });
      } catch {
        // never throw from console wrappers
      }
    }

    console.log = (...args) => {
      emitConsole(SeverityNumber.INFO, 'INFO', 'log', args);
      if (passthrough) originalConsole.log(...args);
    };
    console.info = (...args) => {
      emitConsole(SeverityNumber.INFO, 'INFO', 'info', args);
      if (passthrough) originalConsole.info(...args);
    };
    console.warn = (...args) => {
      emitConsole(SeverityNumber.WARN, 'WARN', 'warn', args);
      if (passthrough) originalConsole.warn(...args);
    };
    console.error = (...args) => {
      emitConsole(SeverityNumber.ERROR, 'ERROR', 'error', args);
      if (passthrough) originalConsole.error(...args);
    };
    console.debug = (...args) => {
      emitConsole(SeverityNumber.DEBUG, 'DEBUG', 'debug', args);
      if (passthrough) originalConsole.debug(...args);
    };

    await sdk.start();

    otelLogger.emit({
      severityNumber: SeverityNumber.INFO,
      severityText: 'INFO',
      body: 'telemetry_initialized',
      attributes: { component: 'vite-preload' },
    });

    const shutdown = async () => {
      try {
        await sdk.shutdown();
      } finally {
        await loggerProvider.shutdown();
      }
    };

    process.on('SIGINT', () => shutdown().finally(() => process.exit(0)));
    process.on('SIGTERM', () => shutdown().finally(() => process.exit(0)));
  } catch (err) {
    console.warn('[visualization] telemetry preload failed:', err?.message || err);
  }
})();
