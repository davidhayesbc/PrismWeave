// eslint.config.js - Modern ESLint configuration
import js from '@eslint/js';

export default [
  js.configs.recommended,
  {
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'script',
      globals: {
        // Browser extension globals
        chrome: 'readonly',
        browser: 'readonly',
        
        // Browser globals
        window: 'readonly',
        document: 'readonly',
        console: 'readonly',
        URL: 'readonly',
        fetch: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        setInterval: 'readonly',
        clearInterval: 'readonly',
        
        // Service Worker globals
        importScripts: 'readonly',
        self: 'readonly',
        
        // Our extension classes
        DocTrackerBackground: 'readonly',
        DocTrackerContent: 'readonly',
        DocTrackerPopup: 'readonly',
        DocTrackerOptions: 'readonly',
        MarkdownConverter: 'readonly',
        GitOperations: 'readonly',
        FileManager: 'readonly',
        ContentExtractor: 'readonly',
        TurndownService: 'readonly'
      }
    },
    rules: {
      // Disable rules that don't work well with browser extensions
      'no-unused-vars': ['error', { 
        'varsIgnorePattern': '^(DocTracker|MarkdownConverter|GitOperations|FileManager|ContentExtractor)',
        'argsIgnorePattern': '^_'
      }],
      'no-console': 'warn',
      'no-debugger': 'error',
      'prefer-const': 'error',
      'no-var': 'error',
      'eqeqeq': 'error',
      'curly': 'error',
      'semi': ['error', 'always'],
      'quotes': ['error', 'single', { 'allowTemplateLiterals': true }],
      'indent': ['error', 2],
      'no-trailing-spaces': 'error',
      'no-multiple-empty-lines': ['error', { 'max': 2 }]
    }
  },
  {
    // Specific rules for service worker files
    files: ['**/service-worker.js', '**/background/*.js'],
    languageOptions: {
      globals: {
        chrome: 'readonly',
        importScripts: 'readonly',
        self: 'readonly'
      }
    }
  },
  {
    // Specific rules for content scripts
    files: ['**/content/*.js'],
    languageOptions: {
      globals: {
        chrome: 'readonly',
        window: 'readonly',
        document: 'readonly'
      }
    }
  },
  {
    // Ignore build output and dependencies
    ignores: [
      'dist/**',
      'node_modules/**',
      '*.min.js',
      'lib/**'
    ]
  }
];
