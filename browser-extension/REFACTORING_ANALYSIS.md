# PrismWeave Code Refactoring Analysis

## Major Refactoring Opportunities Identified

### 1. **Duplicate Default Settings Implementations**

**Issue**: Three different classes implement `getDefaultSettings()` with inconsistent schemas:

- `service-worker.js` (6 properties)
- `popup.js` (6 properties) 
- `options.js` (15+ properties)

**Impact**: Schema inconsistencies, maintenance burden, potential bugs

**Solution**: Create centralized settings manager

### 2. **Repeated DOM Manipulation Patterns**

**Issue**: Both `popup.js` and `options.js` have extensive, similar DOM manipulation code:

- Form population (37 lines in options.js)
- Event listener setup (40+ lines each)
- Status/loading UI management
- Input validation

**Impact**: Code duplication, harder to maintain UI consistency

**Solution**: Create shared UI utility class

### 3. **Scattered Settings Management**

**Issue**: Settings loading/saving logic is duplicated across:
- Service worker
- Popup
- Options page

**Impact**: Inconsistent error handling, duplicate chrome.storage calls

**Solution**: Centralized settings service

### 4. **Inconsistent Error Handling**

**Issue**: Different error handling patterns across files:
- Some use try/catch, others don't
- Inconsistent error logging
- Different user feedback methods

**Solution**: Standardized error handling utility

### 5. **Redundant Content Extraction Logic**

**Issue**: Content script and service worker both handle content extraction differently

**Solution**: Consolidate extraction logic

### 6. **Mixed Validation Logic**

**Issue**: URL validation, filename validation, etc. scattered across multiple files

**Solution**: Already partially addressed with SharedUtils, but more can be moved

## Detailed Analysis

### Settings Schema Inconsistencies

**Service Worker Default Settings:**
```javascript
{
  autoCommit: false,
  autoPush: false,
  repositoryPath: '',
  githubToken: '',
  defaultFolder: 'unsorted',
  fileNamingPattern: 'YYYY-MM-DD-domain-title'
}
```

**Options Page Default Settings:**
```javascript
{
  repositoryPath: '',
  githubToken: '',
  githubRepo: '', // MISSING FROM SERVICE WORKER
  defaultFolder: 'unsorted',
  customFolder: '', // MISSING FROM SERVICE WORKER
  namingPattern: 'YYYY-MM-DD-domain-title', // DIFFERENT NAME
  autoCommit: false,
  autoPush: false,
  captureImages: true, // MISSING FROM SERVICE WORKER
  removeAds: true, // MISSING FROM SERVICE WORKER
  removeNavigation: true, // MISSING FROM SERVICE WORKER
  preserveLinks: true, // MISSING FROM SERVICE WORKER
  customSelectors: '', // MISSING FROM SERVICE WORKER
  commitMessageTemplate: 'Add: {domain} - {title}', // MISSING FROM SERVICE WORKER
  enableKeyboardShortcuts: true, // MISSING FROM SERVICE WORKER
  showNotifications: true // MISSING FROM SERVICE WORKER
}
```

### DOM Manipulation Duplication

**Similar patterns in popup.js and options.js:**
- `showStatus()` / `hideStatus()` methods
- Form field population loops
- Event listener attachment patterns
- Loading state management

### Chrome Extension API Duplication

**Repeated patterns:**
- `chrome.runtime.sendMessage()` calls
- `chrome.storage.sync.get/set()` operations
- Tab manipulation
- Error response handling

## Proposed Refactoring Plan

### Phase 1: Settings Consolidation
1. Create `SettingsManager` class
2. Define canonical settings schema
3. Migrate all files to use centralized settings

### Phase 2: UI Utilities
1. Create `UIManager` class for common DOM operations
2. Standardize status/loading/error display
3. Create form utilities for population/validation

### Phase 3: Message Handling
1. Create `MessageBus` class for chrome extension messaging
2. Standardize request/response patterns
3. Centralize error handling

### Phase 4: Content Processing
1. Consolidate content extraction logic
2. Standardize page analysis utilities
3. Unified capture workflow

## Priority Issues

### High Priority
1. **Settings schema inconsistency** - Can cause runtime errors
2. **Duplicate chrome.storage calls** - Performance impact
3. **Inconsistent error handling** - Poor user experience

### Medium Priority
1. **DOM manipulation duplication** - Maintenance burden
2. **Validation logic scattered** - Code organization
3. **Content extraction redundancy** - Code clarity

### Low Priority
1. **Styling inconsistencies** - UI polish
2. **Keyboard shortcut handling** - Feature completeness
3. **Import/export utilities** - Nice-to-have improvements

## Estimated Impact

**Code Reduction**: ~200-300 lines across files
**Maintenance**: 50% reduction in settings-related bugs
**Performance**: Fewer chrome.storage calls, better caching
**Reliability**: Consistent error handling and validation
**Developer Experience**: Single source of truth for settings
