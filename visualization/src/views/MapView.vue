<template>
  <div class="map-container">
    <aside class="sidebar">
      <h2>Filters</h2>

      <div class="filter-section">
        <label>Graph</label>
        <div class="graph-controls">
          <div class="graph-control">
            <span class="graph-control-label">Link Distance</span>
            <input
              type="range"
              v-model.number="linkDistance"
              min="30"
              max="200"
              step="10"
              @input="renderVisualization"
            />
            <span class="range-value">{{ linkDistance }}</span>
          </div>

          <div class="graph-control">
            <span class="graph-control-label">Charge</span>
            <input
              type="range"
              v-model.number="chargeStrength"
              min="-300"
              max="-10"
              step="10"
              @input="renderVisualization"
            />
            <span class="range-value">{{ chargeStrength }}</span>
          </div>

          <label class="checkbox-label compact">
            <input type="checkbox" v-model="hideIsolated" @change="renderVisualization" />
            Hide isolated nodes
          </label>
        </div>
      </div>

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
        <p><strong>Links:</strong> {{ linkCount }}</p>
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
const linkDistance = ref(80);
const chargeStrength = ref(-100);
const linkCount = ref(0);
const hideIsolated = ref(true);

const COLLISION_PADDING = 8;
const MIN_RADIUS = 6;
const MAX_RADIUS = 24;
const MIN_LABEL_WIDTH = 210;
const MIN_LABEL_HEIGHT = 96;
const LABEL_WIDTH_FACTOR = 7.2;
const LABEL_HEIGHT_FACTOR = 3.9;
const LABEL_HORIZONTAL_PADDING = 16;
const LABEL_VERTICAL_PADDING = 22;

const COLOR_PALETTE = d3.schemeTableau10;
const NO_TOPIC_LABEL = 'No topic';

type SimulationNode = d3.SimulationNodeDatum & {
  article: ArticleSummary;
  width: number;
  height: number;
  collisionRadius: number;
};

type ForceLink = {
  source: SimulationNode;
  target: SimulationNode;
  strength: number;
};

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

