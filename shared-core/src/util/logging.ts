// Simple console logger used by shared modules.
// Keep the implementation lightweight and dependency-free so it can run in any
// JavaScript environment where `console` is available.

export interface ILogger {
  debug: (...args: unknown[]) => void;
  info: (...args: unknown[]) => void;
  warn: (...args: unknown[]) => void;
  error: (...args: unknown[]) => void;
}

class ConsoleLogger implements ILogger {
  constructor(private readonly prefix?: string) {}

  debug(...args: unknown[]): void {
    if (typeof console !== 'undefined' && typeof console.debug === 'function') {
      console.debug(...this.formatMessage(args));
    }
  }

  info(...args: unknown[]): void {
    if (typeof console !== 'undefined' && typeof console.info === 'function') {
      console.info(...this.formatMessage(args));
    }
  }

  warn(...args: unknown[]): void {
    if (typeof console !== 'undefined' && typeof console.warn === 'function') {
      console.warn(...this.formatMessage(args));
    }
  }

  error(...args: unknown[]): void {
    if (typeof console !== 'undefined' && typeof console.error === 'function') {
      console.error(...this.formatMessage(args));
    }
  }

  private formatMessage(args: unknown[]): unknown[] {
    if (!this.prefix) {
      return args;
    }

    return [`[${this.prefix}]`, ...args];
  }
}

export function createConsoleLogger(prefix?: string): ILogger {
  return new ConsoleLogger(prefix);
}
