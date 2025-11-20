/**
 * API service for PrismWeave backend
 */

import type { ArticleDetail, ArticleSummary, RebuildResponse, UpdateArticleRequest } from '@/types';
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const articlesApi = {
  /**
   * Get list of all articles
   */
  async getArticles(): Promise<ArticleSummary[]> {
    const response = await apiClient.get<ArticleSummary[]>('/articles');
    return response.data;
  },

  /**
   * Get detailed article by ID
   */
  async getArticle(id: string): Promise<ArticleDetail> {
    const response = await apiClient.get<ArticleDetail>(`/articles/${encodeURIComponent(id)}`);
    return response.data;
  },

  /**
   * Update article
   */
  async updateArticle(id: string, updates: UpdateArticleRequest): Promise<ArticleDetail> {
    const response = await apiClient.put<ArticleDetail>(
      `/articles/${encodeURIComponent(id)}`,
      updates,
    );
    return response.data;
  },

  /**
   * Delete article
   */
  async deleteArticle(id: string): Promise<void> {
    await apiClient.delete(`/articles/${encodeURIComponent(id)}`);
  },

  /**
   * Rebuild visualization index
   */
  async rebuildVisualization(): Promise<RebuildResponse> {
    const response = await apiClient.post<RebuildResponse>('/visualization/rebuild');
    return response.data;
  },
};
