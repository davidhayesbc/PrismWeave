# Visualization Layer Requirements

## High-Level Goals

- Build an **offline-first**, Dockerized visualization UI over ChromaDB and the PrismWeave documents repo.
- Provide a **2D similarity map** of articles with:
  - Node distances reflecting semantic similarity.
  - Edges between similar articles.
  - Visual encoding for topic, length, age, and read status.
- Allow reading, editing, deleting, and retagging articles **through a web UI**, with changes stored in Git-tracked markdown and a simple metadata store.

## Functional Requirements

### 1. Article Representation

- [ ] One node per article
  - [x] Each node corresponds to a single markdown document (multiple chunks behind the scenes in Chroma).
  - [x] Each node has a stable article ID (e.g., path-based or UUID stored in metadata).

- [x] Metadata fields (Git-friendly index)
  - [x] `id` (stable document ID)
  - [x] `path` (path of the markdown file in repo)
  - [x] `title`
  - [x] `topic` (for coloring)
  - [x] `tags` (optional list)
  - [x] `created_at` (from frontmatter or file system)
  - [x] `updated_at` (from frontmatter or file system)
  - [x] `word_count`
  - [x] `excerpt` (short snippet used in hover)
  - [x] `read_status` (`read`/`unread`, or boolean)
  - [ ] Any additional fields PrismWeave already uses (source URL, collection, etc.)

- [ ] Chroma fields
  - [x] Embeddings (per article or aggregated from chunks).
  - [ ] 2D layout coordinates `x`, `y` stored as metadata.
  - [ ] Optional: nearest neighbor IDs for edges (or computed at query time).

### 2. Visualization UI

- [ ] 2D similarity map
  - [ ] Nodes placed using `x`, `y` from the backend (no layout done in browser).
  - [ ] Edges drawn between each node and its nearest neighbors (N configurable).

- [ ] Visual encoding
  - [ ] Node color = `topic`.
  - [ ] Node size = `word_count` bucket (e.g., small/medium/large).
  - [ ] Node opacity / desaturation = age (older → more faded).
  - [ ] Read/unread indicator = border style or small badge/icon.

- [ ] Interactions
  - [ ] Hover node → tooltip with:
    - [ ] title
    - [ ] excerpt
    - [ ] topic / tags
    - [ ] age (created_at / updated_at)
    - [ ] word count
  - [ ] Click node → opens article view in a **new tab**.
  - [ ] Pan/zoom the 2D map (basic navigation).

- [ ] Filters and search
  - [ ] Filter by age range (slider or presets).
  - [ ] Filter by topic (multi-select).
  - [ ] Optional: filter by tags.
  - [ ] Text search box to highlight matching nodes (title/metadata).

### 3. Article Reading & Editing

- [ ] Article reader
  - [ ] New tab route, e.g. `/article/{id}`.
  - [ ] Fetches article via `GET /articles/{id}`.
  - [ ] Renders markdown → HTML (headings, lists, code, etc.).
  - [ ] Displays metadata (title, topic, tags, created/updated, word_count, read_status).
  - [ ] “Open in VS Code” link using `vscode://file/{absolute_path}`.

- [ ] Editing
  - [ ] Editable fields:
    - [ ] title
    - [ ] topic
    - [ ] tags
    - [ ] optional other frontmatter (e.g., summary)
    - [ ] full markdown content
  - [ ] On Save:
    - [ ] Update markdown file content on disk.
    - [ ] Update metadata index (title, tags, topic, word_count, etc.).
    - [ ] Mark article as `read`.
    - [ ] Trigger minimal reindex for that article in Chroma (embedding recompute if needed).

- [ ] Deleting
  - [ ] “Delete article” action in article view.
  - [ ] On confirm:
    - [ ] Delete the markdown file.
    - [ ] Remove entry from metadata index.
    - [ ] Remove article from Chroma.
    - [ ] Return user to main map with article removed.

### 4. Backend / API Requirements

- [x] Metadata index
  - [x] Git-friendly file(s) (JSON or YAML) stored inside the documents workspace, e.g.:
    - [x] `.prismweave/index/articles.json` **or** `documents_index.json`.
  - [x] Index contains all fields listed in “Metadata fields”.
  - [x] Index generation is deterministic, suitable for Git diffs.

