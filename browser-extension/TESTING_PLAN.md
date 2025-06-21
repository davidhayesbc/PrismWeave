# PrismWeave Browser Extension - Comprehensive Testing Plan

## Overview

This document outlines a comprehensive testing strategy for the PrismWeave browser extension, covering core functionality including settings management, content extraction, markdown conversion, and file operations.

## Testing Categories

### 1. Unit Tests
- **Scope**: Individual function and class testing
- **Framework**: Jest
- **Coverage Target**: 80%+ for critical modules

### 2. Integration Tests
- **Scope**: Component interaction testing
- **Focus**: Cross-module functionality and data flow

### 3. End-to-End Tests
- **Scope**: Complete user workflows
- **Tools**: Browser automation (Puppeteer/Playwright)

### 4. Performance Tests
- **Scope**: Resource usage, processing time, memory management
- **Tools**: Chrome DevTools, custom benchmarks

---

## Completed Tests Summary

### Tests Implemented and Passing ✅

#### A. Settings Management (`settings-manager.test.ts`)
- **A.1.1** ✅ Verify all schema fields have default values
- **A.1.2** ✅ Test loading when storage is empty
- **A.2.1** ✅ Test save to sync storage (saving valid settings)
- **A.3.1** ✅ Test required field validation (Validate settings with correct types)
- **A.3.2** ✅ Test type validation (Validate settings with incorrect types)
- **A.3.3** ✅ Test pattern validation (GitHub repo format)
- **A.4.1** ✅ Handle storage errors gracefully
- **A.4.3** ✅ Test schema migration scenarios (Reset settings to defaults)
- **A.5.1** ✅ Verify JSON format and structure (Export settings sanitized)
- **A.5.2** ✅ Test sensitive data exclusion (GitHub tokens)
- **A.6.1** ✅ Test successful import with complete data
- **A.6.3** ✅ Test import with invalid values (Import invalid JSON fails gracefully)

#### B. Popup Settings Validation (`popup-settings-validation.test.ts`)
- **B.1.1** ✅ Verify validation passes with all required settings present
- **B.1.2** ✅ Verify validation accepts default folder as alternative to repository path
- **B.2.1** ✅ Test detection of missing GitHub token
- **B.2.2** ✅ Test detection of missing GitHub repository
- **B.2.3** ✅ Test detection of missing repository path/default folder
- **B.2.4** ✅ Test handling of multiple missing settings
- **B.3.1** ✅ Test handling of null/undefined settings
- **B.3.2** ✅ Test proper error message generation

**Total Completed Tests: 19**
**Coverage Areas: Settings Management (12 tests), Popup Validation (7 tests)**

---

## Core Functionality Test Plans

### A. Settings Management (`settings-manager.js`)

#### A.1 Settings Loading and Persistence

**Test Suite: Settings Load/Save Lifecycle**

```javascript
describe('SettingsManager - Load/Save Operations', () => {
  // Test cases for basic CRUD operations
  test('should load default settings when no saved settings exist')
  test('should merge user settings with defaults correctly')
  test('should persist settings to both sync and local storage')
  test('should handle storage failures gracefully')
  test('should validate settings before saving')
  test('should reload settings after save to verify persistence')
})
```

**Critical Test Cases:**

1. **Default Settings Loading**
   - [x] 1.1 Verify all schema fields have default values
   - [x] 1.2 Test loading when storage is empty
   - [ ] 1.3 Verify schema validation on load

2. **Settings Persistence**
   - [x] 2.1 Test save to sync storage (primary)
   - [ ] 2.2 Test fallback to local storage
   - [ ] 2.3 Verify settings persist across browser sessions
   - [ ] 2.4 Test concurrent save operations

3. **Settings Validation**
   - [x] 3.1 Test required field validation
   - [x] 3.2 Test type validation (string, boolean, number)
   - [x] 3.3 Test pattern validation (GitHub repo format)
   - [ ] 3.4 Test cross-field validation (autoPush requires githubToken)

4. **Merge and Update Operations**
   - [ ] 4.1 Test merging partial updates with existing settings
   - [ ] 4.2 Test handling of unknown/deprecated fields
   - [x] 4.3 Test schema migration scenarios (Reset settings to defaults)

#### A.2 Settings Import/Export

**Test Suite: Settings Import/Export**

