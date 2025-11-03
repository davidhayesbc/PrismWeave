# PrismWeave CLI - Quick Start Guide

Get started with PrismWeave CLI in 5 minutes!

## Step 1: Installation

```bash
# Navigate to CLI directory
cd cli

# Install dependencies
npm install

# Build the project
npm run build

# (Optional) Install globally
npm link
```

## Step 2: Configure GitHub

You need a GitHub Personal Access Token to save captured content.

### Create GitHub Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "PrismWeave CLI")
4. Select scopes:
   - `repo` (for private repositories)
   - OR `public_repo` (for public repositories only)
5. Click "Generate token"
6. Copy the token (you won't see it again!)

### Configure the CLI

```bash
# Set your GitHub token
prismweave config --set githubToken=ghp_your_token_here

# Set your GitHub repository (replace with your repo)
prismweave config --set githubRepo=yourusername/your-repo

# Verify configuration
prismweave config --list

# Test the connection
prismweave config --test
```

## Step 3: Capture Your First Page

### Single URL

```bash
prismweave capture https://example.com/article
```

### Multiple URLs

Create a file with URLs:

```bash
# Create urls.txt with your favorite articles
cat > urls.txt << EOF
https://dev.to/example-article
https://github.blog/example-post
https://medium.com/@user/example-story
EOF

# Capture all URLs
prismweave capture --file urls.txt
```

## Step 4: View Your Captured Content

Your captured content is automatically committed to GitHub in the `documents/` folder, organized by category:

```
your-repo/
├── documents/
│   ├── tech/
│   │   └── 2025-01-15-dev-to-example-article.md
│   ├── business/
│   ├── tutorial/
│   └── unsorted/
```

Visit your GitHub repository to see the captured markdown files!

## Common Options

### Dry Run (Preview)

Preview what will be captured without saving:

```bash
prismweave capture https://example.com --dry-run
```

### Custom Timeout

For slow-loading pages:

```bash
prismweave capture https://slow-site.com --timeout 60000
```

### Exclude Images

Save bandwidth and space:

```bash
prismweave capture https://example.com --no-images
```

## Troubleshooting

### "GitHub token and repository are required"

You forgot to configure GitHub settings. Run:

```bash
prismweave config --set githubToken=your_token
prismweave config --set githubRepo=owner/repo
```

### "Browser launch failed"

Install Chromium manually:

```bash
npx puppeteer browsers install chrome
```

### "Connection timeout"

Increase the timeout:

```bash
prismweave capture URL --timeout 60000
```

## Next Steps

- Read the full [README.md](README.md) for all features
- Configure additional options with `prismweave config`
- Create automated scripts for regular captures
- Integrate with your documentation workflow

## Examples

### Tech Blog Capture

```bash
# Create a list of tech blogs
cat > tech-blogs.txt << EOF
https://martinfowler.com/articles/
https://blog.codinghorror.com/
https://www.joelonsoftware.com/
EOF

prismweave capture --file tech-blogs.txt
```

### Single Article Quick Capture

```bash
# Just paste the URL
prismweave capture "https://www.example.com/interesting-article"
```

### Preview Before Saving

```bash
# Check what will be captured
prismweave capture https://example.com --dry-run
```

## Getting Help

```bash
# Show all commands
prismweave --help

# Show capture command help
prismweave capture --help

# Show config command help
prismweave config --help
```

## Support

For issues or questions:

- GitHub Issues: https://github.com/yourusername/PrismWeave/issues
- Documentation: See [README.md](README.md)

Happy capturing! 🎉
