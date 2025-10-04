export interface ILogger {
  debug: (...args: unknown[]) => void;
  info: (...args: unknown[]) => void;
  warn: (...args: unknown[]) => void;
  error: (...args: unknown[]) => void;
}

class ConsoleLogger implements ILogger {
  constructor(private readonly prefix?: string) {}

  debug(...args: unknown[]): void {
    if (typeof console !== 'undefined' && console.debug) {
      console.debug(this.formatMessage(args));
    }
  }

  info(...args: unknown[]): void {
    if (typeof console !== 'undefined' && console.info) {
      console.info(this.formatMessage(args));
    }
  }

  warn(...args: unknown[]): void {
    if (typeof console !== 'undefined' && console.warn) {
      console.warn(this.formatMessage(args));
    }
  }

  error(...args: unknown[]): void {
    if (typeof console !== 'undefined' && console.error) {
      console.error(this.formatMessage(args));
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
