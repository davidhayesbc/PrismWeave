<template>
  <div class="map-container">
    <aside class="sidebar">
      <h2>Filters</h2>

      <div class="filter-section">
        <label>Visualization Mode</label>
        <div class="mode-toggle">
          <button 
            :class="{ active: layoutMode === 'embedding' }"
            @click="switchLayout('embedding')"
            class="mode-btn"
          >
            Semantic Space
          </button>
          <button 
            :class="{ active: layoutMode === 'force' }"
            @click="switchLayout('force')"
            class="mode-btn"
          >
            Network Graph
          </button>
        </div>
      </div>

      <div class="filter-section" v-if="layoutMode === 'force'">
        <label>Link Distance</label>
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

      <div class="filter-section" v-if="layoutMode === 'force'">
        <label>Charge Strength</label>
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
        <p v-if="layoutMode === 'force'"><strong>Links:</strong> {{ linkCount }}</p>
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

// Layout mode
type LayoutMode = 'embedding' | 'force';
const layoutMode = ref<LayoutMode>('embedding');
const linkDistance = ref(80);
const chargeStrength = ref(-100);
const linkCount = ref(0);

const CLUSTER_COUNT = 8;
const CLUSTER_ITERATIONS = 20;
const COLLISION_PADDING = 8;
const MIN_RADIUS = 6;
const MAX_RADIUS = 24;
const FORCE_ITERATIONS = 250;
const REPULSION_STRENGTH = -28;
const MIN_LABEL_WIDTH = 140;
const MIN_LABEL_HEIGHT = 64;
const LABEL_WIDTH_FACTOR = 4.8;
const LABEL_HEIGHT_FACTOR = 2.6;
const LABEL_HORIZONTAL_PADDING = 16;
const LABEL_VERTICAL_PADDING = 22;

const COLOR_PALETTE = d3.schemeTableau10;

type SimulationNode = d3.SimulationNodeDatum & {
  article: ArticleSummary;
  targetX: number;
  targetY: number;
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

function switchLayout(mode: LayoutMode) {
  layoutMode.value = mode;
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
  try {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    }).format(new Date(dateStr));
  } catch (error) {
    return formatDate(dateStr);
  }
}

function truncateText(value: string, maxChars: number): string {
  if (value.length <= maxChars) {
    return value;
  }
  return `${value.slice(0, Math.max(0, maxChars - 1)).trim()}…`;
}

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

function computeClusters(articles: ArticleSummary[], desiredClusters: number): Map<string, number> {
  const validArticles = articles.filter(
    (article) => article.x !== undefined && article.y !== undefined,
  );
  const clusterCount = Math.min(Math.max(desiredClusters, 1), validArticles.length);
  const assignments = new Array(validArticles.length).fill(0);
  const centroids: Array<[number, number]> = [];

  if (validArticles.length === 0) {
    return new Map();
  }

  centroids.push([validArticles[0].x!, validArticles[0].y!]);
  for (let idx = 1; idx < clusterCount; idx += 1) {
    let farthestArticle = validArticles[0];
    let farthestDistance = -Infinity;

    validArticles.forEach((article) => {
      let nearestDistance = Number.POSITIVE_INFINITY;
      centroids.forEach(([cx, cy]) => {
        const dx = article.x! - cx;
        const dy = article.y! - cy;
        const distance = dx * dx + dy * dy;
        if (distance < nearestDistance) {
          nearestDistance = distance;
        }
      });

      if (nearestDistance > farthestDistance) {
        farthestDistance = nearestDistance;
        farthestArticle = article;
      }
    });

    centroids.push([farthestArticle.x!, farthestArticle.y!]);
  }

  if (clusterCount === 0) {
    return new Map();
  }

  for (let iteration = 0; iteration < CLUSTER_ITERATIONS; iteration += 1) {
    let moved = false;

    validArticles.forEach((article, index) => {
      let bestCluster = 0;
      let smallestDistance = Number.POSITIVE_INFINITY;

      centroids.forEach(([cx, cy], centroidIndex) => {
        const dx = article.x! - cx;
        const dy = article.y! - cy;
        const distance = dx * dx + dy * dy;
        if (distance < smallestDistance) {
          smallestDistance = distance;
          bestCluster = centroidIndex;
        }
      });

      if (assignments[index] !== bestCluster) {
        moved = true;
        assignments[index] = bestCluster;
      }
    });

    const accumulators = Array.from({ length: clusterCount }, () => ({ x: 0, y: 0, count: 0 }));
    assignments.forEach((clusterIndex, articleIndex) => {
      const article = validArticles[articleIndex];
      const accumulator = accumulators[clusterIndex];
      accumulator.x += article.x!;
      accumulator.y += article.y!;
      accumulator.count += 1;
    });

    accumulators.forEach((accumulator, idx) => {
      if (accumulator.count > 0) {
        centroids[idx] = [accumulator.x / accumulator.count, accumulator.y / accumulator.count];
      }
    });

    if (!moved) break;
  }

  const assignmentsMap = new Map<string, number>();
  validArticles.forEach((article, index) => {
    assignmentsMap.set(article.id, assignments[index]);
  });

  return assignmentsMap;
}

