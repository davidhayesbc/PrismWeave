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

  taxonomy_cluster_id?: string | null;
  taxonomy_category_id?: string | null;
  taxonomy_category?: string | null;
  taxonomy_subcategory_id?: string | null;
  taxonomy_subcategory?: string | null;
  taxonomy_tag_assignments?: TaxonomyTagAssignment[];
  taxonomy_tags?: string[];
}

export interface TaxonomyTagAssignment {
  id: string;
  name: string;
  confidence: number;
}

export interface ArticleDetail extends ArticleSummary {
  content: string;
}

export interface UpdateArticleRequest {
  title?: string;
  topic?: string | null;
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
  categories: string[];
  searchQuery: string;
  ageRange: [number, number] | null;
  tagValues: string[];
}

export interface OptionItem {
  value: string;
  label: string;
}
