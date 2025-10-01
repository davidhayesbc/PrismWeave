# PrismWeave CLI - Setup & Usage Checklist

Quick checklist to get started with the PrismWeave CLI.

## ✅ Installation Checklist

- [ ] **Node.js installed** (v18 or higher)
  ```bash
  node --version  # Should be 18+
  ```

- [ ] **Git installed** (for cloning and version control)
  ```bash
  git --version
  ```

- [ ] **Navigate to CLI directory**
  ```bash
  cd cli
  ```

- [ ] **Install dependencies**
  ```bash
  npm install
  ```

- [ ] **Build the project**
  ```bash
  npm run build
  ```

- [ ] **Install globally (optional but recommended)**
  ```bash
  npm link
  ```

- [ ] **Verify installation**
  ```bash
  prismweave --version
  prismweave --help
  ```

## ✅ Configuration Checklist

- [ ] **Get GitHub Personal Access Token**
  - Go to: https://github.com/settings/tokens
  - Click "Generate new token" → "Generate new token (classic)"
  - Name: "PrismWeave CLI"
  - Scopes needed:
    - [x] `repo` (for private repos) OR
    - [x] `public_repo` (for public repos only)
  - Click "Generate token"
  - **Copy token immediately** (you won't see it again!)

- [ ] **Configure GitHub token**
  ```bash
  prismweave config --set githubToken=ghp_your_token_here
  ```

- [ ] **Configure repository** (format: owner/repo)
  ```bash
  prismweave config --set githubRepo=yourusername/yourrepo
  ```

- [ ] **Test connection**
  ```bash
  prismweave config --test
  ```
  - Should show: ✅ GitHub connection test successful

- [ ] **View configuration**
  ```bash
  prismweave config --list
  ```

## ✅ First Capture Checklist

- [ ] **Test with a simple URL**
  ```bash
  prismweave capture https://example.com
  ```

- [ ] **Verify output**
  - Check terminal for success message
  - Note the file path shown (e.g., `documents/2025-01-15-example.com-...`)

- [ ] **Check GitHub repository**
  - Go to: https://github.com/yourusername/yourrepo
  - Look in `documents/` folder
  - Find your captured file
  - Verify markdown content looks good

- [ ] **View commit history**
  - Check recent commits in your repository
  - Should see commit like: "Capture: Example Domain"

## ✅ Advanced Usage Checklist

- [ ] **Try dry-run mode**
  ```bash
  prismweave capture https://example.com --dry-run
  ```
  - Previews content without saving to GitHub

- [ ] **Test custom commit message**
  ```bash
  prismweave capture https://example.com --message "My custom commit message"
  ```

- [ ] **Create URL list file**
  ```bash
  echo "https://example.com" > my-urls.txt
  echo "https://github.com" >> my-urls.txt
  ```

- [ ] **Test batch processing**
  ```bash
  prismweave capture --file my-urls.txt
  ```

- [ ] **Test with timeout adjustment**
  ```bash
  prismweave capture https://slow-site.com --timeout 60000
  ```

## ✅ Verification Checklist

- [ ] **Check captured content quality**
  - Open captured markdown file on GitHub
  - Verify:
    - [ ] Title is correct
    - [ ] URL is in frontmatter
    - [ ] Content is readable
    - [ ] Markdown formatting looks good
    - [ ] Images are referenced (if any)
    - [ ] Links are working

- [ ] **Check file organization**
  - Files should be in appropriate folders:
    - `documents/` - General content
    - `tech/` - Technical articles
    - `tutorial/` - How-to guides
    - `news/` - News articles
    - `business/` - Business content
    - `research/` - Research papers
    - `design/` - Design articles
    - `tools/` - Tool documentation
    - `reference/` - Reference docs

- [ ] **Verify Git commits**
  - Commits should have:
    - [ ] Meaningful commit messages
    - [ ] Single file per commit
    - [ ] Proper timestamps

## ✅ Troubleshooting Checklist

If something goes wrong:

- [ ] **Check error message**
  - Read the error carefully
  - Note the error code (if any)

- [ ] **Verify configuration**
  ```bash
  prismweave config --list
  prismweave config --test
  ```

- [ ] **Check GitHub token**
  - Still valid? (tokens can expire)
  - Has correct scopes? (`repo` or `public_repo`)
  - Can be regenerated at: https://github.com/settings/tokens

- [ ] **Check repository access**
  - Repository exists?
  - You have write access?
  - Repository name format is `owner/repo`?

- [ ] **Check internet connection**
  ```bash
  ping github.com
  ```

- [ ] **Try with verbose output**
  ```bash
  prismweave capture URL --verbose
  ```

- [ ] **Check disk space**
  - Puppeteer downloads Chromium (~300MB)
  - Need space for temporary files

- [ ] **Review troubleshooting guide**
  - See: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## ✅ Documentation Checklist

Have you read:

- [ ] **README.md** - Complete documentation
- [ ] **QUICKSTART.md** - 5-minute getting started
- [ ] **COMPARISON.md** - Browser extension vs CLI
- [ ] **TROUBLESHOOTING.md** - Common issues and solutions
- [ ] **IMPLEMENTATION_SUMMARY.md** - Technical architecture

## ✅ Development Checklist

For contributors/developers:

- [ ] **Run tests** (when implemented)
  ```bash
  npm test
  ```

- [ ] **Check code style**
  ```bash
  npm run lint
  ```

- [ ] **Build before committing**
  ```bash
  npm run build
  ```

- [ ] **Test changes locally**
  ```bash
  npm start -- capture TEST_URL
  ```

- [ ] **Update documentation**
  - Update README.md if adding features
  - Update TROUBLESHOOTING.md if fixing bugs
  - Add examples for new functionality

## ✅ Regular Maintenance Checklist

- [ ] **Update dependencies** (periodically)
  ```bash
  npm update
  npm audit fix
  ```

- [ ] **Check for CLI updates**
  ```bash
  cd cli
  git pull origin main
  npm install
  npm run build
  ```

- [ ] **Rotate GitHub tokens** (every 6-12 months)
  - Generate new token
  - Update configuration
  - Delete old token

- [ ] **Clean up old files** (if needed)
  - Review captured documents
  - Archive or delete outdated content

## 🎉 Success Indicators

You're all set when:

- ✅ `prismweave --version` shows version number
- ✅ `prismweave config --test` shows connection success
- ✅ Test capture completes without errors
- ✅ File appears in GitHub repository
- ✅ Markdown content looks clean and readable
- ✅ Commit appears in repository history

## 📚 Quick Reference

### Essential Commands

```bash
# Configuration
prismweave config --set githubToken=TOKEN
prismweave config --set githubRepo=owner/repo
prismweave config --test

# Capture
prismweave capture URL
prismweave capture --file urls.txt
prismweave capture URL --dry-run

# Help
prismweave --help
prismweave capture --help
prismweave config --help
```

### Common Workflows

**Quick capture:**
```bash
prismweave capture https://interesting-article.com
```

**Preview before saving:**
```bash
prismweave capture https://article.com --dry-run
```

**Batch processing:**
```bash
prismweave capture --file reading-list.txt
```

**Slow site:**
```bash
prismweave capture https://slow-site.com --timeout 60000
```

---

**Next Steps:**
1. Start with QUICKSTART.md for 5-minute setup
2. Use this checklist to verify everything works
3. Read README.md for complete feature documentation
4. Refer to TROUBLESHOOTING.md if you encounter issues

Happy capturing! 📝✨
