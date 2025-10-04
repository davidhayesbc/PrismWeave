// Shared type definitions for PrismWeave components
// These interfaces are consumed by both the browser extension and the CLI.
// Keep the definitions minimal and environment-agnostic so they can be reused
// across different runtimes without additional dependencies.

export interface IDocumentMetadata {
  title: string;
  url: string;
  captureDate: string;
  tags: string[];
  author?: string;
  wordCount?: number;
  estimatedReadingTime?: number;
  description?: string;
  publishedDate?: string;
  language?: string;
}

export interface IImageAsset {
  originalUrl: string;
  localPath: string;
  filename: string;
  size: number;
  mimeType: string;
}

export interface IGitHubSettings {
  token: string;
  repository: string;
  branch?: string;
}

export interface IFileOperationResult {
  success: boolean;
  filePath?: string;
  error?: string;
  size?: number;
  sha?: string;
  url?: string;
}
