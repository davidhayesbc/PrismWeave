# 🧪 PrismWeave CLI Test Quick Reference

## 🚀 Quick Commands

```bash
# Install and run tests
cd cli
npm install
npm test

# Watch mode (development)
npm run test:watch

# Coverage report
npm run test:coverage
```

## 📊 Test Files Overview

| File | Tests | Purpose |
|------|-------|---------|
| `config.test.ts` | 25+ | Configuration management |
| `file-manager.test.ts` | 35+ | GitHub & file operations |
| `markdown-converter.test.ts` | 40+ | HTML to Markdown |
| `content-extraction.test.ts` | 30+ | Web content extraction |

## 🎯 Coverage Goals

- **All metrics**: 60% minimum
- **Expected**: 70-90% actual

## 📁 File Structure

```
cli/
├── jest.config.js          # Jest config
├── tests/
│   ├── config.test.ts
│   ├── file-manager.test.ts
│   ├── markdown-converter.test.ts
│   └── content-extraction.test.ts
└── coverage/               # After test:coverage
    └── lcov-report/
        └── index.html      # View in browser
```

## 🔧 Key Features Tested

### ConfigManager
- ✅ Load/save configuration
- ✅ Validate GitHub settings
- ✅ Handle file errors

### FileManager
- ✅ Generate filenames
- ✅ Classify content
- ✅ GitHub API operations
- ✅ PDF handling

### MarkdownConverter
- ✅ HTML to Markdown
- ✅ Complex structures
- ✅ Statistics calculation

### ContentExtraction
- ✅ Extract metadata
- ✅ Analyze content
- ✅ Detect blogs
- ✅ Quality scoring

## 🐛 Troubleshooting

### Module errors?
- Check `.js` extensions in imports
- Verify `"type": "module"` in package.json

### Tests not found?
- Ensure test files in `tests/` directory
- Check file names end with `.test.ts`

### Mocks not working?
- Call `jest.clearAllMocks()` in `beforeEach`
- Verify mock before import

## 📚 Documentation

- **Complete Guide**: `TESTING_GUIDE.md`
- **Implementation**: `TEST_IMPLEMENTATION_SUMMARY.md`
- **Test Details**: `tests/README.md`

## ✨ Pro Tips

1. Use watch mode during development
2. Run specific tests: `npm test -- -t "test name"`
3. Check coverage regularly: `npm run test:coverage`
4. Review HTML report for detailed coverage
5. Mock all external dependencies

## 🎉 Ready to Go!

Everything is set up and ready. Just run:

```bash
npm install && npm test
```

Happy testing! 🚀
