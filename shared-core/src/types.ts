export interface IDocumentMetadata {
  title: string;
  url: string;
  captureDate: string;
  tags: string[];
  author?: string;
  wordCount?: number;
  estimatedReadingTime?: number;
  description?: string;
  keywords?: string[];
  publishedDate?: string;
  language?: string;
  [key: string]: unknown;
}

export interface IImageAsset {
  originalUrl: string;
  localPath: string;
  filename: string;
  size: number;
  mimeType: string;
}

export interface IFileOperationResult {
  success: boolean;
  filePath?: string;
  error?: string;
  size?: number;
  sha?: string;
  url?: string;
}

export interface IGitHubSettings {
  token: string;
  repository: string;
  branch?: string;
}