```javascript
describe('SettingsManager - Import/Export', () => {
  test('should export settings in correct JSON format')
  test('should exclude sensitive data from exports')
  test('should validate import data structure')
  test('should handle invalid import data gracefully')
  test('should merge imported settings with defaults')
  test('should preserve existing settings not in import')
})
```

**Critical Test Cases:**

1. **Export Functionality**
   - [x] 1.1 Verify JSON format and structure
   - [x] 1.2 Test sensitive data exclusion (GitHub tokens)
   - [ ] 1.3 Test export of partial settings
   - [ ] 1.4 Verify metadata inclusion (version, timestamp)

2. **Import Validation**
   - [ ] 2.1 Test import data format validation
   - [ ] 2.2 Test handling of missing fields
   - [ ] 2.3 Test type validation for imported values
   - [ ] 2.4 Test pattern validation for imported settings

3. **Import Processing**
   - [x] 3.1 Test successful import with complete data
   - [ ] 3.2 Test partial import scenarios
   - [x] 3.3 Test import with invalid values (Import invalid JSON fails gracefully)
   - [ ] 3.4 Verify settings merge after import

4. **Error Handling**
   - [x] 4.1 Handle storage errors gracefully

#### A.3 Settings Schema and Validation

**Test Suite: Settings Schema Validation**

```javascript
describe('SettingsManager - Schema Validation', () => {
  test('should validate all schema field types')
  test('should enforce required field constraints')
  test('should validate pattern constraints')
  test('should validate option constraints')
  test('should validate number range constraints')
  test('should handle invalid values with fallbacks')
})
```

**Test Data Sets:**
- [ ] 1. Valid settings objects for each field type
- [ ] 2. Invalid type values (string for boolean, etc.)
- [ ] 3. Invalid patterns (malformed GitHub repo)
- [ ] 4. Out-of-range numeric values
- [ ] 5. Unknown/extra fields

### A.4 Popup Settings Validation (`popup.ts`)

#### A.4.1 Settings Validation for Capture Operations

**Test Suite: Popup Settings Validation**

```javascript
describe('PrismWeavePopup - Settings Validation', () => {
  test('should return valid when all required settings are present')
  test('should return invalid when GitHub token is missing')
  test('should return invalid when GitHub repo is missing')
  test('should return invalid when both repository path and default folder are missing')
  test('should return valid when default folder is provided instead of repository path')
  test('should handle multiple missing settings')
  test('should handle null settings')
})
```

**Critical Test Cases:**

1. **Complete Settings Validation**
   - [x] 1.1 Verify validation passes with all required settings present
   - [x] 1.2 Verify validation accepts default folder as alternative to repository path

2. **Missing Settings Detection**
   - [x] 2.1 Test detection of missing GitHub token
   - [x] 2.2 Test detection of missing GitHub repository
   - [x] 2.3 Test detection of missing repository path/default folder
   - [x] 2.4 Test handling of multiple missing settings

3. **Error Handling**
   - [x] 3.1 Test handling of null/undefined settings
   - [x] 3.2 Test proper error message generation

### C. Content Extraction (`content-extractor.js`)

#### C.1 HTML Content Extraction

**Test Suite: Content Extraction Core**

```javascript
describe('ContentExtractor - Core Extraction', () => {
  test('should extract main content from various page layouts')
  test('should preserve semantic structure')
  test('should remove unwanted elements selectively')
  test('should extract page metadata correctly')
  test('should handle empty or invalid documents')
  test('should assess content quality accurately')
})
```

**Critical Test Cases:**

1. **Content Identification**
   - [ ] 1.1 Test article content extraction
   - [ ] 1.2 Test blog post extraction
   - [ ] 1.3 Test documentation page extraction
   - [ ] 1.4 Test forum/discussion page extraction
   - [ ] 1.5 Test handling of single-page applications

2. **Content Cleaning**
   - [ ] 2.1 Test removal of navigation elements
   - [ ] 2.2 Test removal of advertisements
   - [ ] 2.3 Test preservation of article comments
   - [ ] 2.4 Test handling of mixed content types
   - [ ] 2.5 Test selective element preservation

3. **Metadata Extraction**
   - [ ] 3.1 Test Open Graph metadata extraction
   - [ ] 3.2 Test Twitter Card metadata extraction
   - [ ] 3.3 Test JSON-LD structured data extraction
   - [ ] 3.4 Test fallback metadata generation
   - [ ] 3.5 Test canonical URL extraction

