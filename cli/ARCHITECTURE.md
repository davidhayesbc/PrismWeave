# PrismWeave CLI - File Relationships & Architecture

Visual guide to understanding how the CLI components work together.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    PrismWeave CLI                            │
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │   User CLI   │──────│  Commander   │──────│  Commands │ │
│  │   Commands   │      │   Framework  │      │  Handler  │ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│                                │                             │
│                                ▼                             │
│                    ┌───────────────────────┐                │
│                    │   Config Manager      │                │
│                    │  (~/.prismweave/)     │                │
│                    └───────────────────────┘                │
│                                │                             │
│              ┌─────────────────┼─────────────────┐          │
│              ▼                 ▼                 ▼          │
│    ┌─────────────────┐ ┌──────────────┐ ┌──────────────┐  │
│    │ Browser Capture │ │   Markdown   │ │     File     │  │
│    │   (Puppeteer)   │ │  Converter   │ │   Manager    │  │
│    └─────────────────┘ └──────────────┘ └──────────────┘  │
│              │                 │                 │          │
│              ▼                 ▼                 ▼          │
│         Web Page          HTML Content       GitHub API    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Component Relationships

### Main Entry Point (`index.ts`)

```
index.ts (CLI Entry)
    │
    ├─► Commander (CLI Framework)
    │   ├─► capture command
    │   └─► config command
    │
    ├─► ConfigManager (Settings)
    │   └─► ~/.prismweave/config.json
    │
    ├─► BrowserCapture (Headless Browser)
    │   ├─► Puppeteer
    │   └─► MarkdownConverter
    │
    └─► FileManager (GitHub)
        └─► GitHub REST API
```

### Shared Code Architecture

```
Browser Extension          CLI Tool
      │                       │
      ├─► markdown-converter-core.ts ◄──┤
      ├─► file-manager.ts ◄──────────────┤
      └─► types/index.ts ◄───────────────┘
          (Shared Code ~60%)
```

---

## 🔄 Data Flow Diagrams

### Single URL Capture Flow

```
1. User Command
   prismweave capture https://example.com
         │
         ▼
2. CLI Parser (Commander)
   Parse arguments and options
         │
         ▼
3. Config Manager
   Load GitHub settings
         │
         ▼
4. Browser Capture
   ├─► Launch Puppeteer
   ├─► Navigate to URL
   ├─► Extract content
   └─► Extract metadata
         │
         ▼
5. Markdown Converter
   ├─► Convert HTML to Markdown
   ├─► Apply custom rules
   └─► Generate frontmatter
         │
         ▼
6. File Manager
   ├─► Determine folder (tech/tutorial/etc)
   ├─► Generate filename
   ├─► Create/update GitHub file
   └─► Commit changes
         │
         ▼
7. Success Message
   ✅ Captured and saved to GitHub
```

### Batch Processing Flow

```
1. User Command
   prismweave capture --file urls.txt
         │
         ▼
2. Read URL File
   Split into array of URLs
         │
         ▼
3. Process Loop
   For each URL:
   ├─► Single URL Capture Flow (above)
   ├─► Wait 1 second (rate limit)
   └─► Continue to next
         │
         ▼
4. Summary Report
   ✅ X successful
   ❌ Y failed
```

### Configuration Flow

```
1. User Command
   prismweave config --set githubToken=TOKEN
         │
         ▼
2. Config Manager
   ├─► Load current config
   ├─► Validate new value
   ├─► Update setting
   └─► Save to disk
         │
         ▼
3. Confirmation
   ✅ Configuration updated
```

---

## 📁 File Dependency Tree

```
index.ts
├── browser-capture.ts
│   ├── puppeteer (npm)
│   ├── shared/markdown-converter-core.ts
│   │   ├── turndown (npm)
│   │   └── shared with browser extension ✓
│   └── config.ts
│       └── fs (node)
├── shared/file-manager.ts
│   ├── shared with browser extension ✓
│   └── fetch (node)
├── commander (npm)
├── chalk (npm)
└── ora (npm)
```

---

## 🔗 Module Interactions

### Browser Capture Module

```typescript
BrowserCapture
    │
    ├─► initialize()
    │   └─► puppeteer.launch()
    │
    ├─► captureUrl(url)
    │   ├─► page.goto(url)
    │   ├─► extractContent()
    │   │   ├─► page.evaluate()
    │   │   └─► DOM extraction
    │   ├─► convertToMarkdown()
    │   │   └─► MarkdownConverterCore
    │   └─► generateFrontmatter()
    │
    └─► close()
        └─► browser.close()
```

