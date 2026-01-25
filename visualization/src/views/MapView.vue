<template>
  <div class="map-container">
    <aside class="sidebar">
      <div class="sidebar-actions">
        <button @click="handleRebuild" :disabled="rebuilding" class="pw-btn pw-btn-primary">
          {{ rebuilding ? 'Rebuilding...' : 'Rebuild Index' }}
        </button>
      </div>

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
        </div>
      </div>

      <div class="filter-section">
        <label>Search</label>
        <input
          type="search"
          v-model="searchQuery"
          placeholder="Search articles..."
          @input="updateFiltersDebounced"
        />
      </div>

      <div class="filter-section">
        <label>Categories</label>
        <div class="checkbox-group">
          <label
            v-for="category in store.availableCategories"
            :key="category.value"
            class="checkbox-label"
          >
            <input
              type="checkbox"
              :value="category.value"
              v-model="selectedCategories"
              @change="updateFiltersImmediate"
            />
            <span
              class="category-swatch category-swatch--filter"
              :style="{ backgroundColor: getCategoryColor(category.value) }"
              aria-hidden="true"
            ></span>
            {{ category.label }}
          </label>
        </div>
      </div>

      <div class="filter-section">
        <label>Tags</label>
        <select
          v-model="selectedTagValues"
          multiple
          @change="updateFiltersImmediate"
          class="tags-select"
        >
          <option v-for="tag in store.availableTags" :key="tag.value" :value="tag.value">
            {{ tag.label }} ({{ tag.count }})
          </option>
        </select>
      </div>

      <div class="filter-section">
        <label>Clustering</label>
        <div class="checkbox-group">
          <label class="checkbox-label">
            <input type="radio" value="taxonomy" v-model="linkMode" @change="renderVisualization" />
            Taxonomy clusters
          </label>
          <label class="checkbox-label">
            <input
              type="radio"
              value="neighbors"
              v-model="linkMode"
              @change="renderVisualization"
            />
            Nearest neighbors
          </label>
        </div>
      </div>

      <div class="filter-section">
        <div class="matches-header">
          <label class="matches-title">Top matches</label>
          <select v-model="matchSort" class="matches-sort" @change="renderVisualization">
            <option value="recent">Recent</option>
            <option value="unread">Unread first</option>
            <option value="long">Longest</option>
          </select>
        </div>

        <div class="matches-subtitle">
          Showing {{ topMatches.length }} of {{ graphArticles.length }} graph nodes
        </div>

        <div class="matches-list">
          <button
            v-for="article in topMatches"
            :key="article.id"
            class="match-item"
            @click="openArticle(article.id)"
            @mouseenter="highlightArticle(article.id)"
            @mouseleave="highlightArticle(null)"
          >
            <div class="match-title" :title="article.title">{{ article.title }}</div>
            <div class="match-meta">
              <span class="match-topic">
                <span
                  class="category-swatch category-swatch--tiny"
                  :style="{ backgroundColor: getCategoryColor(getCategoryLabel(article)) }"
                  aria-hidden="true"
                ></span>
                <span class="match-topic-text">
                  {{ article.taxonomy_category || article.topic || 'No category' }}
                </span>
              </span>
              <span class="match-date">{{ formatShortDate(article.updated_at) }}</span>
            </div>
          </button>
        </div>
      </div>

      <div class="filter-section">
        <button @click="clearFilters" class="pw-btn pw-btn-secondary">Clear Filters</button>
      </div>

      <div class="stats">
        <p><strong>Total:</strong> {{ store.articles.length }}</p>
        <p><strong>Visible:</strong> {{ store.filteredArticles.length }}</p>
        <p><strong>Graph nodes:</strong> {{ graphArticles.length }}</p>
        <p><strong>Links:</strong> {{ linkCount }}</p>
      </div>
    </aside>

    <div class="visualization-area">
      <div v-if="store.loading" class="loading">Loading articles...</div>
      <div v-else-if="store.error" class="error">{{ store.error }}</div>
      <div v-else-if="graphArticles.length === 0" class="empty">No articles to display.</div>
      <svg ref="svgRef" class="visualization-svg"></svg>
      <div v-if="tooltip.visible" class="tooltip" :style="tooltipStyle">
        <h3>{{ tooltip.article?.title }}</h3>
        <p class="excerpt">{{ tooltip.article?.excerpt }}</p>
        <div class="meta">
          <span v-if="tooltip.article?.taxonomy_category || tooltip.article?.topic" class="topic">
            <span
              class="category-swatch category-swatch--tiny"
              :style="{
                backgroundColor: tooltip.article
                  ? getCategoryColor(getCategoryLabel(tooltip.article))
                  : NO_CATEGORY_COLOR,
              }"
              aria-hidden="true"
            ></span>
            {{ tooltip.article?.taxonomy_category || tooltip.article?.topic }}
          </span>
          <span class="tags">
            {{
              (tooltip.article?.taxonomy_tags?.length
                ? tooltip.article?.taxonomy_tags
                : ['None']
              ).join(', ')
            }}
          </span>
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
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const store = useArticlesStore();
const rebuilding = ref(false);
const linkDistance = ref(80);
const chargeStrength = ref(-100);
const linkCount = ref(0);
// Always show all nodes for the current filters.