function formatShortDate(dateStr: string | undefined): string {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

const TITLE_LINE_HEIGHT = 1.1;

function renderWrappedTitle(
  element: SVGTextElement,
  x: number,
  y: number,
  maxWidth: number,
  title: string,
) {
  const text = d3.select(element);
  text.selectAll('*').remove();
  text.attr('x', x).attr('y', y);

  const words = title.split(/\s+/).filter(Boolean);
  if (words.length === 0) {
    text.text('');
    return;
  }

  const measureSpan = text.append('tspan').attr('opacity', 0).text('');
  const lines: string[] = [];
  const remainingWords = [...words];

  while (remainingWords.length > 0 && lines.length < 2) {
    let line = '';
    while (remainingWords.length > 0) {
      const candidate = line ? `${line} ${remainingWords[0]}` : remainingWords[0];
      measureSpan.text(candidate);
      const width = measureSpan.node()?.getComputedTextLength() || 0;

      if (width <= maxWidth || line.length === 0) {
        line = candidate;
        remainingWords.shift();
      } else {
        break;
      }
    }

    if (!line) {
      line = remainingWords.shift() ?? '';
    }

    lines.push(line.trim());
  }

  if (remainingWords.length > 0 && lines.length > 0) {
    lines[lines.length - 1] = appendEllipsis(lines[lines.length - 1], maxWidth, measureSpan);
  }

  measureSpan.remove();

  lines.forEach((line, index) => {
    text
      .append('tspan')
      .attr('x', x)
      .attr('dy', index === 0 ? 0 : `${TITLE_LINE_HEIGHT}em`)
      .text(line);
  });
}

function appendEllipsis(
  line: string,
  maxWidth: number,
  measureSpan: d3.Selection<SVGTSpanElement, unknown, null, undefined>,
): string {
  let candidate = line.trim();
  candidate = candidate ? `${candidate}…` : '…';
  measureSpan.text(candidate);

  if ((measureSpan.node()?.getComputedTextLength() || 0) <= maxWidth) {
    return candidate;
  }

  const words = line.split(/\s+/);
  while (words.length > 0) {
    words.pop();
    const attempt = words.length > 0 ? `${words.join(' ')}…` : '…';
    measureSpan.text(attempt);
    if ((measureSpan.node()?.getComputedTextLength() || 0) <= maxWidth || words.length === 0) {
      return attempt;
    }
  }

  return '…';
}

function getTopicLabel(article: ArticleSummary): string {
  return article.topic?.trim() ? article.topic : NO_TOPIC_LABEL;
}

function renderVisualization() {
  if (!svgRef.value) return;
  const filtered = store.filteredArticles;

  const connectedIds = new Set<string>();
  filtered.forEach((article) => {
    if (!article.neighbors) return;
    connectedIds.add(article.id);
    article.neighbors.forEach((neighborId) => connectedIds.add(neighborId));
  });

  const graphArticles = hideIsolated.value
    ? filtered.filter((article) => connectedIds.has(article.id))
    : filtered;

  if (graphArticles.length === 0) {
    d3.select(svgRef.value).selectAll('*').remove();
    linkCount.value = 0;
    return;
  }

  renderForceLayout(graphArticles);
}

function renderForceLayout(articles: ArticleSummary[]) {
  if (!svgRef.value) return;

  const svg = d3.select(svgRef.value);
  svg.selectAll('*').remove();

  const width = svgRef.value.clientWidth;
  const height = svgRef.value.clientHeight;

  // Build node lookup map
  const nodeMap = new Map<string, SimulationNode>();

  // Size scale for word count
  const sizeScale = d3
    .scaleSqrt()
    .domain([0, d3.max(articles, (d) => d.word_count) || 1000])
    .range([MIN_RADIUS, MAX_RADIUS]);

  // Topic-based coloring (more interpretable than embedding clusters)
  const topics = Array.from(new Set(articles.map(getTopicLabel))).sort();
  const colorScale = d3.scaleOrdinal<string, string>(COLOR_PALETTE).domain(topics);

  // Opacity scale for age
  const now = Date.now();
  const ageScale = d3.scaleLinear().domain([0, 365]).range([1, 0.4]).clamp(true);

  // Create nodes
  const nodes: SimulationNode[] = articles.map((article) => {
    const baseSize = sizeScale(article.word_count);
    const width = Math.max(MIN_LABEL_WIDTH, baseSize * LABEL_WIDTH_FACTOR);
    const height = Math.max(MIN_LABEL_HEIGHT, baseSize * LABEL_HEIGHT_FACTOR);
    const node: SimulationNode = {
      article,
      x: width / 2 + Math.random() * (width - width),
      y: height / 2 + Math.random() * (height - height),
      width,
      height,
      collisionRadius: Math.max(width, height) / 2,
    };
    nodeMap.set(article.id, node);
    return node;
  });

  // Create links from neighbor data (computed by backend)
  const links: ForceLink[] = [];
  const linkSet = new Set<string>();

  articles.forEach((article) => {
    if (!article.neighbors || article.neighbors.length === 0) return;

    const sourceNode = nodeMap.get(article.id);
    if (!sourceNode) return;

    // Create links to pre-computed neighbors
    article.neighbors.forEach((neighborId) => {
      const targetNode = nodeMap.get(neighborId);
      if (targetNode) {
        const linkId = [article.id, neighborId].sort().join('-');
        if (!linkSet.has(linkId)) {
          linkSet.add(linkId);
          links.push({
            source: sourceNode,
            target: targetNode,
            strength: 1,
          });
        }
      }
    });
  });

  linkCount.value = links.length;

  // Create force simulation
  const simulation = d3
    .forceSimulation(nodes)
    .force(
      'link',
      d3
        .forceLink<SimulationNode, ForceLink>(links)
        .id((d) => d.article.id)
        .distance(linkDistance.value)
        .strength(0.3),
    )
    .force('charge', d3.forceManyBody().strength(chargeStrength.value))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force(
      'collide',
      d3.forceCollide<SimulationNode>((d) => d.collisionRadius + COLLISION_PADDING),
    );

  const g = svg.append('g');

  // Draw links
  const linkElements = g
    .selectAll('line.link')
    .data(links)
    .enter()
    .append('line')
    .attr('class', 'link')
    .attr('stroke', '#999')
    .attr('stroke-opacity', 0.4)
    .attr('stroke-width', 1.5);

  // Draw nodes
  const nodeGroups = g
    .selectAll('g.article-node')
    .data(nodes)
    .enter()
    .append('g')
    .attr('class', 'article-node')
    .style('cursor', 'pointer')
    .on('mouseenter', (event, d) => {
      tooltip.value = {
        visible: true,
        article: d.article,
        x: event.pageX + 10,
        y: event.pageY + 10,
      };
      // Highlight connected nodes
      d3.selectAll('line.link')
        .attr('stroke-opacity', (link) =>
          (link as ForceLink).source === d || (link as ForceLink).target === d ? 1 : 0.1,
        )
        .attr('stroke-width', (link) =>
          (link as ForceLink).source === d || (link as ForceLink).target === d ? 3 : 1.5,
        );
    })
    .on('mouseleave', () => {
      tooltip.value.visible = false;
      d3.selectAll('line.link').attr('stroke-opacity', 0.4).attr('stroke-width', 1.5);
    })
    .on('click', (_, d) => {
      router.push({ name: 'article', params: { id: d.article.id } });
    })
    .call(
      d3
        .drag<SVGGElement, SimulationNode>()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }),
    );

  nodeGroups
    .append('rect')
    .attr('width', (d) => d.width)
    .attr('height', (d) => d.height)
    .attr('rx', 12)
    .attr('ry', 12)
    .attr('x', (d) => -d.width / 2)
    .attr('y', (d) => -d.height / 2)
    .attr('fill', (d) => colorScale(getTopicLabel(d.article)))
    .attr('opacity', (d) => {
      const age = (now - new Date(d.article.created_at).getTime()) / (1000 * 60 * 60 * 24);
      return ageScale(age);
    })
    .attr('stroke', (d) => (d.article.read_status === 'read' ? '#2b2b2b' : '#fff'))
    .attr('stroke-width', (d) => (d.article.read_status === 'read' ? 1 : 2));

  nodeGroups
    .append('text')
    .attr('class', 'node-title')
    .each(function (d) {
      renderWrappedTitle(
        this as SVGTextElement,
        -d.width / 2 + LABEL_HORIZONTAL_PADDING,
        -d.height / 2 + LABEL_VERTICAL_PADDING,
        d.width - LABEL_HORIZONTAL_PADDING * 2,
        d.article.title,
      );
    });

  nodeGroups
    .append('text')
    .attr('class', 'node-date')
    .attr('x', 0)
    .attr('y', (d) => d.height / 2 - 12)
    .attr('text-anchor', 'middle')
    .text((d) => formatShortDate(d.article.created_at));

  // Update positions on tick
  simulation.on('tick', () => {
    linkElements
      .attr('x1', (d) => (d.source as SimulationNode).x ?? 0)
      .attr('y1', (d) => (d.source as SimulationNode).y ?? 0)
      .attr('x2', (d) => (d.target as SimulationNode).x ?? 0)
      .attr('y2', (d) => (d.target as SimulationNode).y ?? 0);

    nodeGroups.attr('transform', (d) => `translate(${d.x ?? 0}, ${d.y ?? 0})`);
  });

  // Add zoom behavior
  const zoom = d3
    .zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.2, 4])
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

.graph-controls {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.75rem;
  border: 1px solid #eee;
  border-radius: 6px;
  background: #fafafa;
}

.graph-control {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  column-gap: 0.5rem;
  row-gap: 0.35rem;
}

.graph-control-label {
  grid-column: 1 / -1;
  font-size: 0.85rem;
  color: #555;
  font-weight: 600;
}

.filter-section input[type='range'] {
  width: calc(100% - 50px);
  margin-right: 0.5rem;
}

.range-value {
  font-size: 0.85rem;
  color: #666;
  font-weight: 600;
  min-width: 40px;
  display: inline-block;
  text-align: right;
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

.checkbox-label.compact {
  margin-top: 0.25rem;
  font-size: 0.85rem;
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

.article-node text {
  font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, sans-serif;
  pointer-events: none;
}

.article-node .node-title {
  font-size: 0.7rem;
  font-weight: 600;
  fill: #fff;
}

.article-node .node-date {
  font-size: 0.62rem;
  fill: rgba(255, 255, 255, 0.9);
  text-anchor: middle;
}

line.link {
  transition:
    stroke-opacity 0.2s,
    stroke-width 0.2s;
}
</style>
