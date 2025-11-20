/**
 * Type definitions for PrismWeave articles and API responses
 */

export interface ArticleSummary {
  id: string;
  title: string;
  path: string;
  topic: string | null;
  tags: string[];
  created_at: string;
  updated_at: string;
  word_count: number;
  excerpt: string;
  read_status: string;
  x?: number;
  y?: number;
  neighbors?: string[];
}

export interface ArticleDetail extends ArticleSummary {
  content: string;
}

export interface UpdateArticleRequest {
  title?: string;
  topic?: string;
  tags?: string[];
  read_status?: string;
  content?: string;
}

export interface RebuildResponse {
  status: string;
  article_count: number;
  message: string;
}

export interface Filters {
  topics: string[];
  searchQuery: string;
  ageRange: [number, number] | null;
  tags: string[];
}