function renderVisualization() {
  if (!svgRef.value) return;

  const articles = store.filteredArticles.filter((a) => a.x !== undefined && a.y !== undefined);
  if (articles.length === 0) return;

  if (layoutMode.value === 'embedding') {
    renderEmbeddingLayout(articles);
  } else {
    renderForceLayout(articles);
  }
}

function renderEmbeddingLayout(articles: ArticleSummary[]) {
  if (!svgRef.value) return;

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

  const clusterAssignments = computeClusters(articles, CLUSTER_COUNT);
  const colorScale = d3
    .scaleOrdinal<number, string>(COLOR_PALETTE)
    .domain(d3.range(COLOR_PALETTE.length));

  // Size scale for word count
  const sizeScale = d3
    .scaleSqrt()
    .domain([0, d3.max(articles, (d) => d.word_count) || 1000])
    .range([MIN_RADIUS, MAX_RADIUS]);

  // Opacity scale for age
  const now = Date.now();
  const ageScale = d3
    .scaleLinear()
    .domain([0, 365]) // 0 to 1 year
    .range([1, 0.4])
    .clamp(true);

  const nodes: SimulationNode[] = articles.map((article) => {
    const baseSize = sizeScale(article.word_count);
    const width = Math.max(MIN_LABEL_WIDTH, baseSize * LABEL_WIDTH_FACTOR);
    const height = Math.max(MIN_LABEL_HEIGHT, baseSize * LABEL_HEIGHT_FACTOR);
    return {
      article,
      x: xScale(article.x!),
      y: yScale(article.y!),
      targetX: xScale(article.x!),
      targetY: yScale(article.y!),
      width,
      height,
      collisionRadius: Math.max(width, height) / 2,
    };
  });

  const simulation = d3
    .forceSimulation(nodes)
    .force('x', d3.forceX<SimulationNode>((node) => node.targetX).strength(0.2))
    .force('y', d3.forceY<SimulationNode>((node) => node.targetY).strength(0.2))
    .force('charge', d3.forceManyBody().strength(REPULSION_STRENGTH))
    .force(
      'collide',
      d3.forceCollide<SimulationNode>((node) => node.collisionRadius + COLLISION_PADDING),
    )
    .stop();

  for (let i = 0; i < FORCE_ITERATIONS; i += 1) {
    simulation.tick();
  }

  const rawXExtent = d3.extent(nodes, (node) => node.x ?? node.targetX) as [number, number];
  const rawYExtent = d3.extent(nodes, (node) => node.y ?? node.targetY) as [number, number];
  const currentCenterX = (rawXExtent[0] + rawXExtent[1]) / 2;
  const currentCenterY = (rawYExtent[0] + rawYExtent[1]) / 2;
  const desiredCenterX = width / 2;
  const desiredCenterY = height / 2;
  const availableWidth = width - padding * 2;
  const availableHeight = height - padding * 2;
  const currentWidth = Math.max(rawXExtent[1] - rawXExtent[0], 1);
  const currentHeight = Math.max(rawYExtent[1] - rawYExtent[0], 1);
  const scaleX = clamp(availableWidth / currentWidth, 0.6, 1.8);
  const scaleY = clamp(availableHeight / currentHeight, 0.6, 1.8);

  const positionsById = new Map<string, { x: number; y: number }>();
  nodes.forEach((node) => {
    const baseX = node.x ?? node.targetX;
    const baseY = node.y ?? node.targetY;
    const shiftedX = (baseX - currentCenterX) * scaleX + desiredCenterX;
    const shiftedY = (baseY - currentCenterY) * scaleY + desiredCenterY;
    const finalX = clamp(shiftedX, padding, width - padding);
    const finalY = clamp(shiftedY, padding, height - padding);
    positionsById.set(node.article.id, {
      x: finalX,
      y: finalY,
    });
    node.x = finalX;
    node.y = finalY;
  });

  // Draw edges (if neighbors exist)
  const g = svg.append('g');

  articles.forEach((article) => {
    if (article.neighbors && article.neighbors.length > 0) {
      const sourcePosition = positionsById.get(article.id);
      if (!sourcePosition) return;

      article.neighbors.forEach((neighborId) => {
        const neighborPosition = positionsById.get(neighborId);
        if (neighborPosition) {
          g.append('line')
            .attr('x1', sourcePosition.x)
            .attr('y1', sourcePosition.y)
            .attr('x2', neighborPosition.x)
            .attr('y2', neighborPosition.y)
            .attr('stroke', '#ddd')
            .attr('stroke-width', 1)
            .attr('opacity', 0.25);
        }
      });
    }
  });

  // Draw nodes
  const nodeGroups = g
    .selectAll('g.article-node')
    .data(nodes)
    .enter()
    .append('g')
    .attr('class', 'article-node')
    .attr(
      'transform',
      (d) => `translate(${(d.x ?? d.targetX) - d.width / 2}, ${(d.y ?? d.targetY) - d.height / 2})`,
    )
    .style('cursor', 'pointer')
    .on('mouseenter', (event, d) => {
      tooltip.value = {
        visible: true,
        article: d.article,
        x: event.pageX + 10,
        y: event.pageY + 10,
      };
    })
    .on('mouseleave', () => {
      tooltip.value.visible = false;
    })
    .on('click', (_, d) => {
      router.push({ name: 'article', params: { id: d.article.id } });
    });

  nodeGroups
    .append('rect')
    .attr('width', (d) => d.width)
    .attr('height', (d) => d.height)
    .attr('rx', 12)
    .attr('ry', 12)
    .attr('fill', (d) => {
      const clusterIndex = clusterAssignments.get(d.article.id) ?? 0;
      const colorDomainSize = COLOR_PALETTE.length;
      return colorScale(clusterIndex % colorDomainSize);
    })
    .attr('opacity', (d) => {
      const age = (now - new Date(d.article.created_at).getTime()) / (1000 * 60 * 60 * 24);
      return ageScale(age);
    })
    .attr('stroke', (d) => (d.article.read_status === 'read' ? '#2b2b2b' : '#fff'))
    .attr('stroke-width', (d) => (d.article.read_status === 'read' ? 1 : 2));

  nodeGroups
    .append('text')
    .attr('class', 'node-title')
    .attr('x', LABEL_HORIZONTAL_PADDING)
    .attr('y', LABEL_VERTICAL_PADDING)
    .text((d) => {
      const approxChars = Math.max(12, Math.floor((d.width - LABEL_HORIZONTAL_PADDING * 2) / 7));
      return truncateText(d.article.title, approxChars);
    });

  nodeGroups
    .append('text')
    .attr('class', 'node-date')
    .attr('x', LABEL_HORIZONTAL_PADDING)
    .attr('y', () => LABEL_VERTICAL_PADDING + 18)
    .text((d) => formatShortDate(d.article.created_at));

  // Add zoom behavior
  const zoom = d3
    .zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.5, 5])
    .on('zoom', (event) => {
      g.attr('transform', event.transform);
    });

  svg.call(zoom);
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

  // Cluster assignments for coloring
  const clusterAssignments = computeClusters(articles, CLUSTER_COUNT);
  const colorScale = d3
    .scaleOrdinal<number, string>(COLOR_PALETTE)
    .domain(d3.range(COLOR_PALETTE.length));

  // Opacity scale for age
  const now = Date.now();
  const ageScale = d3
    .scaleLinear()
    .domain([0, 365])
    .range([1, 0.4])
    .clamp(true);

  // Create nodes
  const nodes: SimulationNode[] = articles.map((article) => {
    const baseSize = sizeScale(article.word_count);
    const width = Math.max(MIN_LABEL_WIDTH, baseSize * LABEL_WIDTH_FACTOR);
    const height = Math.max(MIN_LABEL_HEIGHT, baseSize * LABEL_HEIGHT_FACTOR);
    const node: SimulationNode = {
      article,
      x: width / 2 + Math.random() * (width - width),
      y: height / 2 + Math.random() * (height - height),
      targetX: width / 2,
      targetY: height / 2,
      width,
      height,
      collisionRadius: Math.max(width, height) / 2,
    };
    nodeMap.set(article.id, node);
    return node;
  });

  // Create links from neighbor data
  const links: ForceLink[] = [];
  const linkSet = new Set<string>();

  articles.forEach((article) => {
    if (article.neighbors && article.neighbors.length > 0) {
      const sourceNode = nodeMap.get(article.id);
      if (!sourceNode) return;

      article.neighbors.forEach((neighborId) => {
        const targetNode = nodeMap.get(neighborId);
        if (targetNode) {
          // Avoid duplicate links
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
    }
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
        .strength(0.3)
    )
    .force('charge', d3.forceManyBody().strength(chargeStrength.value))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force(
      'collide',
      d3.forceCollide<SimulationNode>((d) => d.collisionRadius + COLLISION_PADDING)
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
          (link as ForceLink).source === d || (link as ForceLink).target === d ? 1 : 0.1
        )
        .attr('stroke-width', (link) =>
          (link as ForceLink).source === d || (link as ForceLink).target === d ? 3 : 1.5
        );
    })
    .on('mouseleave', () => {
      tooltip.value.visible = false;
      d3.selectAll('line.link')
        .attr('stroke-opacity', 0.4)
        .attr('stroke-width', 1.5);
    })
    .on('click', (_, d) => {
      router.push({ name: 'article', params: { id: d.article.id } });
    })
    .call(
      d3.drag<SVGGElement, SimulationNode>()
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
        })
    );

  nodeGroups
    .append('rect')
    .attr('width', (d) => d.width)
    .attr('height', (d) => d.height)
    .attr('rx', 12)
    .attr('ry', 12)
    .attr('x', (d) => -d.width / 2)
    .attr('y', (d) => -d.height / 2)
    .attr('fill', (d) => {
      const clusterIndex = clusterAssignments.get(d.article.id) ?? 0;
      return colorScale(clusterIndex % COLOR_PALETTE.length);
    })
    .attr('opacity', (d) => {
      const age = (now - new Date(d.article.created_at).getTime()) / (1000 * 60 * 60 * 24);
      return ageScale(age);
    })
    .attr('stroke', (d) => (d.article.read_status === 'read' ? '#2b2b2b' : '#fff'))
    .attr('stroke-width', (d) => (d.article.read_status === 'read' ? 1 : 2));

  nodeGroups
    .append('text')
    .attr('class', 'node-title')
    .attr('x', (d) => -d.width / 2 + LABEL_HORIZONTAL_PADDING)
    .attr('y', (d) => -d.height / 2 + LABEL_VERTICAL_PADDING)
    .text((d) => {
      const approxChars = Math.max(12, Math.floor((d.width - LABEL_HORIZONTAL_PADDING * 2) / 7));
      return truncateText(d.article.title, approxChars);
    });

  nodeGroups
    .append('text')
    .attr('class', 'node-date')
    .attr('x', (d) => -d.width / 2 + LABEL_HORIZONTAL_PADDING)
    .attr('y', (d) => -d.height / 2 + LABEL_VERTICAL_PADDING + 18)
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

  // Stop simulation after a while for performance
  simulation.on('end', () => {
    console.log('Force simulation completed');
  });
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

.mode-toggle {
  display: flex;
  gap: 0.5rem;
}

.mode-btn {
  flex: 1;
  padding: 0.5rem;
  font-size: 0.85rem;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-btn:hover {
  background: #f5f5f5;
}

.mode-btn.active {
  background: #4CAF50;
  color: white;
  border-color: #4CAF50;
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
  font-size: 0.78rem;
  font-weight: 600;
  fill: #fff;
}

.article-node .node-date {
  font-size: 0.7rem;
  fill: rgba(255, 255, 255, 0.9);
}

line.link {
  transition: stroke-opacity 0.2s, stroke-width 0.2s;
}
</style>
