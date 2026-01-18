<template>
  <div class="app-container">
    <header class="app-header">
      <h1>PrismWeave</h1>
      <nav>
        <router-link to="/" class="nav-link">Graph</router-link>
        <button @click="handleRebuild" :disabled="loading" class="secondary">
          {{ loading ? 'Rebuilding...' : 'Rebuild Index' }}
        </button>
      </nav>
    </header>
    <main class="app-main">
      <router-view />
    </main>
    <div v-if="toastMessage" class="toast" :class="toastClass" @click="clearToast">
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
const toastClass = computed(() => (notice.value ? 'toast--notice' : 'toast--error'));

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
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: var(--pw-ui-accent-strong);
  color: var(--pw-btn-primary-text);
  box-shadow: var(--pw-shadow-sm);
}

.app-header h1 {
  font-size: 1.5rem;
  font-weight: 600;
}

.app-header nav {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav-link {
  color: var(--pw-btn-primary-text);
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: var(--pw-radius);
  transition: background-color 0.2s;
}

.nav-link:hover,
.nav-link.router-link-active {
  background: var(--pw-ui-accent-soft);
}

.app-main {
  flex: 1;
  overflow: hidden;
}

.toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  padding: 1rem 1.5rem;
  color: var(--pw-btn-primary-text);
  border-radius: var(--pw-radius);
  box-shadow: var(--pw-shadow-md);
  cursor: pointer;
  animation: slideIn 0.3s ease;
}

.toast--error {
  background: var(--pw-error-600);
}

.toast--notice {
  background: var(--pw-success-600);
}

@keyframes slideIn {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>
