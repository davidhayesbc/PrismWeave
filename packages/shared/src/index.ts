/**
 * @prismweave/shared
 * Shared utilities and types for PrismWeave components
 */

// Common types
export interface DocumentMetadata {
  title: string;
  url: string;
  domain: string;
  extractedAt: Date;
  tags?: string[];
}

export interface CaptureOptions {
  includeImages?: boolean;
  includeLinks?: boolean;
  cleanHtml?: boolean;
}

// Re-export utilities when implemented
export * from './utils';
