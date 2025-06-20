// Unit tests for GitOperations
// Testing GitHub API integration, repository validation, and file operations

describe('GitOperations', () => {
  let gitOps;

  beforeEach(() => {
    const GitOperationsClass = require('../../src/utils/git-operations.js');
    gitOps = new GitOperationsClass();
    jest.clearAllMocks();
    fetch.mockClear();
  });

  describe('Initialization', () => {
    test('should initialize with correct API base', () => {
      expect(gitOps.apiBase).toBe('https://api.github.com');
    });

    test('should initialize successfully with valid settings', async () => {
      const settings = testUtils.createMockSettings();
      
      await expect(gitOps.initialize(settings)).resolves.not.toThrow();
      expect(gitOps.settings).toEqual(settings);
    });

    test('should throw error when GitHub token is missing', async () => {
      const settings = testUtils.createMockSettings({
        githubToken: ''
      });

      await expect(gitOps.initialize(settings)).rejects.toThrow('GitHub token not configured');
    });

    test('should throw error when repository path is missing', async () => {
      const settings = testUtils.createMockSettings({
        githubRepo: '',
        repositoryPath: ''
      });

      await expect(gitOps.initialize(settings)).rejects.toThrow('Repository path not configured');
    });

    test('should normalize repository path from githubRepo', async () => {
      const settings = testUtils.createMockSettings({
        githubRepo: 'owner/repo',
        repositoryPath: ''
      });

      await gitOps.initialize(settings);
      expect(gitOps.settings.repositoryPath).toBe('owner/repo');
    });
  });

  describe('GitHub API Connection Testing', () => {
    beforeEach(async () => {
      const settings = testUtils.createMockSettings();
      await gitOps.initialize(settings);
    });

    test('should test connection successfully', async () => {
      fetch.mockResolvedValueOnce(testUtils.mockGitHubAPI.success());

      const result = await gitOps.testConnection();

      expect(result.success).toBe(true);
      expect(fetch).toHaveBeenCalledWith(
        'https://api.github.com/user',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'token test-token'
          })
        })
      );
    });

    test('should handle connection failure', async () => {
      fetch.mockResolvedValueOnce(testUtils.mockGitHubAPI.error(401, 'Unauthorized'));

      const result = await gitOps.testConnection();

      expect(result.success).toBe(false);
      expect(result.error).toContain('Unauthorized');
    });

    test('should handle network errors', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      const result = await gitOps.testConnection();

      expect(result.success).toBe(false);
      expect(result.error).toContain('Network error');
    });
  });

  describe('Repository Validation', () => {
    beforeEach(async () => {
      const settings = testUtils.createMockSettings();
      await gitOps.initialize(settings);
    });

    test('should validate repository successfully', async () => {
      const mockRepo = {
        name: 'repo',
        full_name: 'owner/repo',
        permissions: { push: true, pull: true }
      };
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockRepo)
      });

      const result = await gitOps.validateRepository();

      expect(result.success).toBe(true);
      expect(result.hasWrite).toBe(true);
      expect(fetch).toHaveBeenCalledWith(
        'https://api.github.com/repos/owner/repo',
        expect.any(Object)
      );
    });

    test('should detect repository without write access', async () => {
      const mockRepo = {
        name: 'repo',
        full_name: 'owner/repo',
        permissions: { push: false, pull: true }
      };
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockRepo)
      });

      const result = await gitOps.validateRepository();

      expect(result.success).toBe(true);
      expect(result.hasWrite).toBe(false);
    });

    test('should handle repository not found', async () => {
      fetch.mockResolvedValueOnce(testUtils.mockGitHubAPI.error(404, 'Not Found'));

      const result = await gitOps.validateRepository();

      expect(result.success).toBe(false);
      expect(result.error).toContain('Not Found');
    });

    test('should handle invalid repository path format', async () => {
      const settings = testUtils.createMockSettings({
        repositoryPath: 'invalid-format'
      });
      
      await gitOps.initialize(settings);
      const result = await gitOps.validateRepository();

      expect(result.success).toBe(false);
      expect(result.error).toContain('Invalid repository path format');
    });
  });

  describe('File Operations', () => {
    beforeEach(async () => {
      const settings = testUtils.createMockSettings();
      await gitOps.initialize(settings);
    });

    test('should save file to GitHub successfully', async () => {
      const processedContent = testUtils.createMockProcessedContent();
      
      // Mock the GitHub API calls for file creation
      fetch
        .mockResolvedValueOnce({
          ok: false,
          status: 404 // File doesn't exist
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({
            content: { sha: 'new-file-sha' }
          })
        });

      const result = await gitOps.saveToGitHub(processedContent);

      expect(result.success).toBe(true);
      expect(fetch).toHaveBeenCalledTimes(2);
    });

    test('should update existing file on GitHub', async () => {
      const processedContent = testUtils.createMockProcessedContent();
      
      // Mock existing file response
      fetch
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({
            sha: 'existing-file-sha',
            content: Buffer.from('existing content').toString('base64')
          })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({
            content: { sha: 'updated-file-sha' }
          })
        });

      const result = await gitOps.saveToGitHub(processedContent);

      expect(result.success).toBe(true);
      expect(fetch).toHaveBeenCalledTimes(2);
    });

    test('should handle file save errors', async () => {
      const processedContent = testUtils.createMockProcessedContent();
      
      fetch.mockResolvedValueOnce(testUtils.mockGitHubAPI.error(403, 'Forbidden'));

      const result = await gitOps.saveToGitHub(processedContent);

      expect(result.success).toBe(false);
      expect(result.error).toContain('Forbidden');
    });

    test('should generate commit message from template', async () => {
      const processedContent = testUtils.createMockProcessedContent();
      const settings = testUtils.createMockSettings({
        commitMessage: 'Add: {title} from {domain}'
      });
      
      await gitOps.initialize(settings);
      const message = gitOps.generateCommitMessage(processedContent);

      expect(message).toBe('Add: Test Article Title from example.com');
    });

    test('should use default commit message when template is empty', async () => {
      const processedContent = testUtils.createMockProcessedContent();
      const settings = testUtils.createMockSettings({
        commitMessage: ''
      });
      
      await gitOps.initialize(settings);
      const message = gitOps.generateCommitMessage(processedContent);

      expect(message).toContain('Test Article Title');
    });
  });

  describe('Image Operations', () => {
    beforeEach(async () => {
      const settings = testUtils.createMockSettings();
      await gitOps.initialize(settings);
    });

    test('should save image to GitHub', async () => {
      const imageData = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';
      const filename = 'test-image.png';
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          content: { sha: 'image-sha' }
        })
      });

      const result = await gitOps.saveImageToGitHub(imageData, filename);

      expect(result.success).toBe(true);
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('images/test-image.png'),
        expect.objectContaining({
          method: 'PUT',
          body: expect.stringContaining('content')
        })
      );
    });

    test('should handle invalid image data', async () => {
      const invalidImageData = 'invalid-data';
      const filename = 'test-image.png';

      const result = await gitOps.saveImageToGitHub(invalidImageData, filename);

      expect(result.success).toBe(false);
      expect(result.error).toContain('Invalid image data');
    });
  });

  describe('Repository Structure', () => {
    beforeEach(async () => {
      const settings = testUtils.createMockSettings();
      await gitOps.initialize(settings);
    });

    test('should ensure repository structure exists', async () => {
      // Mock responses for checking directory structure
      fetch
        .mockResolvedValueOnce({ ok: false, status: 404 }) // documents/ doesn't exist
        .mockResolvedValueOnce({ ok: false, status: 404 }) // images/ doesn't exist
        .mockResolvedValueOnce({ ok: true }) // Create documents/
        .mockResolvedValueOnce({ ok: true }); // Create images/

      const result = await gitOps.ensureRepositoryStructure();

      expect(result.success).toBe(true);
      expect(fetch).toHaveBeenCalledTimes(4);
    });

    test('should handle structure creation errors', async () => {
      fetch.mockResolvedValueOnce(testUtils.mockGitHubAPI.error(403, 'Forbidden'));

      const result = await gitOps.ensureRepositoryStructure();

      expect(result.success).toBe(false);
      expect(result.error).toContain('Forbidden');
    });
  });

  describe('Error Handling', () => {
    test('should handle API rate limiting', async () => {
      const settings = testUtils.createMockSettings();
      await gitOps.initialize(settings);

      fetch.mockResolvedValueOnce({
        ok: false,
        status: 429,
        headers: {
          get: jest.fn(() => '60') // Reset in 60 seconds
        },
        json: () => Promise.resolve({
          message: 'API rate limit exceeded'
        })
      });

      const result = await gitOps.testConnection();

      expect(result.success).toBe(false);
      expect(result.error).toContain('rate limit');
    });

    test('should handle network timeouts', async () => {
      const settings = testUtils.createMockSettings();
      await gitOps.initialize(settings);

      fetch.mockImplementation(() => 
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Network timeout')), 100)
        )
      );

      const result = await gitOps.testConnection();

      expect(result.success).toBe(false);
      expect(result.error).toContain('timeout');
    });
  });

  describe('Batch Operations', () => {
    beforeEach(async () => {
      const settings = testUtils.createMockSettings();
      await gitOps.initialize(settings);
    });

    test('should save multiple files in batch', async () => {
      const files = [
        testUtils.createMockProcessedContent({ filename: 'file1.md' }),
        testUtils.createMockProcessedContent({ filename: 'file2.md' })
      ];

      // Mock successful saves for both files
      fetch
        .mockResolvedValueOnce({ ok: false, status: 404 })
        .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ content: { sha: 'sha1' } }) })
        .mockResolvedValueOnce({ ok: false, status: 404 })
        .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ content: { sha: 'sha2' } }) });

      const results = await gitOps.saveBatch(files);

      expect(results).toHaveLength(2);
      expect(results[0].success).toBe(true);
      expect(results[1].success).toBe(true);
    });

    test('should handle partial batch failures', async () => {
      const files = [
        testUtils.createMockProcessedContent({ filename: 'file1.md' }),
        testUtils.createMockProcessedContent({ filename: 'file2.md' })
      ];

      // Mock success for first file, failure for second
      fetch
        .mockResolvedValueOnce({ ok: false, status: 404 })
        .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ content: { sha: 'sha1' } }) })
        .mockResolvedValueOnce(testUtils.mockGitHubAPI.error(403, 'Forbidden'));

      const results = await gitOps.saveBatch(files);

      expect(results).toHaveLength(2);
      expect(results[0].success).toBe(true);
      expect(results[1].success).toBe(false);
    });
  });
});
