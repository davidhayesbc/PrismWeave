<template>
  <div class="article-container">
    <div v-if="store.loading" class="loading">Loading article...</div>
    <div v-else-if="store.error" class="error">{{ store.error }}</div>
    <template v-else-if="article">
      <aside class="article-sidebar">
        <div class="sidebar-actions">
          <button @click="handleRebuild" :disabled="rebuilding" class="pw-btn pw-btn-primary">
            {{ rebuilding ? 'Rebuilding...' : 'Rebuild Index' }}
          </button>
        </div>

        <div class="metadata-section">
          <h3>Metadata</h3>

          <div class="field">
            <label>Title</label>
            <input v-if="editing" type="text" v-model="editForm.title" />
            <p v-else>{{ article.title }}</p>
          </div>

          <div class="field">
            <label>Topic</label>
            <input
              v-if="editing"
              type="text"
              v-model="editForm.topic"
              placeholder="e.g., programming, design"
            />
            <p v-else>{{ article.topic || 'None' }}</p>
          </div>

          <div class="field" v-if="article.taxonomy_category || article.taxonomy_subcategory">
            <label>Taxonomy Category</label>
            <p>
              {{ article.taxonomy_category || 'None' }}
              <span v-if="article.taxonomy_subcategory"> / {{ article.taxonomy_subcategory }}</span>
            </p>
          </div>

          <div class="field" v-if="article.taxonomy_cluster_id">
            <label>Taxonomy Cluster</label>
            <p>{{ article.taxonomy_cluster_id }}</p>
          </div>

          <div class="field" v-if="article.taxonomy_tag_assignments?.length">
            <label>Taxonomy Tags</label>
            <ul class="taxonomy-tags">
              <li v-for="t in article.taxonomy_tag_assignments" :key="t.id">
                <span class="taxonomy-tag-name">{{ t.name }}</span>
                <span class="taxonomy-tag-confidence">({{ Math.round(t.confidence * 100) }}%)</span>
              </li>
            </ul>
          </div>

          <div class="field">
            <label>Read Status</label>
            <select v-if="editing" v-model="editForm.read_status">
              <option value="unread">Unread</option>
              <option value="read">Read</option>
            </select>
            <p v-else>{{ article.read_status }}</p>
          </div>

          <div class="field">
            <label>Word Count</label>
            <p>{{ article.word_count }}</p>
          </div>

          <div class="field">
            <label>Created</label>
            <p>{{ formatDate(article.created_at) }}</p>
          </div>

          <div class="field">
            <label>Updated</label>
            <p>{{ formatDate(article.updated_at) }}</p>
          </div>
        </div>

        <div class="actions-section">
          <template v-if="editing">
            <button @click="saveChanges" class="pw-btn pw-btn-primary" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save' }}
            </button>
            <button @click="cancelEdit" class="pw-btn pw-btn-secondary">Cancel</button>
          </template>
          <template v-else>
            <button @click="startEdit" class="pw-btn pw-btn-primary">Edit</button>
            <button @click="openInVSCode" class="pw-btn pw-btn-secondary">Open in VS Code</button>
            <button @click="confirmDelete" class="pw-btn pw-btn-error">Delete</button>
          </template>
        </div>
      </aside>

      <main class="article-content">
        <div v-if="editing" class="editor">
          <h2>Content Editor</h2>
          <textarea
            v-model="editForm.content"
            class="content-editor"
            placeholder="Markdown content..."
          ></textarea>
        </div>
        <div v-else class="content-viewer" v-html="renderedContent"></div>
      </main>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useArticlesStore } from '@/stores/articles';
import { marked } from 'marked';
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps<{
  id: string;
}>();

const router = useRouter();
const store = useArticlesStore();

const editing = ref(false);
const saving = ref(false);
const rebuilding = ref(false);
const editForm = ref({
  title: '',
  topic: '',
  read_status: 'unread',
  content: '',
});

const article = computed(() => store.currentArticle);

const renderedContent = computed(() => {
  if (!article.value) return '';
  return marked(article.value.content);
});


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

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function startEdit() {
  if (!article.value) return;

  editing.value = true;
  editForm.value = {
    title: article.value.title,
    topic: article.value.topic || '',
    read_status: article.value.read_status,
    content: article.value.content,
  };
}

function cancelEdit() {
  editing.value = false;
}

async function saveChanges() {
  if (!article.value) return;

  saving.value = true;
  try {
    await store.updateArticle(article.value.id, {
      title: editForm.value.title,
      topic: editForm.value.topic || null,
      read_status: editForm.value.read_status,
      content: editForm.value.content,
    });

    editing.value = false;
    store.setNotice('Article saved successfully.');
  } catch (e) {
    store.setError('Failed to save article. See console for details.');
  } finally {
    saving.value = false;
  }
}

