# Final Tree Structure Fix - Exact Whitespace Preservation

## Problem Identified

The HTML source shows the tree structure with proper line breaks:

```html
<pre class="brush: plain; title: ; notranslate" title="">
tree -L 2
.
├── Dockerfile
├── README-model-runner.md
├── README.md
├── backend.env
├── compose.yaml
├── frontend
..
├── go.mod
├── go.sum
├── grafana
│   └── provisioning
├── main.go
├── main_branch_update.md
├── observability
│   └── README.md
├── pkg
│   ├── health
│   ├── logger
│   ├── metrics
│   ├── middleware
│   └── tracing
├── prometheus
│   └── prometheus.yml
├── refs
│   └── heads
..

21 directories, 33 files
</pre>
```

But the output was collapsing to one line, indicating the whitespace wasn't
being preserved.

## Root Cause

The `preserveTreeStructures` rule was using complex regex logic to try to
reconstruct line breaks, but this was unreliable and error-prone.

## Final Solution

Simplified the approach to use `innerHTML` and preserve ALL whitespace exactly
as it appears in the HTML:

```typescript
replacement: (content: string, node: any) => {
  // For tree structures, use innerHTML and preserve ALL whitespace exactly
  let text = node.innerHTML || '';

  // Remove any HTML tags but preserve ALL whitespace including line breaks
  text = text
    .replace(/<br\s*\/?>/gi, '\n') // Convert <br> to newlines
    .replace(/<[^>]*>/g, '') // Remove HTML tags
    .replace(/&lt;/g, '<') // Decode HTML entities
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, ' '); // Convert non-breaking spaces

  // If innerHTML was empty, fall back to textContent but still don't modify formatting
  if (!text.trim()) {
    text = node.textContent || '';
  }

  // NO trimming, NO line modifications - preserve exact whitespace as it appears in HTML
  return `\n\`\`\`\n${text}\n\`\`\`\n`;
};
```

## Key Changes

1. **Use `innerHTML`** instead of `textContent` to capture whitespace
2. **Only remove HTML tags** - don't modify any whitespace
3. **No trimming** - preserve exact formatting
4. **No regex reconstruction** - keep original structure
5. **Decode HTML entities** to clean text content

## Expected Result

The tree structure should now appear exactly as in the HTML:

```markdown
\`\`\` tree -L 2 . ├── Dockerfile ├── README-model-runner.md ├── README.md ├──
backend.env ├── compose.yaml ├── frontend .. ├── go.mod ├── go.sum ├── grafana │
└── provisioning ├── main.go ├── main_branch_update.md ├── observability │ └──
README.md ├── pkg │ ├── health │ ├── logger │ ├── metrics │ ├── middleware │ └──
tracing ├── prometheus │ └── prometheus.yml ├── refs │ └── heads ..

21 directories, 33 files \`\`\`
```

## Testing

1. Load the updated extension from `browser-extension/dist`
2. Capture the Docker blog page
3. Verify tree structures have proper line breaks and indentation
4. Check that all formatting matches the original HTML exactly

This approach should finally preserve the exact whitespace and line structure
from the HTML source.
