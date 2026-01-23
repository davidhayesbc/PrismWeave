<template>
  <div class="page viz-page">
    <header class="site-header">
      <div class="brand">
        <div class="brand__meta">
          <h1>PrismWeave</h1>
          <p>Visualization</p>
        </div>
      </div>
      <nav class="viz-nav">
        <router-link to="/" class="pw-btn pw-btn-secondary">Graph</router-link>
        <button @click="handleRebuild" :disabled="loading" class="pw-btn pw-btn-primary">
          {{ loading ? 'Rebuilding...' : 'Rebuild Index' }}
        </button>
      </nav>
    </header>
    <main class="page-main viz-main">
      <router-view />
    </main>
    <div v-if="toastMessage" class="pw-toast" :class="toastClass" @click="clearToast">
      {{ toastMessage }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { useArticlesStore } from '@/stores/articles';
import { computed } from 'vue';

const store = useArticlesStore();
const loading = computed(() => store.loading);
const error = computed(() => store.error);
const notice = computed(() => store.notice);
const toastMessage = computed(() => notice.value || error.value);
const toastClass = computed(() => (notice.value ? 'pw-toast-success' : 'pw-toast-error'));

async function handleRebuild() {
  try {
    const response = await store.rebuildVisualization();
    store.setNotice(response.message || 'Visualization index rebuilt successfully');
  } catch (e) {
    console.error('Rebuild failed:', e);
  }
}

function clearToast() {
  store.setError(null);
  store.setNotice(null);
}
</script>

<style scoped>
.viz-nav {
  display: flex;
  gap: var(--pw-space-3);
  align-items: center;
}
</style>