type LinkMode = 'taxonomy' | 'neighbors';
const linkMode = ref<LinkMode>('taxonomy');

const COLLISION_PADDING = 8;
const MIN_RADIUS = 6;
const MAX_RADIUS = 24;
const MIN_LABEL_WIDTH = 210;
const MIN_LABEL_HEIGHT = 96;
const LABEL_WIDTH_FACTOR = 7.2;
const LABEL_HEIGHT_FACTOR = 3.9;
const LABEL_HORIZONTAL_PADDING = 16;
const LABEL_VERTICAL_PADDING = 22;

const CATEGORY_COLOR_PALETTE: string[] = Array.from(
  new Set([...(d3.schemeTableau10 as string[]), ...(d3.schemeSet3 as string[])]),
);
const NO_CATEGORY_COLOR = '#6c757d';
const NO_TOPIC_LABEL = 'No category';

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
const selectedCategories = ref<string[]>([]);
const selectedTagValues = ref<string[]>([]);

type MatchSort = 'recent' | 'unread' | 'long';
const matchSort = ref<MatchSort>('recent');
const highlightedArticleId = ref<string | null>(null);

let renderEpoch = 0;
const ZOOM_EXTENT: [number, number] = [0.2, 4];
const FIT_PADDING = 70;
const FIT_DELAY_MS = 220;

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

const FILTER_DEBOUNCE_MS = 250;
let filterDebounceTimer: number | null = null;

function applyFilters() {
  store.setFilters({
    searchQuery: searchQuery.value,
    topics: [],
    categories: selectedCategories.value,
    tagValues: selectedTagValues.value,
  });
  renderVisualization();
}

function updateFiltersImmediate() {
  if (filterDebounceTimer) {
    window.clearTimeout(filterDebounceTimer);
    filterDebounceTimer = null;
  }
  applyFilters();
}

function updateFiltersDebounced() {
  if (filterDebounceTimer) {
    window.clearTimeout(filterDebounceTimer);
  }

  filterDebounceTimer = window.setTimeout(() => {
    filterDebounceTimer = null;
    applyFilters();
  }, FILTER_DEBOUNCE_MS);
}

function clearFilters() {
  searchQuery.value = '';
  selectedCategories.value = [];
  selectedTagValues.value = [];
  store.clearFilters();
  renderVisualization();
}

