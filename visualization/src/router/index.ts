import ArticleView from '@/views/ArticleView.vue';
import MapView from '@/views/MapView.vue';
import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'graph',
      component: MapView,
    },
    {
      path: '/article/:id',
      name: 'article',
      component: ArticleView,
      props: true,
    },
  ],
});

export default router;
