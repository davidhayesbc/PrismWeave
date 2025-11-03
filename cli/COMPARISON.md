# Browser Extension vs CLI - Which Should You Use?

Both the PrismWeave Browser Extension and CLI tool capture web pages as markdown and sync to GitHub. Here's how to choose the right tool for your needs.

## Quick Comparison

| Feature               | Browser Extension    | CLI Tool             |
| --------------------- | -------------------- | -------------------- |
| **Capture Method**    | Active browser tab   | Headless browser     |
| **Best For**          | Interactive browsing | Batch processing     |
| **Setup**             | Install extension    | npm install + config |
| **Usage**             | Click extension icon | Command line         |
| **Batch Processing**  | Manual               | Automated            |
| **Automation**        | Limited              | Full support         |
| **Server Use**        | No                   | Yes                  |
| **CI/CD Integration** | No                   | Yes                  |

## Use the Browser Extension When...

### ✅ You're actively browsing

- Reading articles and want to save them
- Doing research and capturing sources
- Building a personal knowledge base interactively

### ✅ You want simplicity

- One-click capture while browsing
- Visual feedback during capture
- No command line needed

### ✅ You need context

- Capture pages as you read them
- Select specific content on the page
- Save pages in their current state

**Example Workflow:**

```
1. Browse to interesting article
2. Click PrismWeave extension icon
3. Content automatically saved to GitHub
4. Continue browsing
```

## Use the CLI Tool When...

### ✅ You have a list of URLs

- Batch processing multiple articles
- Importing existing bookmarks
- Scheduled documentation captures

### ✅ You need automation

- Cron jobs for regular captures
- CI/CD pipeline integration
- Server-side processing
- Scripted workflows

### ✅ You want programmatic control

- Custom processing scripts
- Integration with other tools
- Automated documentation systems

**Example Workflow:**

```bash
# Create list of URLs
cat > urls.txt << EOF
https://article1.com
https://article2.com
https://article3.com
EOF

# Batch capture
prismweave capture --file urls.txt

# Or automate with cron
0 2 * * * prismweave capture --file ~/daily-reading.txt
```

## Common Scenarios

### Scenario 1: Daily News Reading

**Browser Extension** ✓

- You're browsing news sites
- Click to save interesting articles
- One-off, interactive captures

**CLI** ✗

- Overkill for interactive use
- Slower for one-off captures

### Scenario 2: Documentation Import

**CLI** ✓

- You have 50+ documentation URLs
- Want to capture them all at once
- Need consistent processing

**Browser Extension** ✗

- Too manual for many URLs
- Time-consuming
- Prone to errors

### Scenario 3: Research Project

**Both!** ✓

- Use browser extension while researching
- Use CLI to process reading list
- Best of both worlds

### Scenario 4: Team Documentation

**CLI** ✓

- Automated daily captures
- CI/CD integration
- Server deployment
- Consistent processing

**Browser Extension** ✗

- Individual use only
- No automation
- Not server-deployable

### Scenario 5: Personal Reading List

**Browser Extension** ✓

- Capture as you read
- Simple and quick
- No scripting needed

**CLI** ~ (Optional)

- Could batch process saved bookmarks
- Useful if importing from elsewhere

## Can You Use Both?

**Yes!** They work together perfectly:

1. **Interactive + Batch**: Use browser extension while browsing, CLI for batch imports
2. **Shared Repository**: Both save to the same GitHub repo
3. **Consistent Output**: Both use the same markdown conversion
4. **Same Organization**: Both use smart folder categorization

## Technical Considerations

### Browser Extension

- **Pros**: Native browser integration, active page access, visual feedback
- **Cons**: Manual operation, no batch processing, requires browser
- **Setup Time**: 5 minutes
- **Learning Curve**: Minimal

### CLI Tool

- **Pros**: Automation, batch processing, CI/CD ready, server-friendly
- **Cons**: Command line required, steeper learning curve
- **Setup Time**: 10-15 minutes
- **Learning Curve**: Moderate

## Migration Path

Start simple, scale up as needed:

1. **Week 1-2**: Use browser extension to get familiar
2. **Week 3-4**: Try CLI for your first batch import
3. **Month 2+**: Automate regular captures with CLI
4. **Ongoing**: Use both for their strengths

## Setup Complexity

### Browser Extension Setup

```bash
# 1. Build extension
cd browser-extension
npm install && npm run build

# 2. Load in browser
# Chrome -> Extensions -> Load Unpacked -> browser-extension/dist

# 3. Configure in extension
# Click extension icon -> Settings -> Enter GitHub token & repo

# Done! ✓ Start capturing
```

### CLI Setup

```bash
# 1. Install CLI
cd cli
npm install && npm run build
npm link

# 2. Configure
prismweave config --set githubToken=your_token
prismweave config --set githubRepo=owner/repo

# 3. Test
prismweave config --test

# Done! ✓ Start capturing
```

## Performance Comparison

### Single URL Capture

- **Browser Extension**: ~2-3 seconds (active tab)
- **CLI**: ~5-8 seconds (headless browser startup)

### Batch Capture (10 URLs)

- **Browser Extension**: ~20-30 seconds (manual)
- **CLI**: ~60-80 seconds (automated)

### Batch Capture (100 URLs)

- **Browser Extension**: ~200-300 seconds (very manual!)
- **CLI**: ~600-800 seconds (unattended)

## Decision Matrix

Choose **Browser Extension** if:

- ☑ Primarily interactive browsing
- ☑ Capture less than 10 URLs per session
- ☑ Want visual feedback
- ☑ Don't need automation
- ☑ Prefer GUI over command line

Choose **CLI** if:

- ☑ Batch processing needed
- ☑ Automation required
- ☑ Server deployment
- ☑ CI/CD integration
- ☑ Comfortable with command line
- ☑ Processing URL lists

Choose **Both** if:

- ☑ Active browsing + batch processing
- ☑ Personal use + team automation
- ☑ Want maximum flexibility

## Getting Started

### Browser Extension

See: [browser-extension/README.md](../browser-extension/README.md)

### CLI Tool

See: [cli/QUICKSTART.md](QUICKSTART.md)

## Questions?

- **Browser Extension Issues**: See browser-extension docs
- **CLI Issues**: See cli/README.md or cli/QUICKSTART.md
- **General Questions**: GitHub Issues

Happy capturing! 🎉
