class ConsoleLogger {
    prefix;
    constructor(prefix) {
        this.prefix = prefix;
    }
    debug(...args) {
        if (typeof console !== 'undefined' && console.debug) {
            console.debug(this.formatMessage(args));
        }
    }
    info(...args) {
        if (typeof console !== 'undefined' && console.info) {
            console.info(this.formatMessage(args));
        }
    }
    warn(...args) {
        if (typeof console !== 'undefined' && console.warn) {
            console.warn(this.formatMessage(args));
        }
    }
    error(...args) {
        if (typeof console !== 'undefined' && console.error) {
            console.error(this.formatMessage(args));
        }
    }
    formatMessage(args) {
        if (!this.prefix) {
            return args;
        }
        return [`[${this.prefix}]`, ...args];
    }
}
export function createConsoleLogger(prefix) {
    return new ConsoleLogger(prefix);
}
//# sourceMappingURL=logging.js.map