async function handleRebuild() {
  if (rebuilding.value) return;
  rebuilding.value = true;
  try {
    const response = await store.rebuildVisualization();
    store.setNotice(response.message || 'Visualization index rebuilt successfully');
  } catch (e) {
    console.error('Rebuild failed:', e);
    store.setError('Failed to rebuild visualization index.');
  } finally {
    rebuilding.value = false;
  }
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

function getCategoryLabel(article: ArticleSummary): string {
  // Top-level category is taxonomy_category (with topic as a fallback).
  const label = article.taxonomy_category || article.topic;
  return label && label.trim() ? label : NO_TOPIC_LABEL;
}

function hashString(input: string): number {
  // Deterministic, fast non-crypto hash.
  let hash = 5381;
  for (let i = 0; i < input.length; i += 1) {
    hash = (hash * 33) ^ input.charCodeAt(i);
  }
  return hash >>> 0;
}

function getCategoryColor(category: string): string {
  const normalized = category.trim() || NO_TOPIC_LABEL;
  if (normalized === NO_TOPIC_LABEL) return NO_CATEGORY_COLOR;
  const index = hashString(normalized) % CATEGORY_COLOR_PALETTE.length;
  return CATEGORY_COLOR_PALETTE[index] ?? NO_CATEGORY_COLOR;
}

const graphArticles = computed(() => store.filteredArticles);

const topMatches = computed(() => {
  const articles = [...graphArticles.value];

  switch (matchSort.value) {
    case 'unread':
      articles.sort((a, b) => {
        const aUnread = a.read_status !== 'read';
        const bUnread = b.read_status !== 'read';
        if (aUnread !== bUnread) return aUnread ? -1 : 1;
        return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
      });
      break;

    case 'long':
      articles.sort((a, b) => (b.word_count || 0) - (a.word_count || 0));
      break;

    case 'recent':
    default:
      articles.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
      break;
  }

  return articles.slice(0, 20);
});

function openArticle(id: string) {
  router.push({ name: 'article', params: { id } });
}

function highlightArticle(id: string | null) {
  highlightedArticleId.value = id;
  applyHighlight();
}

function applyHighlight() {
  if (!svgRef.value) return;

  const selectedId = highlightedArticleId.value;
  const svg = d3.select(svgRef.value);
  const nodes = svg.selectAll<SVGGElement, unknown>('g.article-node');
  const links = svg.selectAll<SVGLineElement, unknown>('line.link');

  if (!selectedId) {
    nodes.classed('is-dimmed', false).classed('is-highlighted', false);
    links.classed('is-dimmed', false).classed('is-highlighted', false);
    return;
  }

  const connected = new Set<string>([selectedId]);
  if (linkMode.value === 'taxonomy') {
    const selected = graphArticles.value.find((a) => a.id === selectedId);
    const clusterId = selected?.taxonomy_cluster_id;
    if (clusterId) {
      graphArticles.value.forEach((article) => {
        if (article.taxonomy_cluster_id === clusterId) {
          connected.add(article.id);
        }
      });
    }
  } else {
    graphArticles.value.forEach((article) => {
      if (article.id !== selectedId) return;
      (article.neighbors || []).forEach((neighborId) => connected.add(neighborId));
    });
  }

  nodes
    .classed('is-highlighted', function () {
      const id = d3.select(this).attr('data-article-id');
      return id === selectedId;
    })
    .classed('is-dimmed', function () {
      const id = d3.select(this).attr('data-article-id');
      return !!id && !connected.has(id);
    });

  links
    .classed('is-highlighted', function () {
      const sourceId = d3.select(this).attr('data-source-id');
      const targetId = d3.select(this).attr('data-target-id');
      return sourceId === selectedId || targetId === selectedId;
    })
    .classed('is-dimmed', function () {
      const sourceId = d3.select(this).attr('data-source-id');
      const targetId = d3.select(this).attr('data-target-id');
      if (!sourceId || !targetId) return false;
      return !connected.has(sourceId) && !connected.has(targetId);
    });
}

function fitGraphToView(params: {
  svg: d3.Selection<SVGSVGElement, unknown, null, undefined>;
  zoom: d3.ZoomBehavior<SVGSVGElement, unknown>;
  nodes: SimulationNode[];
  width: number;
  height: number;
}) {
  const { svg, zoom, nodes, width, height } = params;

  if (width <= 0 || height <= 0) return;
  if (nodes.length === 0) return;

  let minX = Number.POSITIVE_INFINITY;
  let minY = Number.POSITIVE_INFINITY;
  let maxX = Number.NEGATIVE_INFINITY;
  let maxY = Number.NEGATIVE_INFINITY;

  nodes.forEach((node) => {
    const x = node.x ?? 0;
    const y = node.y ?? 0;
    const halfW = node.width / 2;
    const halfH = node.height / 2;

    minX = Math.min(minX, x - halfW);
    maxX = Math.max(maxX, x + halfW);
    minY = Math.min(minY, y - halfH);
    maxY = Math.max(maxY, y + halfH);
  });

  if (
    !Number.isFinite(minX) ||
    !Number.isFinite(minY) ||
    !Number.isFinite(maxX) ||
    !Number.isFinite(maxY)
  ) {
    return;
  }

  const boundsWidth = Math.max(1, maxX - minX + FIT_PADDING * 2);
  const boundsHeight = Math.max(1, maxY - minY + FIT_PADDING * 2);

  const scale = Math.max(
    ZOOM_EXTENT[0],
    Math.min(ZOOM_EXTENT[1], 0.96 * Math.min(width / boundsWidth, height / boundsHeight)),
  );

  const centerX = (minX + maxX) / 2;
  const centerY = (minY + maxY) / 2;
  const translateX = width / 2 - scale * centerX;
  const translateY = height / 2 - scale * centerY;

  svg
    .transition()
    .duration(250)
    .call(zoom.transform, d3.zoomIdentity.translate(translateX, translateY).scale(scale));
}

function renderVisualization() {
  if (!svgRef.value) return;

  // If the SVG hasn't been laid out yet, wait for the next frame.
  // This prevents rendering a blank graph due to 0x0 dimensions on first mount.
  if (svgRef.value.clientWidth <= 0 || svgRef.value.clientHeight <= 0) {
    window.requestAnimationFrame(() => renderVisualization());
    return;
  }

  const articles = graphArticles.value;

  if (articles.length === 0) {
    d3.select(svgRef.value).selectAll('*').remove();
    linkCount.value = 0;
    return;
  }

  renderForceLayout(articles);
  applyHighlight();
}

function renderForceLayout(articles: ArticleSummary[]) {
  if (!svgRef.value) return;

  const epoch = (renderEpoch += 1);

  const svg = d3.select(svgRef.value);
  svg.selectAll('*').remove();

  const svgWidth = svgRef.value.clientWidth;
  const svgHeight = svgRef.value.clientHeight;

  // Ensure the SVG's internal coordinate system matches its displayed size.
  // Without this, elements can be positioned outside the default 300x150 viewport and get clipped.
  svg.attr('viewBox', `0 0 ${Math.max(1, svgWidth)} ${Math.max(1, svgHeight)}`);

  // Build node lookup map
  const nodeMap = new Map<string, SimulationNode>();

  // Size scale for word count
  const sizeScale = d3
    .scaleSqrt()
    .domain([0, d3.max(articles, (d) => d.word_count) || 1000])
    .range([MIN_RADIUS, MAX_RADIUS]);

  // Category-based coloring (top-level category). Use deterministic mapping so colors
  // don't reshuffle when filters change.

  // Opacity scale for age
  const now = Date.now();
  const ageScale = d3.scaleLinear().domain([0, 365]).range([1, 0.4]).clamp(true);

  // Create nodes
  const nodes: SimulationNode[] = articles.map((article) => {
    const wordCount = Number.isFinite(article.word_count) ? article.word_count : 0;
    const baseSize = sizeScale(wordCount);
    const width = Math.max(MIN_LABEL_WIDTH, baseSize * LABEL_WIDTH_FACTOR);
    const height = Math.max(MIN_LABEL_HEIGHT, baseSize * LABEL_HEIGHT_FACTOR);
    const node: SimulationNode = {
      article,
      x: Math.random() * Math.max(1, svgWidth),
      y: Math.random() * Math.max(1, svgHeight),
      width,
      height,
      collisionRadius: Math.max(width, height) / 2,
    };
    nodeMap.set(article.id, node);
    return node;
  });

  // Create links based on selected clustering mode
  const links: ForceLink[] = [];
  const linkSet = new Set<string>();

  const addLink = (source: SimulationNode, target: SimulationNode, strength: number) => {
    const linkId = [source.article.id, target.article.id].sort().join('-');
    if (linkSet.has(linkId)) return;
    linkSet.add(linkId);
    links.push({ source, target, strength });
  };

  const canUseTaxonomy =
    linkMode.value === 'taxonomy' && nodes.some((n) => !!n.article.taxonomy_cluster_id);

  if (canUseTaxonomy) {
    const clusters = new Map<string, SimulationNode[]>();

    nodes.forEach((node) => {
      const clusterId = node.article.taxonomy_cluster_id;
      if (!clusterId) return;
      const list = clusters.get(clusterId) || [];
      list.push(node);
      clusters.set(clusterId, list);
    });

    clusters.forEach((clusterNodes) => {
      if (clusterNodes.length < 2) return;
      const hub = clusterNodes[0];
      for (let i = 1; i < clusterNodes.length; i += 1) {
        addLink(hub, clusterNodes[i], 0.9);
      }
    });
  } else {
    articles.forEach((article) => {
      if (!article.neighbors || article.neighbors.length === 0) return;

      const sourceNode = nodeMap.get(article.id);
      if (!sourceNode) return;

      // Create links to pre-computed neighbors
      article.neighbors.forEach((neighborId) => {
        const targetNode = nodeMap.get(neighborId);
        if (targetNode) {
          addLink(sourceNode, targetNode, 1);
        }
      });
    });
  }

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
        .strength((d) => Math.max(0.05, Math.min(1, d.strength)) * 0.35),
    )
    .force('charge', d3.forceManyBody().strength(chargeStrength.value))
    .force('center', d3.forceCenter(svgWidth / 2, svgHeight / 2))
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
    .attr('data-source-id', (d) => (d.source as SimulationNode).article.id)
    .attr('data-target-id', (d) => (d.target as SimulationNode).article.id)
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
    .attr('data-article-id', (d) => d.article.id)
    .style('cursor', 'pointer')
    .on('mouseenter', (event, d) => {
      highlightedArticleId.value = d.article.id;
      tooltip.value = {
        visible: true,
        article: d.article,
        x: event.pageX + 10,
        y: event.pageY + 10,
      };
      // Highlight connected nodes
      applyHighlight();
    })
    .on('mouseleave', () => {
      tooltip.value.visible = false;
      highlightedArticleId.value = null;
      applyHighlight();
    })
    .on('click', (_, d) => {
      openArticle(d.article.id);
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
    .attr('fill', (d) => getCategoryColor(getCategoryLabel(d.article)))
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
    .scaleExtent(ZOOM_EXTENT)
    .on('zoom', (event) => {
      g.attr('transform', event.transform);
    });

  svg.call(zoom);

  // Auto-fit to the currently rendered nodes (important after filters change).
  // Use a short delay so the simulation has a moment to spread nodes out.
  window.setTimeout(() => {
    if (epoch !== renderEpoch) return;
    fitGraphToView({
      svg,
      zoom,
      nodes,
      width: svgWidth,
      height: svgHeight,
    });
  }, FIT_DELAY_MS);
}

let svgResizeObserver: ResizeObserver | null = null;

onMounted(async () => {
  await store.fetchArticles();
  await nextTick();

  // Render once the SVG exists and has dimensions.
  window.requestAnimationFrame(() => renderVisualization());

  // Keep the layout responsive: re-render when the SVG size changes.
  if (typeof ResizeObserver !== 'undefined') {
    svgResizeObserver = new ResizeObserver(() => {
      renderVisualization();
    });
    if (svgRef.value) {
      svgResizeObserver.observe(svgRef.value);
    }
  }
});

onBeforeUnmount(() => {
  if (svgResizeObserver) {
    svgResizeObserver.disconnect();
    svgResizeObserver = null;
  }
});

watch(
  () => store.filteredArticles,
  () => {
    renderVisualization();
  },
);

watch(
  () => store.availableTags.map((t) => t.value).join('|'),
  () => {
    const allowed = new Set(store.availableTags.map((t) => t.value));
    const next = selectedTagValues.value.filter((value) => allowed.has(value));
    if (next.length !== selectedTagValues.value.length) {
      selectedTagValues.value = next;
      updateFiltersImmediate();
    }
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
  background: var(--pw-panel-bg);
  border-right: 1px solid var(--pw-border-color);
  padding: 1.5rem;
  overflow-y: auto;
  color: var(--pw-text-primary);
}

.sidebar-actions {
  display: grid;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.sidebar h2 {
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
  color: var(--pw-text-primary);
}

.filter-section {
  margin-bottom: 1.5rem;
}

.filter-section label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--pw-text-primary);
}

.filter-section input[type='search'] {
  width: 100%;
}

.graph-controls {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.75rem;
  border: 1px solid var(--pw-border-color);
  border-radius: 8px;
  background: var(--pw-panel-bg);
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
  color: var(--pw-text-primary);
  font-weight: 600;
}

.filter-section input[type='range'] {
  width: calc(100% - 50px);
  margin-right: 0.5rem;
  accent-color: var(--pw-ui-accent-strong);
}

.range-value {
  font-size: 0.85rem;
  color: var(--pw-text-primary);
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
  border: 1px solid var(--pw-border-color);
  border-radius: 4px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: normal;
  cursor: pointer;
  color: var(--pw-text-primary);
}

.category-swatch {
  display: inline-block;
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 999px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.08);
  flex: 0 0 auto;
}

.category-swatch--filter {
  width: 1rem;
  height: 1rem;
}

.category-swatch--tiny {
  width: 0.6rem;
  height: 0.6rem;
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

.matches-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.matches-title {
  margin: 0;
}

.matches-sort {
  padding: 0.35rem 0.5rem;
  font-size: 0.85rem;
}

.matches-subtitle {
  margin-top: 0.35rem;
  font-size: 0.8rem;
  color: var(--pw-text-secondary);
  font-weight: 500;
}

.matches-list {
  margin-top: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 260px;
  overflow-y: auto;
  padding-right: 0.25rem;
}

.match-item {
  text-align: left;
  background: var(--pw-surface-bg);
  border: 1px solid var(--pw-border-color);
  border-radius: 6px;
  padding: 0.6rem 0.65rem;
  overflow-wrap: anywhere;
}

.match-item:hover {
  background: var(--pw-bg-secondary);
}

.match-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--pw-text-primary);
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow-wrap: anywhere;
}

