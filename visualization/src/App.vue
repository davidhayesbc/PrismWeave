<template>
  <div class="page viz-page">
    <header class="viz-header">
      <div class="viz-brand">
        <img :src="logoUrl" alt="PrismWeave" class="viz-logo" />
        <span class="viz-title">PrismWeave</span>
      </div>
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
const logoUrl = new URL('../../logo.png', import.meta.url).href;
const error = computed(() => store.error);
const notice = computed(() => store.notice);
const toastMessage = computed(() => notice.value || error.value);
const toastClass = computed(() => (notice.value ? 'pw-toast-success' : 'pw-toast-error'));

function clearToast() {
  store.setError(null);
  store.setNotice(null);
}
</script>

<style scoped>
.viz-header {
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.viz-brand {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
}

.viz-logo {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  box-shadow: 0 10px 20px -16px rgba(79, 70, 229, 0.45);
}

.viz-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--pw-text-primary);
  letter-spacing: -0.01em;
}
</style>