function openInVSCode() {
  if (!article.value) return;

  // Construct vscode:// URL
  const absolutePath = article.value.path;
  window.location.href = `vscode://file/${absolutePath}`;
}

async function confirmDelete() {
  if (!article.value) return;

  const confirmed = confirm(
    `Are you sure you want to delete "${article.value.title}"?\n\nThis will:\n- Delete the markdown file\n- Remove it from the index\n- Remove it from ChromaDB\n\nThis action cannot be undone.`,
  );

  if (confirmed) {
    try {
      await store.deleteArticle(article.value.id);
      store.setNotice('Article deleted successfully.');
      router.push({ name: 'graph' });
    } catch (e) {
      store.setError('Failed to delete article. See console for details.');
    }
  }
}

onMounted(async () => {
  await store.fetchArticle(props.id);
});
</script>

<style scoped>
.article-container {
  display: flex;
  height: 100%;
  flex: 1;
  min-height: 0;
  background: var(--pw-panel-bg);
}

.sidebar-actions {
  display: grid;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.article-sidebar {
  width: 300px;
  background: var(--pw-bg-secondary);
  border-right: 1px solid var(--pw-border-color);
  padding: 1.25rem;
  overflow-y: auto;
  min-height: 0;
  color: var(--pw-text-primary);
}

.metadata-section {
  margin: 1.5rem 0;
}

.metadata-section h3 {
  font-size: 1rem;
  margin-bottom: 1rem;
  color: var(--pw-text-primary);
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--pw-text-primary);
  margin-bottom: 0.25rem;
}

.field input,
.field select {
  width: 100%;
}

.field p {
  margin: 0;
  color: var(--pw-text-primary);
}

.taxonomy-tags {
  list-style: none;
  padding: 0;
  margin: 0;
}

.taxonomy-tags li {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.25rem 0;
}

.taxonomy-tag-name {
  color: var(--pw-text-primary);
}

.taxonomy-tag-confidence {
  color: var(--pw-text-primary);
  font-size: 0.85rem;
}

.actions-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--pw-border-color);
}

.actions-section button {
  width: 100%;
}

.article-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 2rem;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.editor {
  display: flex;
  flex-direction: column;
  min-height: 0;
  flex: 1;
}

.editor h2 {
  margin-bottom: 1rem;
  color: var(--pw-text-primary);
}

.content-editor {
  width: 100%;
  flex: 1;
  height: auto;
  min-height: 300px;
  padding: 1rem;
  font-family: var(--pw-font-mono);
  font-size: 0.9rem;
  line-height: 1.6;
  border: 1px solid var(--pw-border-color);
  border-radius: var(--pw-radius);
  background: var(--pw-bg-primary);
  color: var(--pw-text-primary);
  resize: vertical;
}

.content-viewer {
  max-width: 100%;
  margin: 0;
  flex: 1;
}

.content-viewer :deep(h1) {
  font-size: 2rem;
  margin: 2rem 0 1rem 0;
  color: var(--pw-text-primary);
}

.content-viewer :deep(h2) {
  font-size: 1.5rem;
  margin: 1.5rem 0 0.75rem 0;
  color: var(--pw-text-primary);
}

.content-viewer :deep(h3) {
  font-size: 1.25rem;
  margin: 1.25rem 0 0.5rem 0;
  color: var(--pw-text-primary);
}

.content-viewer :deep(p) {
  margin: 1rem 0;
  line-height: 1.8;
}

.content-viewer :deep(ul),
.content-viewer :deep(ol) {
  margin: 1rem 0;
  padding-left: 2rem;
}

.content-viewer :deep(li) {
  margin: 0.5rem 0;
}

.content-viewer :deep(code) {
  background: var(--pw-bg-secondary);
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  font-family: var(--pw-font-mono);
  font-size: 0.9em;
}

.content-viewer :deep(pre) {
  background: var(--pw-bg-secondary);
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  margin: 1rem 0;
}

.content-viewer :deep(pre code) {
  background: none;
  padding: 0;
}

.content-viewer :deep(blockquote) {
  border-left: 4px solid var(--pw-border-color);
  padding-left: 1rem;
  margin: 1rem 0;
  color: var(--pw-text-secondary);
}

.content-viewer :deep(a) {
  color: var(--pw-primary-600);
  text-decoration: none;
}

.content-viewer :deep(a:hover) {
  text-decoration: underline;
}
</style>
