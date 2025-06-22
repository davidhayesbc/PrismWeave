# Shell Script Code Block Fix Summary

## Problem Identified

The Chris Penner blog post (https://chrispenner.ca/posts/transcript-tests)
contains complex shell scripting code with:

- Nested code blocks within markdown examples
- Special characters like `$`, `#!`, backticks, quotes
- Multiple programming languages (Unison, UCM, Bash, ZSH)
- HTML entities in code content

These were causing issues in the markdown converter, leading to:

- Loss of special characters
- Improper handling of HTML entities
- Missing language detection
- Broken nested code structures

## Improvements Made

### 1. Enhanced Service Worker Code Block Processing

**File**: `src/background/service-worker.ts` (lines 1330-1350)

**Before**:

````javascript
.replace(/<pre[^>]*><code[^>]*>(.*?)<\/code><\/pre>/gis, '```\n$1\n```\n\n')
.replace(/<code[^>]*>(.*?)<\/code>/gi, '`$1`')
````

**After**:

```javascript
// Enhanced code block processing with language detection and proper escaping
.replace(/<pre[^>]*><code[^>]*class="[^"]*language-([^"]*)"[^>]*>([\s\S]*?)<\/code><\/pre>/gis, (match, language, code) => {
  // Decode HTML entities and preserve special characters in code
  const cleanCode = code
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, ' ');
  return `\`\`\`${language}\n${cleanCode}\n\`\`\`\n\n`;
})
.replace(/<pre[^>]*><code[^>]*>([\s\S]*?)<\/code><\/pre>/gis, (match, code) => {
  // Handle code blocks without language specification
  const cleanCode = code
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, ' ');
  return `\`\`\`\n${cleanCode}\n\`\`\`\n\n`;
})
.replace(/<code[^>]*>(.*?)<\/code>/gi, (match, code) => {
  // Handle inline code with proper escaping
  const cleanCode = code
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, ' ');
  return `\`${cleanCode}\``;
})
```

**Improvements**:

- ✅ Language detection and preservation (`language-bash`, `language-zsh`, etc.)
- ✅ Proper HTML entity decoding in code blocks
- ✅ Use of `[\s\S]*?` for better handling of multiline content
- ✅ Separate processing for language-tagged vs. untagged code blocks
- ✅ Proper escaping of special characters

### 2. Enhanced Language Detection

**File**: `src/utils/markdown-converter.ts` (lines 613-690)

**Added Support For**:

- Shell variants: `bash`, `shell`, `sh`, `zsh`
- Script types: `console`, `terminal`, `cmd`, `batch`
- Unison language: `unison`, `ucm` (specific to the blog post)
- Additional prefixes: `hljs-`, `prism-` (for different syntax highlighters)

**Example**:

```typescript
const languageMap: Record<string, string> = {
  // ... existing languages ...
  zsh: 'zsh',
  shell: 'bash',
  sh: 'bash',
  console: 'console',
  terminal: 'bash',
  unison: 'unison',
  ucm: 'unison',
};
```

### 3. Improved TurndownService Rules

**File**: `src/utils/markdown-converter.ts` (lines 183-230)

**Enhanced Code Block Rule**:

````typescript
this.turndownService.addRule('enhancedCodeBlock', {
  filter: (node: any): boolean => {
    return (
      node.nodeName === 'PRE' &&
      node.firstChild &&
      node.firstChild.nodeName === 'CODE'
    );
  },
  replacement: (content: string, node: any): string => {
    const codeElement = node.firstChild;
    const language = this.extractLanguageFromClass(codeElement.className);

    // Get raw text content to preserve formatting and special characters
    let code = codeElement.textContent || '';

    // Preserve HTML entities that should be decoded in code blocks
    code = code
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&amp;/g, '&')
      .replace(/&quot;/g, '"')
      .replace(/&#39;/g, "'")
      .replace(/&nbsp;/g, ' ');

    return '\n\n```' + language + '\n' + code + '\n```\n\n';
  },
});
````

**Enhanced Inline Code Rule**:

```typescript
this.turndownService.addRule('enhancedInlineCode', {
  filter: (node: any): boolean => {
    return (
      node.nodeName === 'CODE' &&
      (!node.parentNode || node.parentNode.nodeName !== 'PRE')
    );
  },
  replacement: (content: string, node: any): string => {
    let code = node.textContent || content;

    // Decode HTML entities for inline code
    code = code
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&amp;/g, '&')
      .replace(/&quot;/g, '"')
      .replace(/&#39;/g, "'")
      .replace(/&nbsp;/g, ' ');

    // Escape backticks in inline code
    code = code.replace(/`/g, '\\`');

    return '`' + code + '`';
  },
});
```

### 4. Improved Fallback Conversion

**File**: `src/utils/markdown-converter.ts` (lines 540-570)

**Enhanced Pre/Code Handling**:

````typescript
case 'pre':
  const codeEl = el.querySelector('code');
  let language = '';
  let codeContent = '';

  if (codeEl) {
    language = this.extractLanguageFromClass(codeEl.className);
    codeContent = codeEl.textContent || '';
  } else {
    codeContent = el.textContent || '';
  }

  // Preserve special characters in code blocks
  const preservedContent = codeContent
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, ' ');

  markdown += '\n\n```' + language + '\n' + preservedContent + '\n```\n\n';
  break;
````

## Test Coverage

### 1. Created Comprehensive Test Suite

**File**: `src/__tests__/utils/shell-script-code-blocks.test.ts`

**Test Categories**:

- Service Worker Markdown Conversion (5 tests)
- Language Detection (1 test)
- HTML Entity Handling (2 tests)

**Key Test Cases**:

- Shell scripts with special characters (`$`, `#!`, quotes)
- Code blocks without language specification
- Inline code with special characters
- Nested code blocks (markdown containing code)
- Multiple language code blocks
- HTML entity decoding

### 2. Enhanced Extension Test Script

**File**: `complete-extension-test.js`

**Added Analysis**:

- Code block counting and validation
- Language tagging detection
- Shell script content verification
- HTML entity issue detection
- Code block examples display

## Expected Outcomes

With these improvements, the Chris Penner blog should now:

1. **✅ Preserve Shell Commands**:

   ```bash
   #!/usr/bin/env zsh
   set -e
   source "../../transcript_helpers.sh"
   fetch "$unauthenticated_user" GET project-get-simple
   ```

2. **✅ Maintain Language Tags**:

   ````markdown
   ```bash
   echo "Shell script"
   ```
   ````

   ```unison
   isZero = cases
     0 -> true
     _ -> false
   ```

3. **✅ Handle Nested Code Blocks**: Complex markdown examples containing their
   own code blocks

4. **✅ Decode HTML Entities**: `&lt;script&gt;` becomes `<script>`
   `&quot;value&quot;` becomes `"value"`

5. **✅ Preserve Special Characters**: `$`, `#!`, `"`, `'`, `{`, `}`, `<`, `>`,
   `&` in code contexts

## Testing Instructions

1. Load the rebuilt extension in Chrome
2. Navigate to https://chrispenner.ca/posts/transcript-tests
3. Run the enhanced test script via DevTools console
4. Check for proper code block preservation and language tagging
5. Verify no HTML entities remain in the markdown output

## Files Modified

1. `src/background/service-worker.ts` - Enhanced regex patterns for code block
   processing
2. `src/utils/markdown-converter.ts` - Improved language detection and
   TurndownService rules
3. `complete-extension-test.js` - Enhanced analysis and reporting
4. `shell-script-test.js` - New specialized test script
5. `src/__tests__/utils/shell-script-code-blocks.test.ts` - Comprehensive test
   suite

The improvements ensure robust handling of complex shell scripting content and
other programming languages in blog posts and technical documentation.
