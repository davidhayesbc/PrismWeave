#!/usr/bin/env node
interface ITestResult {
    url: string;
    timestamp: string;
    originalHtml: string;
    cleanedHtml: string;
    markdown: string;
    frontmatter: string;
    metadata: any;
    images: any[];
    stats: any;
    conversionTime: number;
}
interface ITestOptions {
    url: string;
    output?: string;
    format?: 'all' | 'markdown' | 'html';
    includeMetadata?: boolean;
    preserveFormatting?: boolean;
    generateFrontmatter?: boolean;
    verbose?: boolean;
}
declare class UrlTester {
    private converter;
    private outputDir;
    constructor(outputDir?: string);
    testUrl(options: ITestOptions): Promise<ITestResult>;
    private extractMetadata;
    private saveResults;
    private displayStats;
}
export { ITestOptions, ITestResult, UrlTester };