### Markdown Converter Module (Shared)

```typescript
MarkdownConverterCore
    │
    ├─► initialize()
    │   └─► Setup TurndownService
    │
    ├─► convertToMarkdown(html)
    │   ├─► turndownService.turndown()
    │   ├─► Apply custom rules
    │   │   ├─► Task list rule
    │   │   └─► Strikethrough rule
    │   └─► Return markdown
    │
    └─► Shared with browser extension ✓
```

### File Manager Module (Shared)

```typescript
FileManager
    │
    ├─► determineFolder(metadata)
    │   └─► Keyword matching
    │       ├─► tech/, tutorial/
    │       ├─► news/, business/
    │       └─► reference/, tools/
    │
    ├─► generateFilename(metadata)
    │   └─► Format: YYYY-MM-DD-domain-keywords-HHMM.md
    │
    ├─► saveToGitHub(settings, filepath, content)
    │   ├─► Check if file exists
    │   ├─► Create/update file
    │   ├─► Commit with message
    │   └─► Return result
    │
    ├─► testConnection(settings)
    │   ├─► Validate token
    │   ├─► Check repository
    │   └─► Test write access
    │
    └─► Shared with browser extension ✓
```

### Config Manager Module

```typescript
ConfigManager
    │
    ├─► loadConfig()
    │   ├─► Read ~/.prismweave/config.json
    │   └─► Return settings object
    │
    ├─► saveConfig(config)
    │   ├─► Validate settings
    │   ├─► Write to disk
    │   └─► Return success
    │
    ├─► get(key)
    │   └─► Return specific setting
    │
    ├─► set(key, value)
    │   ├─► Validate value
    │   ├─► Update config
    │   └─► Save to disk
    │
    └─► validate(config)
        ├─► Check required fields
        └─► Validate formats
```

---

## 🎯 Command Flow Examples

### Example 1: Capture with Custom Message

```
Command:
  prismweave capture https://blog.com/article --message "Great article"

Flow:
  1. CLI Parser extracts:
     - URL: "https://blog.com/article"
     - message: "Great article"

  2. Load Config:
     - githubToken: "ghp_xxx"
     - githubRepo: "user/repo"

  3. Browser Capture:
     - Launch browser
     - Navigate to URL
     - Extract: title, content, metadata

  4. Convert to Markdown:
     - HTML → Markdown
     - Generate frontmatter

  5. Save to GitHub:
     - Folder: "documents/" (default)
     - Filename: "2025-01-15-blog.com-article-1234.md"
     - Commit: "Great article"

  6. Output:
     ✅ Captured: Great Article
     📁 Saved to: documents/2025-01-15-blog.com-article-1234.md
```

### Example 2: Batch Processing

```
Command:
  prismweave capture --file tech-articles.txt

File Content (tech-articles.txt):
  https://nodejs.org/en/docs/
  https://github.com/features
  https://developer.mozilla.org/en-US/

Flow:
  1. Read File:
     - Parse 3 URLs

  2. For Each URL:
     URL 1: nodejs.org/en/docs/
       ├─► Capture → tech/2025-01-15-nodejs.org-docs-1234.md
       └─► Wait 1 second

     URL 2: github.com/features
       ├─► Capture → tech/2025-01-15-github.com-features-1235.md
       └─► Wait 1 second

     URL 3: developer.mozilla.org
       ├─► Capture → reference/2025-01-15-developer.mozilla.org-1236.md
       └─► Done

  3. Summary:
     ✅ Successfully captured 3 URLs
     📁 Saved to GitHub repository
```

### Example 3: Config Test

```
Command:
  prismweave config --test

Flow:
  1. Load Config:
     - githubToken: "ghp_xxx"
     - githubRepo: "user/repo"

  2. Test GitHub User:
     GET https://api.github.com/user
     ├─► 200 OK
     └─► User: "username"

  3. Test Repository Access:
     GET https://api.github.com/repos/user/repo
     ├─► 200 OK
     └─► Repo: "user/repo" (private: false)

  4. Test Write Access:
     GET https://api.github.com/repos/user/repo/contents
     ├─► 200 OK
     └─► Has write access: true

  5. Output:
     ✅ GitHub connection test successful
     👤 User: username
     📦 Repository: user/repo (public)
     ✍️  Write access: Yes
```

