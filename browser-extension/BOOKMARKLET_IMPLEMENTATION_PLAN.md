# Bookmarklet Implementation Plan for PrismWeave Browser Extension

## Overview

Add bookmarklet support to the PrismWeave browser extension, allowing users to
capture content from any webpage without needing the browser extension
installed. The bookmarklet will reuse existing extension code and provide a
fallback capture method.

## Implementation Steps

### Phase 1: Core Bookmarklet Infrastructure

- [x] **Step 1.1**: Create bookmarklet generation utility

  - [x] Create `src/utils/bookmarklet-generator.ts` for generating bookmarklet
        code
  - [x] Create `src/utils/bookmarklet-core.ts` for core bookmarklet
        functionality
  - [x] Implement URL-safe JavaScript code generation and compression

- [x] **Step 1.2**: Add bookmarklet configuration to settings

  - [x] Update `src/types/index.ts` to include bookmarklet settings interface
  - [x] Update `SettingsManager` to handle bookmarklet configuration
  - [x] Add bookmarklet endpoint URL configuration

- [x] **Step 1.3**: Create bookmarklet options page
  - [x] Create `src/options/bookmarklet.html` for bookmarklet management UI
  - [x] Create `src/options/bookmarklet.ts` for bookmarklet generation and copy
        functionality
  - [x] Add navigation to bookmarklet page from main options

### Phase 2: Content Extraction Refactoring

- [x] **Step 2.1**: Extract reusable content extraction utilities

  - [x] Refactor `ContentExtractor` from `src/utils/content-extractor.ts` for
        standalone use
  - [x] Create `src/utils/content-extraction-core.ts` with DOM-only dependencies
  - [x] Create `src/utils/markdown-converter-core.ts` for HTML-to-markdown
        conversion (already existed with comprehensive functionality)

- [x] **Step 2.2**: Create bookmarklet-compatible content capture
  - [x] Create `src/utils/bookmarklet-content-capture.ts` with no Chrome API
        dependencies
  - [x] Implement DOM-based content extraction using existing strategies
  - [x] Add content cleanup and markdown conversion functionality

### Phase 3: Bookmarklet Runtime Implementation

- [x] **Step 3.1**: Create bookmarklet execution environment

  - [x] Create `src/bookmarklet/runtime.ts` as main bookmarklet entry point
  - [x] Implement content extraction and processing without extension APIs
  - [x] Add user interface overlay for bookmarklet interaction

