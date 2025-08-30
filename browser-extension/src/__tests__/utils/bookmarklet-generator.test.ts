/**
 * Tests for EmbeddedBookmarkletGenerator
 * Tests the PAT-based personal bookmarklet generation
 */

import {
  EmbeddedBookmarkletGenerator,
  type IPATConfiguration,
} from '../../utils/embedded-bookmarklet-generator';

describe('EmbeddedBookmarkletGenerator', () => {
  // Valid test configuration
  const validConfig: IPATConfiguration = {
    githubToken: 'ghp_1234567890abcdef1234567890abcdef12345678',
    githubRepo: 'testuser/testrepo',
    defaultFolder: 'documents',
    commitMessage: 'Add captured content via PrismWeave',
  };

  describe('generatePersonalBookmarklet', () => {
    test('should generate a valid bookmarklet with minimal config', () => {
      const minimalConfig: IPATConfiguration = {
        githubToken: 'ghp_1234567890abcdef1234567890abcdef12345678',
        githubRepo: 'testuser/testrepo',
      };

      const bookmarklet = EmbeddedBookmarkletGenerator.generatePersonalBookmarklet(minimalConfig);

      expect(bookmarklet).toContain('javascript:');
      expect(bookmarklet).toContain('atob(');
      expect(bookmarklet).toContain('JSON.parse');
    });

    test('should generate a valid bookmarklet with full config', () => {
      const bookmarklet = EmbeddedBookmarkletGenerator.generatePersonalBookmarklet(validConfig);

      expect(bookmarklet).toContain('javascript:');
      expect(bookmarklet).toContain('atob(');
      expect(bookmarklet).toContain('JSON.parse');
      expect(bookmarklet).toContain('api.github.com');
    });

    test('should embed configuration as base64', () => {
      const bookmarklet = EmbeddedBookmarkletGenerator.generatePersonalBookmarklet(validConfig);

      expect(bookmarklet).toContain('atob(');
      // Should not contain plaintext sensitive data
      expect(bookmarklet).not.toContain(validConfig.githubToken);
    });

    test('should handle special characters in configuration', () => {
      const specialConfig: IPATConfiguration = {
        githubToken: 'ghp_1234567890abcdef1234567890abcdef12345678',
        githubRepo: 'user/repo-with-special-chars',
        defaultFolder: 'documents/special-folder',
        commitMessage: 'Add "content" with special & characters',
      };

      const bookmarklet = EmbeddedBookmarkletGenerator.generatePersonalBookmarklet(specialConfig);

      expect(bookmarklet).toContain('javascript:');
      expect(bookmarklet).toContain('atob(');
    });

    test('should include content extraction logic', () => {
      const bookmarklet = EmbeddedBookmarkletGenerator.generatePersonalBookmarklet(validConfig);

      expect(bookmarklet).toContain('document.title');
      expect(bookmarklet).toContain('window.location.href');
      expect(bookmarklet).toContain('querySelector');
    });

    test('should include GitHub API integration', () => {
      const bookmarklet = EmbeddedBookmarkletGenerator.generatePersonalBookmarklet(validConfig);

      expect(bookmarklet).toContain('api.github.com');
      expect(bookmarklet).toContain('fetch');
      expect(bookmarklet).toContain('contents');
    });
  });

  describe('generateBookmarkletPage', () => {
    test('should generate a complete HTML page', () => {
      const page = EmbeddedBookmarkletGenerator.generateBookmarkletPage(validConfig);

      expect(page).toContain('<!DOCTYPE html>');
      expect(page).toContain('<html');
      expect(page).toContain('</html>');
      expect(page).toContain('<head>');
      expect(page).toContain('<body>');
    });

    test('should include the bookmarklet in the page', () => {
      const page = EmbeddedBookmarkletGenerator.generateBookmarkletPage(validConfig);

      expect(page).toContain('javascript:');
      expect(page).toContain('href=');
    });
  });

  describe('validateConfiguration', () => {
    test('should validate correct configuration', () => {
      const result = EmbeddedBookmarkletGenerator.validateConfiguration(validConfig);

      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    test('should require GitHub token', () => {
      const invalidConfig = { ...validConfig };
      delete (invalidConfig as any).githubToken;

      const result = EmbeddedBookmarkletGenerator.validateConfiguration(invalidConfig);

      expect(result.valid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });
  });

  describe('extractConfigFromBookmarklet', () => {
    test('should extract configuration from valid bookmarklet', () => {
      const originalConfig = validConfig;
      const bookmarklet = EmbeddedBookmarkletGenerator.generatePersonalBookmarklet(originalConfig);

      const extractedConfig =
        EmbeddedBookmarkletGenerator.extractConfigFromBookmarklet(bookmarklet);

      expect(extractedConfig).toBeTruthy();
      expect(extractedConfig?.githubToken).toBe(originalConfig.githubToken);
      expect(extractedConfig?.githubRepo).toBe(originalConfig.githubRepo);
    });

    test('should return null for invalid bookmarklet', () => {
      const invalidBookmarklet = 'javascript:alert("not a valid bookmarklet");';

      const extractedConfig =
        EmbeddedBookmarkletGenerator.extractConfigFromBookmarklet(invalidBookmarklet);

      expect(extractedConfig).toBeNull();
    });
  });

  describe('generateSetupForm', () => {
    test('should generate valid HTML form', () => {
      const form = EmbeddedBookmarkletGenerator.generateSetupForm();

      expect(form).toContain('<!DOCTYPE html>');
      expect(form).toContain('<form');
      expect(form).toContain('<input');
      expect(form).toContain('githubToken');
      expect(form).toContain('githubRepo');
    });
  });
});
