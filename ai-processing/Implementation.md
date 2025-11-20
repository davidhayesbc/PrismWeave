# Visualization Layer Implementation Plan

## Overview

This document breaks down the implementation of the visualization layer into concrete tasks and phases. It assumes:

- Backend: Python (`ai-processing`), reusing existing ChromaDB integration.
- Frontend: Vue 3 + TypeScript.
- Runtime: Docker Compose stack (Chroma + API + UI).

---

## Phase 1: Backend Foundations

### 1.1 Define Article Metadata Schema

- [x] Create a Python model (e.g., dataclass or pydantic model) representing article metadata:
  - [x] `id`: str
  - [x] `path`: str
  - [x] `title`: str
  - [x] `topic`: str | None
  - [x] `tags`: list[str]
  - [x] `created_at`: datetime
  - [x] `updated_at`: datetime
  - [x] `word_count`: int
  - [x] `excerpt`: str
  - [x] `read_status`: bool or str (`"read"`/`"unread"`)
  - [ ] Optional / future fields: `source_url`, `collection`, etc.

- [x] Decide on serialization format:
  - [x] JSON (easier for tooling and web clients) **or**
  - [ ] YAML (more human-readable), ensuring deterministic ordering.

### 1.2 Metadata Index Builder

- [x] Choose index file location, e.g. `.prismweave/index/articles.json`.
- [x] Implement a module in `ai-processing` (e.g., `src/core/metadata_index.py`) that:
  - [x] Walks the documents directory tree and finds markdown files.
  - [x] Parses frontmatter to extract `title`, `tags`, `topic`, date fields, etc.
  - [x] Derives `created_at` / `updated_at` from frontmatter or filesystem if missing.
  - [x] Counts words in the markdown body.
  - [x] Generates an `excerpt` (first N chars/words, or first paragraph).
  - [x] Initializes or preserves `read_status` (default `unread` for new docs).
  - [x] Emits a deterministic index structure keyed by article `id`.

- [x] Ensure index updates:
  - [x] Add new documents.
  - [x] Update changed documents.
  - [x] Remove entries for deleted documents.

### 1.3 CLI Integration (`cli.py`)

- [x] Add a `visualize` command group, or similar, in `cli.py`:
  - [x] `visualize build-index`:
    - [x] Calls metadata index builder.
    - [ ] Triggers Chroma sync and layout computation (see Phase 2).
  - [x] `visualize print-index` (optional for debugging):
    - [x] Prints a summary of the metadata index.

---

## Phase 2: Chroma Integration & Layout

### 2.1 Article-Level Embeddings

- [x] Review current embedding behavior in `ai-processing`:
  - [x] Identify whether embeddings are per-chunk or per-document.

- [x] Implement article-level embedding strategy:
  - [x] Option A: Aggregate chunk embeddings (mean or weighted mean) to a single vector per article.
  - [ ] Option B: Use a designated representative chunk embedding per article.

- [ ] Update or add a pipeline function to:
  - [ ] Ensure one Chroma record per article ID.
  - [ ] Store article-level embedding and metadata reference.

### 2.2 Layout Computation

- [x] Add a layout module (e.g., `src/core/layout.py`) that:
  - [x] Retrieves article embeddings from Chroma.
  - [x] Computes a 2D projection (e.g., with UMAP or a similar library).
  - [x] Produces a mapping `article_id -> (x, y)`.

- [ ] Store layout data:
  - [ ] Save `x` and `y` into Chroma metadata for each article **and/or**
  - [x] Persist into the metadata index file for easy API access.

- [ ] Optional: compute nearest neighbors per article:
  - [ ] Use cosine similarity on embeddings.
  - [ ] Maintain a list of neighbor IDs in metadata (for edges).

### 2.3 Integrate Layout into `visualize build-index`

-- [x] Make `visualize build-index` perform the following in order:
  - [x] (1) Rebuild metadata index from documents.
  - [ ] (2) Sync or rebuild article-level embeddings in Chroma.
  - [x] (3) Compute 2D layout and nearest neighbors.
  - [x] (4) Persist x,y (and neighbors) back into metadata.

---

## Phase 3: HTTP API in ai-processing

### 3.1 API Framework Setup

- [x] Choose lightweight framework (FastAPI recommended):
  - [x] Add dependency to `pyproject.toml`.
  - [x] Create `src/api/app.py` (or similar) with application factory.

- [x] Define shared models (aligned with metadata schema):
  - [x] Pydantic models for `ArticleSummary`, `ArticleDetail`, `UpdateArticleRequest`.

### 3.2 Endpoints

- [x] `GET /articles`
  - [x] Reads metadata index.
  - [x] Returns an array of `ArticleSummary`:
    - [x] `id`, `title`, `topic`, `tags`, `created_at`, `updated_at`, `word_count`, `read_status`, `x`, `y`, optional neighbors.

- [x] `GET /articles/{id}`
  - [x] Reads metadata index and markdown file.
  - [x] Returns `ArticleDetail`:
    - [x] Metadata fields.
    - [x] `content` (full markdown).
    - [x] `path` (filesystem path) for VS Code link.

- [x] `PUT /articles/{id}`
  - [x] Accepts `UpdateArticleRequest` with optional fields:
    - [x] metadata updates (title, topic, tags, read_status).
    - [x] `content` (markdown).
  - [x] Applies changes:
    - [x] Writes markdown to disk.
    - [x] Updates metadata index.
    - [x] Optionally re-embeds and updates layout for this article.