4. **Content Quality Assessment**
   - [ ] 4.1 Test word count calculation
   - [ ] 4.2 Test reading time estimation
   - [ ] 4.3 Test content scoring algorithm
   - [ ] 4.4 Test semantic richness detection
   - [ ] 4.5 Test media content assessment

#### C.2 Image and Link Processing

**Test Suite: Media and Link Extraction**

```javascript
describe('ContentExtractor - Media Processing', () => {
  test('should extract and validate image URLs')
  test('should resolve relative URLs correctly')
  test('should extract image metadata (alt, title)')
  test('should handle image errors gracefully')
  test('should extract and validate links')
  test('should categorize internal vs external links')
})
```

**Test Data:**
- Pages with various image formats and sources
- Pages with relative and absolute URLs
- Pages with broken/invalid media links
- Pages with different link types (external, internal, anchor)

#### C.3 Content Structure Analysis

**Test Suite: Structure and Semantic Analysis**

```javascript
describe('ContentExtractor - Structure Analysis', () => {
  test('should identify heading hierarchy')
  test('should detect and preserve code blocks')
  test('should identify and structure tables')
  test('should handle nested content structures')
  test('should preserve definition lists')
  test('should enhance semantic markup')
})
```

### D. Markdown Conversion (`markdown-converter.js`)

#### D.1 HTML to Markdown Conversion

**Test Suite: Core Markdown Conversion**

```javascript
describe('MarkdownConverter - Core Conversion', () => {
  test('should convert basic HTML elements to markdown')
  test('should preserve text formatting (bold, italic)')
  test('should convert headings with proper hierarchy')
  test('should convert lists (ordered and unordered)')
  test('should handle nested content structures')
  test('should convert tables with proper formatting')
})
```

**Critical Test Cases:**

1. **Basic Element Conversion**
   - Headers (h1-h6) → markdown headers
   - Paragraphs → proper line spacing
   - Bold/strong → `**text**`
   - Italic/em → `*text*`
   - Links → `[text](url)`
   - Images → `![alt](src)`

2. **Complex Structure Conversion**
   - Nested lists → proper indentation
   - Tables → markdown table format
   - Blockquotes → `>` prefixed lines
   - Code blocks → fenced code blocks
   - Definition lists → custom format

3. **Content Preservation**
   - Text content accuracy
   - Link URL preservation
   - Image alt text and titles
   - Code language detection
   - Table alignment information

#### D.2 Code Block Processing

**Test Suite: Code Block Conversion**

```javascript
describe('MarkdownConverter - Code Blocks', () => {
  test('should detect programming languages from CSS classes')
  test('should detect languages from data attributes')
  test('should detect languages from content analysis')
  test('should preserve code indentation')
  test('should handle inline code correctly')
  test('should escape special characters in code')
})
```

**Test Data:**
- Code blocks with `language-*` classes
- Code blocks with `data-lang` attributes
- Code blocks with recognizable syntax patterns
- Code with special markdown characters
- Mixed inline and block code

#### D.3 Table Conversion

**Test Suite: Table Processing**

```javascript
describe('MarkdownConverter - Table Conversion', () => {
  test('should detect table headers correctly')
  test('should preserve column alignment')
  test('should handle merged cells (colspan/rowspan)')
  test('should escape pipe characters in cell content')
  test('should handle nested formatting in cells')
  test('should generate proper markdown table syntax')
})
```

**Test Cases:**
- Tables with `<thead>` and `<th>` elements
- Tables with alignment styles
- Tables with complex cell content
- Tables with merged cells
- Tables with nested formatting

#### D.4 Enhanced Content Processing

**Test Suite: Advanced Markdown Features**

```javascript
describe('MarkdownConverter - Advanced Features', () => {
  test('should convert figures with captions')
  test('should handle callouts and note boxes')
  test('should process definition lists')
  test('should preserve semantic HTML elements')
  test('should handle mathematical expressions')
  test('should convert enhanced formatting elements')
})
```

### E. File Management (`file-manager.js`)

#### E.1 Filename Generation

**Test Suite: File Naming**

