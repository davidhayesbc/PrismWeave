# Browser Extension Testing Instructions

## Testing the Tree Structure Fix

1. **Load Extension in Chrome/Edge:**

   - Open Chrome or Edge
   - Go to `chrome://extensions/` or `edge://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `d:\source\PrismWeave\browser-extension\dist` folder

2. **Test on Docker Blog:**

   - Navigate to:
     https://www.docker.com/blog/how-to-make-ai-chatbot-from-scratch/
   - Wait for page to fully load
   - Click the PrismWeave extension icon in toolbar
   - Click "Capture Page" button

3. **Check Output:**

   - Copy the generated markdown
   - Count lines (should be similar to 534 lines from dev-tools)
   - Look for tree structure formatting - should be in code blocks, not tables
   - Check for proper frontmatter at the top

4. **Save Results:**
   - Save the captured markdown as `comparison-browser-ext.md` in the
     browser-extension folder
   - This will allow the comparison script to analyze differences

## Expected Results After Fix:

- **Line count**: Should be ~530-540 lines (close to dev-tools output)
- **Tree structures**: Should appear as proper code blocks with newlines, not as
  tables with `|` separators
- **Frontmatter**: Should include captureDate and tags
- **Content structure**: Should match dev-tools output closely

## Key Things to Check:

1. **Tree formatting**: Look for sections with file/directory structures - they
   should be in code blocks like:

   ```
   ├── Dockerfile
   ├── docker-compose.yml
   └── src/
       ├── main.go
       └── static/
   ```

   NOT as tables like:

   ```
   | ├── Dockerfile |
   | ├── docker-compose.yml |
   ```

2. **Code blocks**: Should have proper language tags and formatting
3. **Headers**: Should be properly formatted with # symbols
4. **Overall length**: Should be much closer to dev-tools output (~534 lines)

## Comparison Test:

After capturing, run:

```bash
cd d:\source\PrismWeave\browser-extension
node comparison-test.js
```

This will analyze the differences between dev-tools and browser extension
outputs.
