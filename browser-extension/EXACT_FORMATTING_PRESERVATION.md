# Exact Formatting Preservation Fix

## Problem

The user reported that tree structures and other `<pre>` blocks were having
their formatting modified, particularly losing newlines.

## Solution

Modified both `preserveTreeStructures` and `standalonePreBlocks` rules to
preserve **EXACT** formatting from the original HTML.

## Key Changes

### 1. Use `innerHTML` instead of `textContent`

```typescript
// OLD (strips formatting):
const text = (node.textContent || '').trim();

// NEW (preserves formatting):
let text = node.innerHTML || node.textContent || '';
```

### 2. Preserve All Whitespace

```typescript
// Clean up HTML tags but preserve all whitespace and newlines exactly
text = text
  .replace(/<br\s*\/?>/gi, '\n')  // Convert <br> to newlines
  .replace(/<[^>]*>/g, '')        // Remove HTML tags
  .replace(/&lt;/g, '<')          // Decode HTML entities
  .replace(/&gt;/g, '>')
  .replace(/&amp;/g, '&')
  .replace(/&quot;/g, '"')
  .replace(/&#39;/g, "'");

// Don't trim - preserve exact whitespace as it appears in HTML
return \`\n\`\`\`\n${text}\n\`\`\`\n\`;
```

### 3. No Content Modifications

- No trimming of whitespace
- No line number removal
- No content cleaning
- Exact preservation of original HTML formatting

## Expected Result

Tree structures like:

```html
<pre>
├── src/
│   ├── components/
│   └── utils/
└── tests/
</pre>
```

Will become:

```markdown
\`\`\` ├── src/ │ ├── components/ │ └── utils/ └── tests/ \`\`\`
```

With **exactly** the same whitespace, newlines, and indentation as in the
original HTML.

## Testing

1. Load browser extension from `dist/` folder
2. Test on Docker blog page
3. Verify tree structures preserve exact formatting
4. Check that all `<pre>` blocks maintain original spacing

This should completely solve the newline stripping issue by preserving the exact
formatting from the HTML source.
