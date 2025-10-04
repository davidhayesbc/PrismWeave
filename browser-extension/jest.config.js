// Jest configuration for PrismWeave Browser Extension
module.exports = {
  // Use ts-jest preset for TypeScript support
  preset: 'ts-jest',

  // Test environment setup
  testEnvironment: 'jsdom',

  // Root directory for tests
  rootDir: '.',

  // Test file patterns
  testMatch: ['<rootDir>/src/**/__tests__/**/*.test.{js,ts}', '<rootDir>/tests/**/*.test.{js,ts}'],
  // Transform configuration for TypeScript and JavaScript
  transform: {
    '^.+\\.ts$': [
      'ts-jest',
      {
        tsconfig: 'tsconfig.test.json',
      },
    ],
    '^.+\\.js$': [
      'babel-jest',
      {
        presets: [['@babel/preset-env', { targets: { node: 'current' } }]],
      },
    ],
  },

  // Module file extensions
  moduleFileExtensions: ['ts', 'js', 'json'],

  // Coverage configuration - disabled (using c8 external coverage)
  collectCoverage: false,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  collectCoverageFrom: [
    'src/**/*.{js,ts}',
    '!src/libs/**',
    '!src/**/*.min.js',
    '!src/bookmarklet/templates/**',
    '!src/bookmarklet/examples/**',
    '!**/node_modules/**',
    '!**/*.d.ts',
  ],

  // Skip coverage collection for problematic files
  coveragePathIgnorePatterns: [
    'node_modules',
    'src/libs/',
    'src/bookmarklet/examples/',
    'src/bookmarklet/templates/',
  ],

  // Coverage thresholds
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
  // Module name mapping for browser APIs and TypeScript imports
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    // Handle TypeScript imports with .js extensions - more specific to avoid JSDOM conflicts
    '^(\\.{1,2}/.+)\\.js$': '$1',
    '^(src/.+)\\.js$': '$1',
  },

  // Setup files
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],

  // Explicitly configure test environment globals
  testEnvironmentOptions: {
    customExportConditions: ['node', 'node-addons'],
  },

  // Configure globals
  setupFiles: ['<rootDir>/jest.setup.js'],

  // Test timeout
  testTimeout: 10000,

  // Verbose output - controlled by TEST_DEBUG environment variable
  verbose: process.env.TEST_DEBUG === 'true',

  // Silent mode - suppress console output unless debug mode
  silent: process.env.TEST_DEBUG !== 'true',

  // Clear mocks between tests
  clearMocks: true,

  // Restore mocks after each test
  restoreMocks: true,

  // Limit workers for stability
  maxWorkers: 1,

  // Globals configuration for test logging
  globals: {
    TEST_DEBUG: process.env.TEST_DEBUG === 'true',
    TEST_LOG_LEVEL: process.env.TEST_LOG_LEVEL || 'ERROR',
  },
};
