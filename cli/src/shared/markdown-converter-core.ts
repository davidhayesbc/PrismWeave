import { MarkdownConverterCore as BaseMarkdownConverterCore } from '@prismweave/shared-core/markdown';
import { createConsoleLogger } from '@prismweave/shared-core/util';
import TurndownService from 'turndown';

export { MarkdownConverterCore } from '@prismweave/shared-core/markdown';
export type { IConversionOptions, IConversionResult } from '@prismweave/shared-core/markdown';

/**
 * CLI-specific adapter that wires TurndownService into the shared markdown
 * conversion core.
 */
export class MarkdownConverter extends BaseMarkdownConverterCore {
  constructor() {
    super(createConsoleLogger('CLI-MarkdownConverter'));
    this.initializeTurndown();
  }

  private initializeTurndown(): void {
    const options = {
      headingStyle: 'atx' as const,
      bulletListMarker: '-' as const,
      codeBlockStyle: 'fenced' as const,
      emDelimiter: '*' as const,
      strongDelimiter: '**' as const,
      linkStyle: 'inlined' as const,
      linkReferenceStyle: 'full' as const,
      preformattedCode: true,
    };

    this.turndownService = new TurndownService(options);
    this.setupTurndownService();
    this._isInitialized = true;
  }
}
