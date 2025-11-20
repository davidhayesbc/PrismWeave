<template>
  <div class="map-container">
    <aside class="sidebar">
      <h2>Filters</h2>

      <div class="filter-section">
        <label>Search</label>
        <input
          type="search"
          v-model="searchQuery"
          placeholder="Search articles..."
          @input="updateFilters"
        />
      </div>

      <div class="filter-section">
        <label>Topics</label>
        <div class="checkbox-group">
          <label v-for="topic in store.availableTopics" :key="topic" class="checkbox-label">
            <input
              type="checkbox"
              :value="topic"
              v-model="selectedTopics"
              @change="updateFilters"
            />
            {{ topic }}
          </label>
        </div>
      </div>

      <div class="filter-section">
        <label>Tags</label>
        <select v-model="selectedTags" multiple @change="updateFilters" class="tags-select">
          <option v-for="tag in store.availableTags" :key="tag" :value="tag">
            {{ tag }}
          </option>
        </select>
      </div>

      <div class="filter-section">
        <button @click="clearFilters" class="secondary">Clear Filters</button>
      </div>

      <div class="stats">
        <p><strong>Total:</strong> {{ store.articles.length }}</p>
        <p><strong>Visible:</strong> {{ store.filteredArticles.length }}</p>
      </div>
    </aside>

    <div class="visualization-area">
      <div v-if="store.loading" class="loading">Loading articles...</div>
      <div v-else-if="store.error" class="error">{{ store.error }}</div>
      <svg ref="svgRef" class="visualization-svg"></svg>
      <div v-if="tooltip.visible" class="tooltip" :style="tooltipStyle">
        <h3>{{ tooltip.article?.title }}</h3>
        <p class="excerpt">{{ tooltip.article?.excerpt }}</p>
        <div class="meta">
          <span v-if="tooltip.article?.topic" class="topic">{{ tooltip.article.topic }}</span>
          <span class="tags">{{ tooltip.article?.tags.join(', ') }}</span>
        </div>
        <div class="stats-line">
          <span>{{ tooltip.article?.word_count }} words</span>
          <span>{{ formatDate(tooltip.article?.created_at) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useArticlesStore } from '@/stores/articles';
import type { ArticleSummary } from '@/types';
import * as d3 from 'd3';
import { computed, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const store = useArticlesStore();

const svgRef = ref<SVGSVGElement | null>(null);
const searchQuery = ref('');
const selectedTopics = ref<string[]>([]);
const selectedTags = ref<string[]>([]);

const tooltip = ref<{
  visible: boolean;
  article: ArticleSummary | null;
  x: number;
  y: number;
}>({
  visible: false,
  article: null,
  x: 0,
  y: 0,
});

const tooltipStyle = computed(() => ({
  left: `${tooltip.value.x}px`,
  top: `${tooltip.value.y}px`,
}));

function updateFilters() {
  store.setFilters({
    searchQuery: searchQuery.value,
    topics: selectedTopics.value,
    tags: selectedTags.value,
  });
  renderVisualization();
}

function clearFilters() {
  searchQuery.value = '';
  selectedTopics.value = [];
  selectedTags.value = [];
  store.clearFilters();
  renderVisualization();
}

function formatDate(dateStr: string | undefined): string {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  const now = new Date();
  const days = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
  if (days === 0) return 'Today';
  if (days === 1) return 'Yesterday';
  if (days < 30) return `${days} days ago`;
  if (days < 365) return `${Math.floor(days / 30)} months ago`;
  return `${Math.floor(days / 365)} years ago`;
}

function renderVisualization() {
  if (!svgRef.value) return;

  const articles = store.filteredArticles.filter((a) => a.x !== undefined && a.y !== undefined);
  if (articles.length === 0) return;

  const svg = d3.select(svgRef.value);
  svg.selectAll('*').remove();

  const width = svgRef.value.clientWidth;
  const height = svgRef.value.clientHeight;

  // Find coordinate bounds
  const xExtent = d3.extent(articles, (d) => d.x!) as [number, number];
  const yExtent = d3.extent(articles, (d) => d.y!) as [number, number];

  // Add padding
  const padding = 50;
  const xScale = d3
    .scaleLinear()
    .domain(xExtent)
    .range([padding, width - padding]);

  const yScale = d3
    .scaleLinear()
    .domain(yExtent)
    .range([padding, height - padding]);

  // Color scale for topics
  const topics = Array.from(new Set(articles.map((a) => a.topic).filter(Boolean)));
  const colorScale = d3.scaleOrdinal(d3.schemeCategory10).domain(topics);

  // Size scale for word count
  const sizeScale = d3
    .scaleSqrt()
    .domain([0, d3.max(articles, (d) => d.word_count) || 1000])
    .range([4, 12]);

  // Opacity scale for age
  const now = Date.now();
  const ageScale = d3
    .scaleLinear()
    .domain([0, 365]) // 0 to 1 year
    .range([1, 0.4])
    .clamp(true);

  // Draw edges (if neighbors exist)
  const g = svg.append('g');

  articles.forEach((article) => {
    if (article.neighbors && article.neighbors.length > 0) {
      article.neighbors.forEach((neighborId) => {
        const neighbor = articles.find((a) => a.id === neighborId);
        if (neighbor && neighbor.x !== undefined && neighbor.y !== undefined) {
          g.append('line')
            .attr('x1', xScale(article.x!))
            .attr('y1', yScale(article.y!))
            .attr('x2', xScale(neighbor.x))
            .attr('y2', yScale(neighbor.y))
            .attr('stroke', '#ddd')
            .attr('stroke-width', 1)
            .attr('opacity', 0.3);
        }
      });
    }
  });

  // Draw nodes
  g.selectAll('circle')
    .data(articles)
    .enter()
    .append('circle')
    .attr('cx', (d) => xScale(d.x!))
    .attr('cy', (d) => yScale(d.y!))
    .attr('r', (d) => sizeScale(d.word_count))
    .attr('fill', (d) => (d.topic ? colorScale(d.topic) : '#999'))
    .attr('opacity', (d) => {
      const age = (now - new Date(d.created_at).getTime()) / (1000 * 60 * 60 * 24);
      return ageScale(age);
    })
    .attr('stroke', (d) => (d.read_status === 'read' ? '#333' : '#fff'))
    .attr('stroke-width', (d) => (d.read_status === 'read' ? 1 : 2))
    .style('cursor', 'pointer')
    .on('mouseenter', (event, d) => {
      tooltip.value = {
        visible: true,
        article: d,
        x: event.pageX + 10,
        y: event.pageY + 10,
      };
    })
    .on('mouseleave', () => {
      tooltip.value.visible = false;
    })
    .on('click', (_, d) => {
      router.push({ name: 'article', params: { id: d.id } });
    });

  // Add zoom behavior
  const zoom = d3
    .zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.5, 5])
    .on('zoom', (event) => {
      g.attr('transform', event.transform);
    });

  svg.call(zoom);
}