```javascript
describe('FileManager - Filename Generation', () => {
  test('should generate filenames from templates')
  test('should sanitize titles for filesystem compatibility')
  test('should handle domain extraction from URLs')
  test('should apply custom naming patterns')
  test('should handle filename conflicts')
  test('should ensure proper file extensions')
})
```

**Critical Test Cases:**

1. **Template Processing**
   - Date pattern replacement (`{date}`)
   - Domain pattern replacement (`{domain}`)
   - Title pattern replacement (`{title}`)
   - Custom pattern variables
   - Pattern combination scenarios

2. **Content Sanitization**
   - Special character removal
   - Length limitations
   - Unicode character handling
   - Filesystem-invalid characters
   - Duplicate filename handling

#### E.2 Metadata Generation

**Test Suite: Frontmatter Creation**

```javascript
describe('FileManager - Metadata Processing', () => {
  test('should generate YAML frontmatter correctly')
  test('should escape special characters in YAML')
  test('should include all required metadata fields')
  test('should handle optional metadata fields')
  test('should classify content into folders correctly')
  test('should generate appropriate tags')
})
```

**Test Data:**
- Content with various metadata sources
- Content requiring YAML escaping
- Content from different domains/topics
- Content with edge case characters

#### E.3 Content Organization

**Test Suite: Folder Classification**

```javascript
describe('FileManager - Content Organization', () => {
  test('should classify technical content correctly')
  test('should classify business content correctly')
  test('should classify tutorial content correctly')
  test('should handle ambiguous content classification')
  test('should support custom folder rules')
  test('should fallback to default folder when uncertain')
})
```

### F. Integration Testing

#### F.1 Settings-Content Pipeline

**Test Suite: Settings Impact on Processing**

```javascript
describe('Integration - Settings and Content Processing', () => {
  test('should apply content filtering based on settings')
  test('should use custom selectors from settings')
  test('should apply image capture settings')
  test('should respect naming pattern settings')
  test('should apply folder classification settings')
})
```

#### F.2 Extraction-Conversion Pipeline

**Test Suite: Content Flow Integration**

```javascript
describe('Integration - Extraction to Markdown', () => {
  test('should maintain content integrity through pipeline')
  test('should preserve metadata through conversion')
  test('should handle large content efficiently')
  test('should process multimedia content correctly')
  test('should maintain link relationships')
})
```

#### F.3 Error Handling and Recovery

**Test Suite: Error Scenarios**

```javascript
describe('Integration - Error Handling', () => {
  test('should handle malformed HTML gracefully')
  test('should recover from conversion failures')
  test('should provide meaningful error messages')
  test('should maintain partial functionality on component failure')
  test('should log errors appropriately for debugging')
})
```

---

## Performance Testing

### A. Memory Usage Tests

**Objectives:**
- Monitor memory consumption during large page processing
- Test for memory leaks in repeated operations
- Validate cleanup after processing completion

**Test Scenarios:**
- Processing 100+ pages in sequence
- Processing pages with large image sets
- Processing pages with complex table structures
- Stress testing with malformed HTML

### B. Processing Speed Tests

**Objectives:**
- Benchmark conversion speed for various content types
- Identify performance bottlenecks
- Validate timeout handling

**Metrics:**
- Time to extract content (target: <2s for average page)
- Time to convert to markdown (target: <1s for average content)
- Time to generate metadata (target: <500ms)
- Memory usage per operation (target: <50MB peak)

### C. Storage Performance Tests

**Objectives:**
- Test settings save/load performance
- Validate storage quota handling
- Test sync vs local storage performance

---

## Browser Compatibility Testing

### A. Cross-Browser Support

**Target Browsers:**
- Chrome 100+ (primary)
- Edge 100+ (primary)
- Firefox 100+ (secondary)
- Safari 15+ (secondary)

**Test Scenarios:**
- Extension installation and permissions
- Settings persistence across browsers
- Content extraction accuracy
- Performance characteristics

### B. Extension API Compatibility

**Test Areas:**
- Storage API functionality
- Runtime messaging
- Content script injection
- Background script operations

---

## Test Implementation Strategy

### Phase 1: Core Unit Tests (Week 1-2)
1. Implement settings manager tests
2. Implement content extractor tests
3. Implement markdown converter tests
4. Implement file manager tests

### Phase 2: Integration Tests (Week 3)
1. Component interaction tests
2. Data flow validation tests
3. Error handling tests

