# Markdown Conversion Architecture

## Overview

The markdown conversion system in PrismWeave follows a clean architecture
pattern that separates environment-agnostic conversion logic from
browser-specific concerns.

## Architecture

```
┌─────────────────────────────────────┐
│           Content Script            │
│                                     │
│  import { MarkdownConverter }       │
│  from './utils/markdown'            │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│       MarkdownConverter             │
│     (Browser Adapter)               │
│                                     │
│ • TurndownService initialization    │
│ • Context detection                 │
│ • Browser API integration           │
│ • Error handling & fallbacks        │
└─────────────┬───────────────────────┘
              │ extends
              ▼
┌─────────────────────────────────────┐
│    MarkdownConverterCore            │
│   (Environment-Agnostic)            │
│                                     │
│ • HTML parsing & analysis           │
│ • Conversion rules & algorithms     │
│ • Metadata extraction               │
│ • Output formatting                 │
└─────────────────────────────────────┘
```

## Components

### MarkdownConverterCore

- **Purpose**: Environment-agnostic conversion engine
- **Location**: `src/utils/markdown-converter-core.ts`
- **Coverage**: 72.89%
- **Dependencies**: None (pure logic)

**Responsibilities:**

- HTML semantic analysis
- Conversion rules and algorithms
- Table processing
- Code block detection
- Metadata extraction
- Word counting

### MarkdownConverter

- **Purpose**: Browser-specific adapter
- **Location**: `src/utils/markdown-converter.ts`
- **Coverage**: 64.51%
- **Dependencies**: TurndownService, MarkdownConverterCore

**Responsibilities:**

- TurndownService initialization
- Context detection (content script vs service worker vs test)
- Browser API integration
- Graceful fallbacks when dependencies unavailable

### Public API

- **Purpose**: Clean import interface
- **Location**: `src/utils/markdown/index.ts`
- **Coverage**: N/A (re-exports only)

## Usage Patterns

### Standard Browser Extension Code

```typescript
import { MarkdownConverter } from './utils/markdown';

const converter = new MarkdownConverter();
const result = converter.convertToMarkdown(htmlContent, {
  preserveFormatting: true,
  includeMetadata: true,
});
```

### Testing with Core (Advanced)

```typescript
import { MarkdownConverterCore } from './utils/markdown';

// For unit testing with mock TurndownService
const core = new MarkdownConverterCore();
// Manual setup required...
```

## Context Behavior

| Context          | TurndownService  | Behavior                      |
| ---------------- | ---------------- | ----------------------------- |
| Content Script   | ✅ Available     | Full conversion functionality |
| Service Worker   | ❌ Not available | Limited fallback mode         |
| Test Environment | 🔧 Mocked        | Full testing capability       |

## Benefits of Current Architecture

### ✅ Separation of Concerns

- Core logic isolated from browser APIs
- Environment-specific code contained in adapter
- Clean testing boundaries

### ✅ Testability

- Core can be tested independently
- Mock-friendly adapter pattern
- Clear dependency injection points

### ✅ Maintainability

- Browser-specific workarounds isolated
- Conversion logic reusable across environments
- Clear ownership and responsibilities

### ✅ Extensibility

- Core could support Node.js environments
- Easy to add new adapters for different contexts
- Plugin architecture for custom rules

## Previous Consolidation Analysis

**Initial Assessment**: "Two converters with unclear responsibilities"

**Architecture Review**: The separation is actually well-designed and follows
good software engineering principles. Rather than consolidate, we enhanced
documentation and improved the public API.

**Decision**: Keep both components but improve clarity through:

- Comprehensive documentation
- Clear usage guidelines
- Clean public API
- Architecture diagrams

## Testing Strategy

### Core Testing

- Focus on conversion algorithms
- Test with mocked TurndownService
- Verify metadata extraction
- Validate output formatting

### Adapter Testing

- Test context detection
- Verify TurndownService integration
- Test error handling and fallbacks
- Browser API interaction

### Integration Testing

- End-to-end conversion workflows
- Cross-browser compatibility
- Performance benchmarking
- Memory usage validation

## Performance Considerations

- **Lazy Initialization**: TurndownService only created when needed
- **Context Optimization**: Different behavior for different environments
- **Memory Management**: Clean disposal of conversion artifacts
- **Caching Strategy**: Reuse initialized converters where possible

## Future Enhancements

1. **Node.js Support**: Create Node.js adapter for core
2. **Plugin System**: Allow custom conversion rules
3. **Performance Monitoring**: Add conversion metrics
4. **Advanced Fallbacks**: Improve service worker conversion
5. **Stream Processing**: Support for large document conversion