onMounted(async () => {
  await store.fetchArticles();
  renderVisualization();
});

watch(
  () => store.filteredArticles,
  () => {
    renderVisualization();
  },
);
</script>

<style scoped>
.map-container {
  display: flex;
  height: 100%;
}

.sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid #ddd;
  padding: 1.5rem;
  overflow-y: auto;
}

.sidebar h2 {
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.filter-section {
  margin-bottom: 1.5rem;
}

.filter-section label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #555;
}

.filter-section input[type='search'] {
  width: 100%;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 200px;
  overflow-y: auto;
  padding: 0.5rem;
  border: 1px solid #eee;
  border-radius: 4px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: normal;
  cursor: pointer;
}

.checkbox-label input {
  cursor: pointer;
}

.tags-select {
  width: 100%;
  height: 120px;
}

.stats {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.stats p {
  margin: 0.25rem 0;
  color: #666;
}

.visualization-area {
  flex: 1;
  position: relative;
  background: #fafafa;
}

.visualization-svg {
  width: 100%;
  height: 100%;
}

.tooltip {
  position: fixed;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 1rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  max-width: 300px;
  pointer-events: none;
  z-index: 1000;
}

.tooltip h3 {
  font-size: 1rem;
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
}

.tooltip .excerpt {
  font-size: 0.85rem;
  color: #666;
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
}

.tooltip .meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 0.5rem;
}

.tooltip .topic {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 3px;
  font-size: 0.75rem;
  font-weight: 600;
}

.tooltip .tags {
  font-size: 0.75rem;
  color: #999;
}

.tooltip .stats-line {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #999;
  padding-top: 0.5rem;
  border-top: 1px solid #eee;
}
</style>
