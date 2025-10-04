export interface ILogger {
    debug: (...args: unknown[]) => void;
    info: (...args: unknown[]) => void;
    warn: (...args: unknown[]) => void;
    error: (...args: unknown[]) => void;
}
export declare function createConsoleLogger(prefix?: string): ILogger;
//# sourceMappingURL=logging.d.ts.map