.match-meta {
  margin-top: 0.2rem;
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  font-size: 0.78rem;
  color: var(--pw-text-primary);
  overflow-wrap: anywhere;
}

.match-topic {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  min-width: 0;
}

.match-topic-text {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow-wrap: anywhere;
  min-width: 0;
}

.match-date {
  flex: 0 0 auto;
}

.stats {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--pw-border-color);
}

.stats p {
  margin: 0.25rem 0;
  color: var(--pw-text-primary);
}

.visualization-area {
  flex: 1;
  position: relative;
  background: var(--pw-bg-secondary);
}

.empty {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  font-size: 1rem;
  color: var(--pw-text-secondary);
}

.visualization-svg {
  width: 100%;
  height: 100%;
}

.tooltip {
  position: fixed;
  background: var(--pw-panel-bg);
  border: 1px solid var(--pw-border-color);
  border-radius: 6px;
  padding: 1rem;
  box-shadow: var(--pw-shadow-md);
  max-width: 300px;
  pointer-events: none;
  z-index: 1000;
}

.tooltip h3 {
  font-size: 1rem;
  margin: 0 0 0.5rem 0;
  color: var(--pw-text-primary);
  overflow-wrap: anywhere;
}

.tooltip .excerpt {
  font-size: 0.85rem;
  color: var(--pw-text-secondary);
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
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.5rem;
  background: var(--pw-surface-primary-muted);
  color: var(--pw-primary-600);
  border-radius: 3px;
  font-size: 0.75rem;
  font-weight: 600;
}

.tooltip .tags {
  font-size: 0.75rem;
  color: var(--pw-text-muted);
}

.tooltip .stats-line {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--pw-text-muted);
  padding-top: 0.5rem;
  border-top: 1px solid var(--pw-border-color);
}

.article-node text {
  font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, sans-serif;
  pointer-events: none;
}

.article-node .node-title {
  font-size: 0.7rem;
  font-weight: 600;
  fill: var(--pw-btn-primary-text);
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

.article-node.is-dimmed {
  opacity: 0.25;
}

line.link.is-dimmed {
  stroke-opacity: 0.1;
}

.article-node.is-highlighted {
  opacity: 1;
}

line.link.is-highlighted {
  stroke-opacity: 1;
  stroke-width: 3;
}
</style>
