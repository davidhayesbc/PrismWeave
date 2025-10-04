# Changelog

All notable changes to the PrismWeave CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- [ ] Progress bars with detailed statistics
- [ ] Parallel processing for batch captures
- [ ] Custom CSS selectors for content extraction
- [ ] Support for authentication (login before capture)
- [ ] Screenshot capture alongside markdown
- [ ] PDF export option
- [ ] Local SQLite database for metadata
- [ ] Search functionality across captured documents
- [ ] Auto-tagging using AI
- [ ] Browser extension sync/import

## [0.1.0] - 2025-01-15

### Added
- Initial release of PrismWeave CLI
- Single URL capture with `prismweave capture URL`
- Batch processing with `prismweave capture --file urls.txt`
- Configuration management with `prismweave config`
- Headless browser capture using Puppeteer
- HTML to Markdown conversion using Turndown
- GitHub integration for automated commits
- Smart file organization by content type
- YAML frontmatter generation with metadata
- Dry-run mode for content preview
- Custom timeout support
- Terminal spinners and colored output
- Configuration persistence in `~/.prismweave/config.json`

### Features

#### Core Functionality
- **Content Capture**: Extract clean content from any web page
- **Markdown Conversion**: Convert HTML to well-formatted markdown
- **GitHub Integration**: Automatically commit to repository
- **Batch Processing**: Process multiple URLs from a file
- **Smart Organization**: Auto-categorize files by keywords

#### Command Line Interface
- `capture` command with URL or file input
- `config` command for settings management
- `--dry-run` flag for preview mode
- `--timeout` option for slow sites
- `--message` option for custom commit messages
- `--version` flag for version info
- `--help` flag for usage information

#### Configuration
- Persistent storage in user home directory
- GitHub token and repository settings
- Validation with `--test` option
- Support for both public and private repositories

#### Code Sharing
- 60%+ code reuse with browser extension
- Shared markdown converter core
- Shared file manager for GitHub operations
- Shared type definitions

### Documentation
- Comprehensive README.md (400+ lines)
- Quick start guide (QUICKSTART.md)
- Browser extension comparison (COMPARISON.md)
- Troubleshooting guide (TROUBLESHOOTING.md)
- Setup checklist (CHECKLIST.md)
- Implementation summary (IMPLEMENTATION_SUMMARY.md)
- Windows and Unix setup scripts

### Technical Details
- TypeScript 5.8.3 with strict mode
- ES2022 target with Node.js module resolution
- Puppeteer 22.0.0 for headless browsing
- Commander.js 12.0.0 for CLI framework
- Chalk 5.3.0 for colored terminal output
- Ora 8.0.1 for progress spinners
- Turndown 7.2.0 for markdown conversion

### Dependencies
```json
{
  "puppeteer": "^22.0.0",
  "commander": "^12.0.0",
  "chalk": "^5.3.0",
  "ora": "^8.0.1",
  "turndown": "^7.2.0"
}
```

### Requirements
- Node.js 18.0.0 or higher
- Git (for version control)
- GitHub account and personal access token
- Internet connection for web page capture

### Known Limitations
- Single-threaded processing (captures are sequential)
- Requires GitHub for storage (no local-only mode yet)
- Limited customization of content extraction
- No built-in authentication support
- Cannot handle sites requiring JavaScript interaction
- Rate limited by GitHub API (5000 requests/hour)

### Performance
- Browser startup: ~3-5 seconds per capture
- Typical page capture: 5-10 seconds
- Batch processing: ~10-15 seconds per URL
- Memory usage: ~300MB for Chromium + ~50MB per page

### File Organization
Files are automatically organized into folders:
- `documents/` - General web content
- `tech/` - Technical articles and documentation
- `tutorial/` - How-to guides and tutorials
- `news/` - News articles and updates
- `business/` - Business and finance content
- `research/` - Research papers and academic content
- `design/` - Design articles and resources
- `tools/` - Tool documentation and guides
- `reference/` - Reference documentation and specs

### Markdown Format
Generated markdown includes:
- YAML frontmatter with metadata (title, URL, domain, tags, etc.)
- Clean content with proper heading hierarchy
- Preserved links (converted to markdown format)
- Code blocks with syntax preservation
- Lists (ordered and unordered)
- Blockquotes
- Tables (when applicable)

## Version History

### Version Numbering
- **Major version (X.0.0)**: Breaking changes or significant new features
- **Minor version (0.X.0)**: New features, backward compatible
- **Patch version (0.0.X)**: Bug fixes, minor improvements

### Upgrade Path
Currently on first version. Future upgrades:
```bash
cd cli
git pull origin main
npm install
npm run build
```

## Contributing

### How to Contribute
1. Check planned features in [Unreleased] section
2. Create issue for discussion
3. Fork repository
4. Create feature branch
5. Implement changes with tests
6. Update documentation
7. Submit pull request

### Contribution Guidelines
- Follow existing code style
- Add tests for new features
- Update documentation
- Update this CHANGELOG
- Follow semantic versioning

## Future Roadmap

### Version 0.2.0 (Planned)
- Parallel processing for faster batch captures
- Progress bars with detailed statistics
- Custom CSS selectors for extraction
- Local SQLite database for metadata

### Version 0.3.0 (Planned)
- Authentication support (login workflows)
- Screenshot capture alongside markdown
- PDF export functionality
- Browser extension import/sync

### Version 1.0.0 (Future)
- Full feature parity with browser extension
- Comprehensive test suite
- Production-ready stability
- Complete API documentation

## Support

### Getting Help
- Read [README.md](README.md) for complete documentation
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- Search existing GitHub issues
- Create new issue with details

### Reporting Bugs
Include in bug reports:
- PrismWeave CLI version (`prismweave --version`)
- Node.js version (`node --version`)
- Operating system
- Full error message
- Steps to reproduce
- Expected vs actual behavior

### Requesting Features
Include in feature requests:
- Use case description
- Why it's needed
- Proposed solution
- Alternative solutions considered
- Willingness to contribute

---

**Legend:**
- `Added`: New features
- `Changed`: Changes to existing functionality
- `Deprecated`: Features to be removed in future
- `Removed`: Features removed in this version
- `Fixed`: Bug fixes
- `Security`: Security vulnerability fixes
