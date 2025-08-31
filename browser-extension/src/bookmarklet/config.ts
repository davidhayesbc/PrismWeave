// Bookmarklet Configuration Constants
// Consolidated configuration for bookmarklet components

export const BOOKMARKLET_CONFIG = {
  DEFAULT_INJECTABLE_BASE: 'https://davidhayesbc.github.io/PrismWeave/injectable',
  LOCAL_INJECTABLE_BASE: 'http://localhost:3000/injectable',
  DEFAULT_BRANCH: 'main',
  DEFAULT_FOLDER: 'documents',
  DEFAULT_COMMIT_TEMPLATE: 'PrismWeave: Add {title}',
  UI_Z_INDEX: 999999,
  MAX_CONTENT_LENGTH: 1000000,
  API_TIMEOUT: 30000,
} as const;
