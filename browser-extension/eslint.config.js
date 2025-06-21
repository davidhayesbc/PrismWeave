// eslint.config.js - Modern ESLint configuration with TypeScript support
import js from '@eslint/js';
import tseslint from '@typescript-eslint/eslint-plugin';
import tsparser from '@typescript-eslint/parser';

export default [
  js.configs.recommended,
  {
    files: ['**/*.js'],
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
        PrismWeaveBackground: 'readonly',
        PrismWeaveContent: 'readonly',
        PrismWeavePopup: 'readonly',
        PrismWeaveOptions: 'readonly',
        MarkdownConverter: 'readonly',
        GitOperations: 'readonly',
        FileManager: 'readonly',
        ContentExtractor: 'readonly',
        TurndownService: 'readonly',
      },
    },
    rules: {
      // Disable rules that don't work well with browser extensions
      'no-unused-vars': [
        'error',
        {
          varsIgnorePattern:
            '^(PrismWeave|MarkdownConverter|GitOperations|FileManager|ContentExtractor)',
          argsIgnorePattern: '^_',
        },
      ],
      'no-console': 'warn',
      'no-debugger': 'error',
      'prefer-const': 'error',
      'no-var': 'error',
      eqeqeq: 'error',
      curly: 'error',
      semi: ['error', 'always'],
      quotes: ['error', 'single', { allowTemplateLiterals: true }],
      indent: ['error', 2],
      'no-trailing-spaces': 'error',
      'no-multiple-empty-lines': ['error', { max: 2 }],
    },
  },
  {
    // Specific rules for service worker files
    files: ['**/service-worker.js', '**/background/*.js'],
    languageOptions: {
      globals: {
        chrome: 'readonly',
        importScripts: 'readonly',
        self: 'readonly',
      },
    },
  },
  {
    // Specific rules for content scripts
    files: ['**/content/*.js'],
    languageOptions: {
      globals: {
        chrome: 'readonly',
        window: 'readonly',
        document: 'readonly',
      },
    },
  },
  {
    files: ['**/*.ts'],
    languageOptions: {
      parser: tsparser,
      parserOptions: {
        ecmaVersion: 2022,
        sourceType: 'module',
        project: './tsconfig.json',
      },
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
      },
    },
    plugins: {
      '@typescript-eslint': tseslint,
    },
    rules: {
      ...tseslint.configs.recommended.rules,
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/no-non-null-assertion': 'off',
      'prefer-const': 'error',
      'no-var': 'error',
      'no-console': 'warn',
      'no-debugger': 'error',
      eqeqeq: 'error',
      curly: 'error',
      semi: ['error', 'always'],
      quotes: ['error', 'single', { allowTemplateLiterals: true }],
      indent: ['error', 2],
      'no-trailing-spaces': 'error',
      'no-multiple-empty-lines': ['error', { max: 2 }],
    },
  },
  {
    // Ignore build output and dependencies
    ignores: ['dist/**', 'node_modules/**', '*.min.js', 'lib/**'],
  },
];