- [x] **Step 3.2**: Implement remote content submission
  - [x] Create API endpoint handling in bookmarklet for content submission
  - [x] Add GitHub API direct integration for commits (using user's token)
  - [x] Implement error handling and user feedback

### Phase 4: Integration with Existing Extension

- [x] **Step 4.1**: Add bookmarklet generation to extension

  - [x] Update options page to include bookmarklet generation section
  - [x] Add bookmarklet customization options (GitHub repo, folder structure,
        etc.)
  - [x] Implement one-click bookmarklet creation and installation

- [x] **Step 4.2**: Create bookmarklet management utilities
  - [x] Add bookmarklet testing functionality
  - [x] Create bookmarklet sharing features
  - [x] Add bookmarklet usage statistics and monitoring

### Phase 5: Build System and Deployment

- [x] **Step 5.1**: Update build configuration

  - [x] Modify `tsconfig.json` to handle bookmarklet compilation
  - [x] Update build scripts to generate minified bookmarklet code
  - [x] Add bookmarklet bundling to existing build process

- [x] **Step 5.2**: Add bookmarklet assets to extension
  - [x] Update `manifest.json` to include bookmarklet resources
  - [x] Add bookmarklet templates and assets to web accessible resources
  - [x] Create bookmarklet documentation and help files

### Phase 6: Testing and Documentation

- [x] **Step 6.1**: Create comprehensive tests

  - [x] Add unit tests for bookmarklet generation utilities (19 tests passing)
  - [x] Create integration tests for content extraction (13 tests passing)
  - [x] Add end-to-end tests for bookmarklet functionality (13 tests passing)
  - [x] Make sure all tests pass with no console errors (310/310 tests passing)
  - [x] Clean up any old files and tests we don't need

- [x] **Step 6.2**: Update documentation
  - [x] Create user guide for bookmarklet installation and usage
  - [x] Add developer documentation for bookmarklet architecture
  - [x] Update README with bookmarklet features and setup instructions

## Technical Architecture

### File Structure

```
src/
├── bookmarklet/
│   ├── runtime.ts              # Main bookmarklet execution code
│   ├── ui.ts                   # Bookmarklet UI overlay
│   └── templates/
│       └── bookmarklet.js      # Generated bookmarklet template
├── options/
│   ├── bookmarklet.html        # Bookmarklet management page
│   └── bookmarklet.ts          # Bookmarklet options functionality
├── utils/
│   ├── bookmarklet-generator.ts    # Bookmarklet code generation
│   ├── bookmarklet-core.ts         # Core bookmarklet functionality
│   ├── content-extraction-core.ts  # Standalone content extraction
│   └── markdown-converter-core.ts  # Standalone markdown conversion
```

### Core Components

#### 1. BookmarkletGenerator

- Generates JavaScript code for bookmarklets
- Handles user configuration and customization
- Creates URL-safe, minified bookmarklet code
- Manages bookmarklet versioning and updates

#### 2. ContentExtractionCore

- Standalone content extraction without Chrome APIs
- Reuses existing content detection strategies
- DOM-only content processing
- Compatible with any webpage context

#### 3. BookmarkletRuntime

- Main execution environment for bookmarklet
- Content capture and processing
- User interface and feedback
- GitHub API integration for content saving

#### 4. BookmarkletUI

- Overlay interface for bookmarklet interaction
- Progress indication and error display
- Settings and configuration interface
- Content preview and editing capabilities

### Integration Points

#### 1. Settings Integration

- Extend existing `ISettings` interface for bookmarklet configuration
- Reuse GitHub authentication and repository settings
- Add bookmarklet-specific options (UI theme, default folder, etc.)

#### 2. Content Capture Service Integration

- Reuse content detection and extraction logic
- Share markdown conversion utilities
- Maintain consistency with extension capture behavior

#### 3. Build System Integration

- Extend existing TypeScript build process
- Add bookmarklet minification and optimization
- Include bookmarklet assets in extension package

## Reusable Components

### From Existing Extension

- Content extraction strategies from `ContentExtractor`
- Markdown conversion logic from `content-capture-service.ts`
- GitHub API integration patterns from `SettingsManager`
- DOM manipulation utilities from `content-script.ts`
- Error handling patterns from existing services

### New Shared Utilities

- `content-extraction-core.ts` - Chrome API independent content extraction
- `markdown-converter-core.ts` - Standalone HTML to markdown conversion
- `github-api-core.ts` - Direct GitHub API client (no Chrome storage)
- `dom-utils-core.ts` - Cross-platform DOM utilities

## Implementation Notes

### Design Principles

1. **Code Reuse**: Maximize reuse of existing extension logic
2. **Simplicity**: Keep bookmarklet code minimal and focused
3. **Compatibility**: Ensure bookmarklet works across different browsers
4. **Security**: Handle GitHub tokens securely in bookmarklet context
5. **Performance**: Minimize bookmarklet size and loading time

### Technical Constraints

- No Chrome extension APIs available in bookmarklet context
- Limited storage options (localStorage only)
- Cross-origin restrictions for API calls
- Code size limitations for bookmarklet URLs
- Need for inline CSS and minimal UI footprint

### Security Considerations

- GitHub token handling in bookmarklet environment
- Content Security Policy compatibility
- XSS protection in injected bookmarklet code
- Secure transmission of captured content

## Success Criteria

- [x] Bookmarklet successfully captures content from web pages
- [x] Content quality matches extension-based capture
- [x] User can easily install and use bookmarklet
- [x] Bookmarklet integrates with existing GitHub workflow
- [x] Comprehensive test coverage for all bookmarklet functionality (310 tests
      passing across all components)
- [x] Clear documentation for installation and usage

## Future Enhancements

- Offline content queueing in bookmarklet
- Advanced content editing in bookmarklet UI
- Bookmarklet analytics and usage tracking
- Multi-repository support in bookmarklet
- Collaborative features for shared bookmarklets