- [ ] Rescan & rebuild
  - [x] CLI command (under `cli.py`, e.g. `visualize build-index`) that:
    - [x] Scans documents repo for markdown files.
    - [x] Extracts frontmatter + content.
    - [x] Computes:
      - [x] `title`
      - [x] `tags` / `topic`
      - [x] timestamps
      - [x] word_count
      - [x] excerpt
    - [x] Updates metadata index.
    - [ ] Ensures Chroma entries exist per article.
    - [x] Computes or updates 2D layout coordinates `x`, `y`.
    - [x] Stores x,y in Chroma metadata and/or index.

- [x] HTTP API (Python, inside ai-processing)
  - [x] `GET /articles`
    - [x] Returns list of articles with:
      - [x] id, title, topic, tags, created_at, updated_at, word_count, read_status
      - [x] x, y coordinates
      - [x] neighbor IDs or an adjacency list for edges (optional).
  - [x] `GET /articles/{id}`
    - [x] Returns full markdown content.
    - [x] Returns all metadata from index.
    - [x] Returns filesystem path for VS Code link.
  - [x] `PUT /articles/{id}`
    - [x] Accepts updated metadata + markdown.
    - [x] Writes markdown to disk.
    - [x] Updates metadata index.
    - [x] Updates `read_status`.
    - [x] Optionally updates embedding + layout for that article.
  - [x] `DELETE /articles/{id}`
    - [x] Deletes markdown from disk.
    - [x] Removes from metadata index.
    - [x] Removes from Chroma.
  - [x] `POST /visualization/rebuild`
    - [x] Triggers the same logic as the CLI rescan command (`visualize build-index`).
    - [x] Returns a summary status (e.g., counts of processed docs).

### 5. Chroma & Embeddings

- [ ] Embedding strategy
  - [x] Reuse existing embedding pipeline from `ai-processing`.
  - [x] Decide on per-article embedding:
    - [x] Either aggregate chunk embeddings to one vector per article.
    - [ ] Or pick a representative embedding per article.
  - [ ] Store article-level embedding in Chroma with:
    - [ ] `id` = article ID.
    - [ ] `metadata` including article ID, x,y, topic, etc.

- [ ] 2D layout
  - [ ] Implement layout computation in Python using existing or new library (e.g., UMAP):
    - [ ] Input: article embeddings.
    - [ ] Output: 2D coordinates.
  - [ ] Store `x` and `y` in Chroma metadata and/or metadata index for each article.
  - [ ] Optionally compute nearest neighbors for edges and store them (or compute neighbors at query time using embeddings).

### 6. Frontend (Vue + TypeScript)

- [ ] Tech stack
  - [ ] Vue 3 + TypeScript.
  - [ ] Simple build setup (Vite or similar).
  - [ ] A visualization layer:
    - [ ] Either custom canvas/SVG using D3 or a light graph lib that plays well with Vue.

- [ ] Structure
  - [ ] `App.vue`: basic layout (sidebar filters + main visualization area).
  - [ ] `MapView.vue`:
    - [ ] Fetches `/articles` data.
    - [ ] Renders nodes + edges.
    - [ ] Handles hover tooltips & click navigation.
  - [ ] `ArticleView.vue`:
    - [ ] Fetches `/articles/{id}`.
    - [ ] Renders markdown.
    - [ ] Provides edit form for metadata and content.
    - [ ] Save/Delete actions.
    - [ ] “Open in VS Code” link.

- [ ] State management
  - [ ] Local state in components or small store (e.g., Pinia) for filters and current selection.
  - [ ] Debounced search/filter applied client-side.

### 7. Docker & Offline-First

- [ ] Docker Compose stack
  - [ ] `chroma` service:
    - [ ] Runs ChromaDB.
    - [ ] Persist data locally (volume).
  - [ ] `ai-processing-api` service:
    - [ ] Image built from `ai-processing` Python code.
    - [ ] Exposes HTTP API.
    - [ ] Mounts documents repo and metadata index.
    - [ ] Connects to Chroma.
  - [ ] `visualization-ui` service:
    - [ ] Runs built Vue app served via a tiny web server (e.g., nginx or node).
    - [ ] Exposes port on `localhost`.
  - [ ] All services operate without internet, using only local resources.

- [ ] Environment
  - [ ] No calls to external LLMs or APIs.
  - [ ] All embedding/layout work done locally (using your existing local models / setup).
  - [ ] “Rebuild visualization” is a manual control (button in UI that calls `POST /visualization/rebuild`).