- [x] `DELETE /articles/{id}`
  - [x] Deletes the markdown file.
  - [x] Removes from metadata index.
  - [x] Removes corresponding Chroma entry.

- [x] `POST /visualization/rebuild`
  - [x] Triggers `visualize build-index` logic (or equivalent function).
  - [x] Returns summary statistics (e.g., doc count).

### 3.3 Running the API

- [x] Add an entry point (e.g., `python -m src.api.app` or a `uvicorn` command).
- [x] Document how to run API locally during development.

---

## Phase 4: Vue Frontend (Visualization & Reader)

### 4.1 Project Setup

- [ ] Create a new `visualization` (or similar) directory at repo root or under `website/`.
- [ ] Initialize Vue 3 + TypeScript project (e.g., via Vite):
  - [ ] Configure base URL to work behind Docker.
  - [ ] Add dependencies for markdown rendering and visualization (D3 or light graph lib).

### 4.2 Core Layout & Routing

- [ ] Define routes:
  - [ ] `/` → main map view.
  - [ ] `/article/:id` → article reader/editor view.

- [ ] `App.vue`
  - [ ] Layout shell with sidebar (filters) and main content area.

### 4.3 Map View (`MapView.vue`)

- [ ] Fetch `/articles` on load.
- [ ] Maintain state for:
  - [ ] `articles` (list of summaries).
  - [ ] filters: age range, topic, search query.

- [ ] Render visualization:
  - [ ] Draw nodes at (x, y).
  - [ ] Color, size, opacity, and read/unread styling per requirements.
  - [ ] Draw edges between nearest neighbors if available.

- [ ] Interactions:
  - [ ] Hover → tooltip with title, excerpt, topic/tags, age, word count.
  - [ ] Click → open `/article/{id}` in a **new tab**.
  - [ ] Pan/zoom controls.

### 4.4 Article View (`ArticleView.vue`)

- [ ] On mount, fetch `/articles/{id}`.
- [ ] Render markdown content using a markdown renderer.
- [ ] Show metadata in editable form:
  - [ ] Inputs for title, topic, tags.
  - [ ] Possibly a toggle or indicator for `read_status`.

- [ ] Actions:
  - [ ] Save → `PUT /articles/{id}`.
  - [ ] Delete → `DELETE /articles/{id}` with confirmation.
  - [ ] “Open in VS Code” → `vscode://file/{path}` link.

- [ ] After save/delete:
  - [ ] Show confirmation.
  - [ ] Optionally instruct user to refresh map or trigger rebuild.

### 4.5 Filters & Search

- [ ] Implement sidebar filters:
  - [ ] Age range (slider, using `created_at`/`updated_at`).
  - [ ] Topic multi-select.
  - [ ] Optional tags filter.

- [ ] Implement text search:
  - [ ] Filter or highlight nodes whose title/metadata contain the query.

---

## Phase 5: Dockerization & Orchestration

### 5.1 Dockerfiles

- [ ] `ai-processing-api` Dockerfile:
  - [ ] Base on Python image.
  - [ ] Install `ai-processing` dependencies.
  - [ ] Set entrypoint to run the API server.
  - [ ] Mount documents volume and metadata index at runtime.

- [ ] `visualization-ui` Dockerfile:
  - [ ] Base on node or a builder image to `npm install` & `npm run build`.
  - [ ] Serve built assets via a small server (e.g., nginx or node).

### 5.2 docker-compose.yml

- [ ] Define services:
  - [ ] `chroma`:
    - [ ] ChromaDB container.
    - [ ] Volume for persistence.
  - [ ] `ai-processing-api`:
    - [ ] Depends on `chroma`.
    - [ ] Exposes API port.
    - [ ] Mounts documents and metadata volumes.
  - [ ] `visualization-ui`:
    - [ ] Depends on `ai-processing-api`.
    - [ ] Exposes UI on `localhost`.

- [ ] Network configuration:
  - [ ] Ensure API and UI can reach `chroma` within the compose network.

### 5.3 Local Workflow

- [ ] Document commands:
  - [ ] `docker compose up` to start stack.
  - [ ] Access UI at `http://localhost:<port>`.
  - [ ] Use "Rebuild visualization" button (calls `POST /visualization/rebuild`).

---

## Phase 6: Polish & Quality

### 6.1 UX/Visual Polish

- [ ] Tune colors for topics.
- [ ] Adjust size scaling for word count.
- [ ] Implement smooth hover and selection interactions.
- [ ] Improve tooltips with clear layout.

### 6.2 Robustness

- [ ] Add error handling in API and UI for:
  - [ ] Missing files.
  - [ ] Chroma connectivity issues.
  - [ ] Index rebuild failures.

- [ ] Add loading states and basic retries in the UI.

### 6.3 Documentation

- [ ] Update main project `README` or create a dedicated `VISUALIZATION.md`:
  - [ ] How to build and run the visualization stack.
  - [ ] How the metadata index works.
  - [ ] How to extend metadata fields.

- [ ] Optionally add tests:
  - [ ] Unit tests for metadata index builder and layout.
  - [ ] API endpoint tests (using existing pytest setup).

---

This checklist can be updated as the implementation progresses, with items ticked off as they are completed.