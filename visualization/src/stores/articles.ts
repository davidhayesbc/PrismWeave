/**
 * Pinia store for articles and filters
 */

import { articlesApi } from '@/services/api';
import type { ArticleDetail, ArticleSummary, Filters } from '@/types';
import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

export const useArticlesStore = defineStore('articles', () => {
  // State
  const articles = ref<ArticleSummary[]>([]);
  const currentArticle = ref<ArticleDetail | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Filters
  const filters = ref<Filters>({
    topics: [],
    searchQuery: '',
    ageRange: null,
    tags: [],
  });

  // Computed
  const filteredArticles = computed(() => {
    let result = articles.value;

    // Filter by topics
    if (filters.value.topics.length > 0) {
      result = result.filter(
        (article) => article.topic && filters.value.topics.includes(article.topic),
      );
    }

    // Filter by tags
    if (filters.value.tags.length > 0) {
      result = result.filter((article) =>
        filters.value.tags.some((tag) => article.tags.includes(tag)),
      );
    }

    // Filter by search query
    if (filters.value.searchQuery) {
      const query = filters.value.searchQuery.toLowerCase();
      result = result.filter(
        (article) =>
          article.title.toLowerCase().includes(query) ||
          article.excerpt.toLowerCase().includes(query) ||
          article.tags.some((tag) => tag.toLowerCase().includes(query)),
      );
    }

    // Filter by age range (in days)
    if (filters.value.ageRange) {
      const now = Date.now();
      const [minDays, maxDays] = filters.value.ageRange;
      result = result.filter((article) => {
        const age = (now - new Date(article.created_at).getTime()) / (1000 * 60 * 60 * 24);
        return age >= minDays && age <= maxDays;
      });
    }

    return result;
  });

  const availableTopics = computed(() => {
    const topics = new Set<string>();
    articles.value.forEach((article) => {
      if (article.topic) topics.add(article.topic);
    });
    return Array.from(topics).sort();
  });

  const availableTags = computed(() => {
    const tags = new Set<string>();
    articles.value.forEach((article) => {
      article.tags.forEach((tag) => tags.add(tag));
    });
    return Array.from(tags).sort();
  });

  // Actions
  async function fetchArticles() {
    loading.value = true;
    error.value = null;
    try {
      articles.value = await articlesApi.getArticles();
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch articles';
      console.error('Error fetching articles:', e);
    } finally {
      loading.value = false;
    }
  }

  async function fetchArticle(id: string) {
    loading.value = true;
    error.value = null;
    try {
      currentArticle.value = await articlesApi.getArticle(id);
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch article';
      console.error('Error fetching article:', e);
    } finally {
      loading.value = false;
    }
  }

  async function updateArticle(id: string, updates: Partial<ArticleDetail>) {
    loading.value = true;
    error.value = null;
    try {
      currentArticle.value = await articlesApi.updateArticle(id, updates);
      // Update in list
      const index = articles.value.findIndex((a) => a.id === id);
      if (index !== -1) {
        articles.value[index] = { ...articles.value[index], ...updates };
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update article';
      console.error('Error updating article:', e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function deleteArticle(id: string) {
    loading.value = true;
    error.value = null;
    try {
      await articlesApi.deleteArticle(id);
      articles.value = articles.value.filter((a) => a.id !== id);
      if (currentArticle.value?.id === id) {
        currentArticle.value = null;
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete article';
      console.error('Error deleting article:', e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function rebuildVisualization() {
    loading.value = true;
    error.value = null;
    try {
      const response = await articlesApi.rebuildVisualization();
      await fetchArticles(); // Refresh articles after rebuild
      return response;
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to rebuild visualization';
      console.error('Error rebuilding visualization:', e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  function setFilters(newFilters: Partial<Filters>) {
    filters.value = { ...filters.value, ...newFilters };
  }

  function clearFilters() {
    filters.value = {
      topics: [],
      searchQuery: '',
      ageRange: null,
      tags: [],
    };
  }

  return {
    // State
    articles,
    currentArticle,
    loading,
    error,
    filters,
    // Computed
    filteredArticles,
    availableTopics,
    availableTags,
    // Actions
    fetchArticles,
    fetchArticle,
    updateArticle,
    deleteArticle,
    rebuildVisualization,
    setFilters,
    clearFilters,
  };
});