### Phase 3: End-to-End Tests (Week 4)
1. Complete workflow tests
2. Browser compatibility tests
3. Performance benchmarks

### Phase 4: Continuous Testing (Ongoing)
1. Automated test execution
2. Coverage monitoring
3. Performance regression testing

---

## Test Data Requirements

### A. Sample Web Pages

**Content Types:**
- Technical blog posts (programming tutorials, documentation)
- Business articles (marketing, finance, strategy)
- News articles (current events, press releases)
- Academic papers (research, studies)
- Forum discussions (Stack Overflow, Reddit)
- E-commerce pages (product descriptions)
- Social media posts (Twitter threads, LinkedIn articles)

**Content Complexity:**
- Simple text-only articles
- Rich media content (images, videos, embedded content)
- Complex layouts (multi-column, sidebars)
- Interactive content (forms, widgets)
- Malformed HTML (real-world edge cases)

### B. Test Settings Configurations

**Configuration Variants:**
- Default settings (clean slate)
- Minimal settings (basic functionality)
- Advanced settings (all features enabled)
- Custom patterns (user-defined templates)
- Edge case settings (extreme values)

### C. Expected Output Samples

**Validation Data:**
- Expected markdown for each test page
- Expected metadata for various content types
- Expected filenames for different naming patterns
- Expected folder classifications
- Expected quality scores

---

## Testing Tools and Setup

### A. Development Dependencies

```json
{
  "devDependencies": {
    "jest": "^29.0.0",
    "@testing-library/dom": "^8.0.0",
    "@testing-library/jest-dom": "^5.0.0",
    "puppeteer": "^19.0.0",
    "jsdom": "^20.0.0",
    "chrome-remote-interface": "^0.32.0"
  }
}
```

### B. Test Configuration

**Jest Configuration (`jest.config.js`):**
```javascript
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/test/setup.js'],
  collectCoverageFrom: [
    'src/utils/*.js',
    'src/background/*.js',
    'src/content/*.js',
    '!src/**/*.test.js'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

### C. Test Environment Setup

**Mock Browser APIs:**
- Chrome storage API
- Chrome runtime messaging
- DOM manipulation APIs
- Network fetch APIs

**Test Data Management:**
- Sample HTML files for extraction testing
- Expected output files for validation
- Configuration presets for different scenarios

---

## Success Criteria

### A. Coverage Metrics
- **Unit Test Coverage**: 85%+ for critical modules
- **Integration Test Coverage**: 70%+ for major workflows
- **End-to-End Test Coverage**: 100% for primary user flows

### B. Performance Benchmarks
- **Content Extraction**: <3 seconds for 95% of pages
- **Markdown Conversion**: <2 seconds for typical content
- **Settings Operations**: <100ms for all operations
- **Memory Usage**: <100MB peak during normal operation

### C. Quality Metrics
- **Conversion Accuracy**: 95%+ for standard HTML elements
- **Content Preservation**: 98%+ for text content integrity
- **Metadata Accuracy**: 90%+ for extracted metadata fields
- **Error Rate**: <1% for well-formed input content

### D. Compatibility Requirements
- **Browser Support**: 100% functionality on Chrome/Edge 100+
- **Extension APIs**: Full compatibility with Manifest V3
- **Storage Reliability**: 99.9% persistence across sessions
- **Cross-Platform**: Consistent behavior across Windows/Mac/Linux

---

## Maintenance and Continuous Testing

### A. Automated Testing Pipeline
1. **Pre-commit hooks**: Run unit tests before code commits
2. **Pull request validation**: Full test suite on PR creation
3. **Nightly builds**: Performance and compatibility testing
4. **Release validation**: Comprehensive test execution before releases

### B. Test Data Updates
1. **Regular content samples**: Update test pages quarterly
2. **Browser compatibility**: Test new browser versions monthly
3. **Performance baselines**: Update benchmarks with each release
4. **Edge case discovery**: Add tests for user-reported issues

### C. Test Review and Improvement
1. **Monthly test review**: Analyze coverage and effectiveness
2. **Performance monitoring**: Track test execution time trends
3. **False positive analysis**: Reduce flaky test occurrences
4. **Test documentation**: Keep test documentation current

This comprehensive testing plan ensures the PrismWeave browser extension maintains high quality, reliability, and performance standards while supporting continuous development and improvement.
