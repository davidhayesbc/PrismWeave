import type { IDocumentMetadata, IImageAsset } from '../types.js';
import { type ILogger } from '../util/index.js';
export interface IConversionOptions {
    preserveFormatting?: boolean;
    includeMetadata?: boolean;
    generateFrontmatter?: boolean;
    customRules?: Record<string, unknown>;
    headingStyle?: 'atx' | 'setext';
    bulletListMarker?: '-' | '*' | '+';
    codeBlockStyle?: 'fenced' | 'indented';
    linkStyle?: 'inlined' | 'referenced';
}
export interface IConversionResult {
    markdown: string;
    frontmatter: string;
    metadata: IDocumentMetadata;
    images: IImageAsset[];
    wordCount: number;
}
interface ISemanticSelectors {
    callouts: string[];
    quotes: string[];
    highlights: string[];
    captions: string[];
    metadata: string[];
    codeElements: string[];
}
/**
 * Environment-agnostic Markdown conversion engine. This class avoids direct
 * browser dependencies so it can run in the extension, CLI, and test
 * environments. Environment-specific adapters are responsible for wiring up
 * TurndownService or any other HTML-to-Markdown implementation.
 */
export declare class MarkdownConverterCore {
    protected turndownService: any;
    protected readonly semanticSelectors: ISemanticSelectors;
    protected _isInitialized: boolean;
    protected readonly logger: ILogger;
    constructor(logger?: ILogger);
    /**
     * Called by environment-specific wrappers after assigning `turndownService`.
     */
    protected setupTurndownService(): void;
    private addMinimalCustomRules;
    convertToMarkdown(html: string, options?: IConversionOptions): IConversionResult;
    private preprocessHtml;
    private postprocessMarkdown;
}
export {};
//# sourceMappingURL=markdown-converter-core.d.ts.map