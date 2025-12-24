import process from 'node:process';

// Telemetry should never crash the dev server.
export async function startTelemetry({ serviceName }) {
  const endpointBase = process.env.OTEL_EXPORTER_OTLP_ENDPOINT;
  if (!endpointBase) {
    return { shutdown: async () => {} };
  }

  try {
    const { diag, DiagConsoleLogger, DiagLogLevel } = await import('@opentelemetry/api');
    const { NodeSDK } = await import('@opentelemetry/sdk-node');
    const { getNodeAutoInstrumentations } = await import(
      '@opentelemetry/auto-instrumentations-node'
    );
    const { Resource } = await import('@opentelemetry/resources');
    const { OTLPTraceExporter } = await import('@opentelemetry/exporter-trace-otlp-http');
    const { OTLPMetricExporter } = await import('@opentelemetry/exporter-metrics-otlp-http');
    const { PeriodicExportingMetricReader } = await import('@opentelemetry/sdk-metrics');

    // Logs (OpenTelemetry Logs API)
    const { logs, SeverityNumber } = await import('@opentelemetry/api-logs');
    const { LoggerProvider, BatchLogRecordProcessor } = await import('@opentelemetry/sdk-logs');
    const { OTLPLogExporter } = await import('@opentelemetry/exporter-logs-otlp-http');

    // Optional internal diagnostics
    if (process.env.OTEL_DIAGNOSTIC_LOG_LEVEL === 'DEBUG') {
      diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.DEBUG);
    }

    const resource = new Resource({
      'service.name': process.env.OTEL_SERVICE_NAME || serviceName,
    });

    const traceExporter = new OTLPTraceExporter({
      url: new URL('/v1/traces', endpointBase).toString(),
    });
    const metricReader = new PeriodicExportingMetricReader({
      exporter: new OTLPMetricExporter({ url: new URL('/v1/metrics', endpointBase).toString() }),
    });

    const sdk = new NodeSDK({
      resource,
      traceExporter,
      metricReader,
      instrumentations: [getNodeAutoInstrumentations()],
    });

    const loggerProvider = new LoggerProvider({ resource });
    loggerProvider.addLogRecordProcessor(
      new BatchLogRecordProcessor(
        new OTLPLogExporter({ url: new URL('/v1/logs', endpointBase).toString() }),
      ),
    );
    logs.setGlobalLoggerProvider(loggerProvider);

    const otelLogger = logs.getLogger(serviceName);

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

    function log(severityNumber, severityText, body, attributes = {}) {
      otelLogger.emit({
        severityNumber,
        severityText,
        body,
        attributes,
      });
    }

    await sdk.start();

    return {
      logInfo: (msg, attrs) => log(SeverityNumber.INFO, 'INFO', msg, attrs),
      logWarn: (msg, attrs) => log(SeverityNumber.WARN, 'WARN', msg, attrs),
      logError: (msg, attrs) => log(SeverityNumber.ERROR, 'ERROR', msg, attrs),
      shutdown: async () => {
        try {
          await sdk.shutdown();
        } finally {
          await loggerProvider.shutdown();
        }
      },
    };
  } catch {
    // If deps aren't installed or something else breaks, keep server alive.
    return { shutdown: async () => {} };
  }
}