---

## 🧩 Shared Code Strategy

### What's Shared (60%+ Reuse)

```
┌────────────────────────────────────────────────┐
│          Browser Extension                     │
│  ┌──────────────────────────────────────┐    │
│  │  src/utils/                          │    │
│  │  ├─► markdown-converter.ts           │    │
│  │  │   └─► Core conversion logic       │────┼─┐
│  │  ├─► file-manager.ts                 │    │ │
│  │  │   └─► GitHub operations           │────┼─┤
│  │  └─► types/index.ts                  │    │ │
│  │      └─► Interface definitions       │────┼─┤
│  └──────────────────────────────────────┘    │ │
└────────────────────────────────────────────────┘ │
                                                   │
┌────────────────────────────────────────────────┐ │
│          CLI Tool                              │ │
│  ┌──────────────────────────────────────┐    │ │
│  │  src/shared/                         │    │ │
│  │  ├─► markdown-converter-core.ts ◄────┼────┘ │
│  │  │   └─► Adapted for Node.js         │      │
│  │  ├─► file-manager.ts ◄───────────────┼──────┘
│  │  │   └─► Direct reuse                │
│  │  └─► types/ (referenced)             │
│  │      └─► Shared definitions          │
│  └──────────────────────────────────────┘    │
└────────────────────────────────────────────────┘
```

### What's CLI-Specific

```
CLI-Specific Components:
├─► browser-capture.ts
│   └─► Puppeteer integration (replaces content scripts)
│
├─► config.ts
│   └─► File-based configuration (replaces chrome.storage)
│
└─► index.ts
    └─► Commander CLI interface (replaces popup/options UI)
```

### Adaptation Layer

```
Browser Extension API          Node.js API
─────────────────────          ───────────
chrome.storage.sync     ──►    fs.readFile/writeFile
chrome.runtime.sendMsg  ──►    Direct function calls
content scripts         ──►    Puppeteer page.evaluate
popup UI                ──►    Commander CLI
chrome.tabs             ──►    Puppeteer browser/page
```

---

## 📊 Performance Flow

### Timing Breakdown (Typical)

```
Total Capture Time: ~10 seconds

├─► Browser Launch: ~3-5 seconds
│   └─► Puppeteer.launch()
│
├─► Page Load: ~2-4 seconds
│   └─► page.goto() + waitForNetworkIdle
│
├─► Content Extraction: ~0.5 seconds
│   └─► page.evaluate() + DOM parsing
│
├─► Markdown Conversion: ~0.2 seconds
│   └─► turndownService.turndown()
│
├─► GitHub API Call: ~1-2 seconds
│   ├─► Check existing file
│   └─► Create/update commit
│
└─► Browser Cleanup: ~0.3 seconds
    └─► browser.close()
```

### Memory Usage

```
Base CLI Process: ~50MB
├─► Node.js runtime: ~30MB
└─► CLI code: ~20MB

Puppeteer Browser: ~300MB
├─► Chromium process: ~250MB
└─► Page context: ~50MB

Peak Memory: ~350MB per capture
```

---

## 🚀 Optimization Strategies

### Current Implementation

```
Sequential Processing:
  URL 1 → Browser → Convert → Save → Close
           ↓
  URL 2 → Browser → Convert → Save → Close
           ↓
  URL 3 → Browser → Convert → Save → Close

  Total Time: 3 URLs × 10 seconds = 30 seconds
```

### Future Parallel Processing

```
Parallel Processing (Future):
  ┌─► URL 1 → Browser → Convert → Save → Close
  ├─► URL 2 → Browser → Convert → Save → Close
  └─► URL 3 → Browser → Convert → Save → Close

  Total Time: ~12 seconds (with 3 concurrent workers)
```

---

## 📝 Summary

This CLI tool demonstrates:

- **Clean Architecture**: Separation of concerns
- **Code Reuse**: 60%+ shared with browser extension
- **Extensibility**: Easy to add new features
- **Maintainability**: Clear module boundaries
- **Type Safety**: Full TypeScript support

**Key Files**:

- `index.ts` - Main entry point
- `browser-capture.ts` - Puppeteer integration
- `config.ts` - Configuration management
- `shared/markdown-converter-core.ts` - Shared conversion
- `shared/file-manager.ts` - Shared GitHub operations

**Next Steps**: Install dependencies and start capturing! 📝✨
