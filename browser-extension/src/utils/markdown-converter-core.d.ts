import { IDocumentMetadata, IImageAsset } from '../types/index.js';
interface IConversionOptions {
    preserveFormatting?: boolean;
    includeMetadata?: boolean;
    generateFrontmatter?: boolean;
    customRules?: Record<string, unknown>;
    headingStyle?: 'atx' | 'setext';
    bulletListMarker?: '-' | '*' | '+';
    codeBlockStyle?: 'fenced' | 'indented';
    linkStyle?: 'inlined' | 'referenced';
}
interface IConversionResult {
    markdown: string;
    frontmatter: string;
    metadata: IDocumentMetadata;
    images: IImageAsset[];
    wordCount: number;
}
interface ITurndownService {
    turndown(html: string): string;
    addRule(key: string, rule: any): void;
    remove(filter: string | string[]): void;
    use(plugin: any): void;
}
interface ISemanticSelectors {
    callouts: string[];
    quotes: string[];
    highlights: string[];
    captions: string[];
    metadata: string[];
    codeElements: string[];
}
export declare class MarkdownConverterCore {
    protected turndownService: ITurndownService | null;
    protected readonly semanticSelectors: ISemanticSelectors;
    protected _isInitialized: boolean;
    constructor();
    protected setupTurndownService(): void;
    private addAllCustomRules;
    private cleanCodeContent;
    private makeAbsoluteUrl;
    private getListItemContent;
    convertToMarkdown(html: string, options?: IConversionOptions): IConversionResult;
    private preprocessHtml;
    private postprocessMarkdown;
    private extractMetadata;
    private generateFrontmatter;
    private extractImages;
    private calculateWordCount;
    get isInitialized(): boolean;
}
export { IConversionOptions, IConversionResult };
