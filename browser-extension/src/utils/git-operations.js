// PrismWeave Git Operations
// Handles Git repository management and synchronization

class GitOperations {
  constructor() {
    this.apiBase = 'https://api.github.com';
    this.settings = null;
  }

  async initialize(settings) {
    this.settings = settings;

    if (!this.settings.githubToken) {
      throw new Error('GitHub token not configured');
    }

    // Check for repository path in either githubRepo or repositoryPath
    const repoPath = this.settings.githubRepo || this.settings.repositoryPath;
    if (!repoPath) {
      throw new Error('Repository path not configured');
    }
    
    // Normalize the repository path
    this.settings.repositoryPath = repoPath;
    
    console.log('GitOperations initialized with:', {
      hasToken: !!this.settings.githubToken,
      repositoryPath: this.settings.repositoryPath,
      githubRepo: this.settings.githubRepo
    });
  }

  async saveToRepository(processedContent) {
    try {
      if (!this.settings) {
        throw new Error('Git operations not initialized');
      }

      // For browser extension, we'll use GitHub API directly
      // since we can't run git commands in the browser
      await this.saveToGitHub(processedContent);
    } catch (error) {
      console.error('Failed to save to repository:', error);
      // Fallback to local download
      await this.downloadFile(processedContent);
      throw error;
    }
  }

  async saveToGitHub(processedContent) {
    const { filename, content, metadata } = processedContent;
    const [owner, repo] = this.parseRepositoryPath();

    // Use the folder from metadata, fallback to 'unsorted'
    const folder = metadata?.folder || 'unsorted';
    
    // Sanitize filename for GitHub (remove/replace problematic characters)
    const sanitizedFilename = this.sanitizeFilenameForGitHub(filename);
    const targetPath = `documents/${folder}/${sanitizedFilename}`;

    console.log('Saving to GitHub:', { 
      owner, 
      repo, 
      targetPath, 
      folder, 
      originalFilename: filename,
      sanitizedFilename,
      pathLength: targetPath.length
    });

    // First, let's get repository info to check the default branch
    const repoInfo = await this.getRepositoryInfo(owner, repo);
    const defaultBranch = repoInfo.default_branch || 'main';
    console.log('Repository default branch:', defaultBranch);

    // Ensure repository structure exists (especially for new repos)
    await this.ensureRepositoryStructure(owner, repo, defaultBranch);

    // Check if file already exists
    const existingFile = await this.getFileFromGitHub(owner, repo, targetPath, defaultBranch);

    // Prepare the commit
    const commitData = {
      message: `Add: ${metadata?.domain || 'unknown'} - ${metadata?.title || sanitizedFilename}`,
      content: btoa(unescape(encodeURIComponent(content))), // Base64 encode
      branch: defaultBranch,
    };

    if (existingFile) {
      commitData.sha = existingFile.sha;
      console.log('Updating existing file with SHA:', existingFile.sha);
    } else {
      console.log('Creating new file');
    }

    // Create or update the file
    const apiUrl = `${this.apiBase}/repos/${owner}/${repo}/contents/${targetPath}`;
    console.log('Making API request to:', apiUrl);
    console.log('Request payload:', { 
      ...commitData, 
      content: '[BASE64_CONTENT]',
      contentLength: commitData.content.length 
    });
    
    const response = await fetch(apiUrl, {
      method: 'PUT',
      headers: {
        Authorization: `token ${this.settings.githubToken}`,
        'Content-Type': 'application/json',
        Accept: 'application/vnd.github.v3+json',
      },
      body: JSON.stringify(commitData),
    });

    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const errorData = await response.json();
        console.error('GitHub API Error Details:', errorData);
        errorMessage = errorData.message || errorMessage;
        
        // Add specific error handling for common issues
        if (response.status === 404) {
          errorMessage = `Repository or path not found. Check that '${owner}/${repo}' exists and you have write access. Path: ${targetPath}`;
        } else if (response.status === 409 && errorData.message?.includes('sha')) {
          errorMessage = `File conflict - the file may have been modified. Try again or check the repository.`;
        } else if (response.status === 422) {
          errorMessage = `Invalid request. This might be due to path length (${targetPath.length} chars) or invalid characters. ${errorData.message || ''}`;
        }
      } catch (parseError) {
        console.error('Failed to parse error response:', parseError);
      }
      throw new Error(`GitHub API error: ${errorMessage} (URL: ${apiUrl})`);
    }

    const result = await response.json();
    console.log('File saved successfully:', result.content?.name);

    // Save images if any
    if (processedContent.images && processedContent.images.length > 0) {
      await this.saveImages(processedContent.images, owner, repo, defaultBranch);
    }

    return result;
  }

  async saveImages(images, owner, repo, branch = 'main') {
    const savedImages = [];

    for (const image of images) {
      try {
        if (!image.src || image.src.startsWith('data:')) {
          continue; // Skip data URLs and empty sources
        }

        // Download the image
        const imageResponse = await fetch(image.src);
        if (!imageResponse.ok) {
          console.error(`Failed to download image: HTTP ${imageResponse.status} (URL: ${image.src})`);
          continue;
        }

        const imageBlob = await imageResponse.blob();
        const arrayBuffer = await imageBlob.arrayBuffer();
        const base64Content = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));

        // Generate filename
        const url = new URL(image.src);
        const extension = this.getImageExtension(url.pathname) || 'jpg';
        const filename = `${Date.now()}-${Math.random().toString(36).substring(7)}.${extension}`;
        const imagePath = `images/${new Date().toISOString().split('T')[0]}/${filename}`;

        // Save to GitHub
        const commitData = {
          message: `Add image: ${filename}`,
          content: base64Content,
          branch: branch,
        };

        const imageApiUrl = `${this.apiBase}/repos/${owner}/${repo}/contents/${imagePath}`;
        const response = await fetch(imageApiUrl, {
          method: 'PUT',
          headers: {
            Authorization: `token ${this.settings.githubToken}`,
            'Content-Type': 'application/json',
            Accept: 'application/vnd.github.v3+json',
          },
          body: JSON.stringify(commitData),
        });

        if (response.ok) {
          savedImages.push({
            original: image.src,
            saved: imagePath,
            filename: filename,
          });
          console.log(`Image saved successfully: ${filename}`);
        } else {
          console.error(`Failed to save image to GitHub: HTTP ${response.status} (URL: ${imageApiUrl})`);
        }
      } catch (error) {
        console.error('Failed to save image:', image.src, error);
      }
    }

    return savedImages;
  }

  async ensureRepositoryStructure(owner, repo, branch = 'main') {
    try {
      console.log('Ensuring repository structure exists...');
      
      // Check if basic structure exists by trying to get the documents folder
      const documentsCheck = await this.checkDirectoryExists(owner, repo, 'documents', branch);
      
      if (!documentsCheck) {
        console.log('Repository structure not found, creating basic structure...');
        await this.initializeRepositoryStructure(owner, repo, branch);
      } else {
        console.log('Repository structure exists');
      }
    } catch (error) {
      console.warn('Failed to ensure repository structure, but continuing...', error);
      // Don't throw here - the file creation might still work
    }
  }

  async checkDirectoryExists(owner, repo, path, branch = 'main') {
    try {
      const apiUrl = `${this.apiBase}/repos/${owner}/${repo}/contents/${path}?ref=${branch}`;
      const response = await fetch(apiUrl, {
        headers: {
          Authorization: `token ${this.settings.githubToken}`,
          Accept: 'application/vnd.github.v3+json',
        },
      });

      // If we get 200, the directory exists and has contents
      // If we get 404, the directory doesn't exist
      return response.ok;
    } catch (error) {
      console.warn(`Failed to check if directory exists: ${path}`, error);
      return false;
    }
  }

  async getRepositoryInfo(owner, repo) {
    try {
      const apiUrl = `${this.apiBase}/repos/${owner}/${repo}`;
      const response = await fetch(apiUrl, {
        headers: {
          Authorization: `token ${this.settings.githubToken}`,
          Accept: 'application/vnd.github.v3+json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to get repository info: HTTP ${response.status} (URL: ${apiUrl})`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to get repository info:', error);
      // Return default info as fallback
      return { default_branch: 'main' };
    }
  }

  async getFileFromGitHub(owner, repo, path, branch = 'main') {
    try {
      const apiUrl = `${this.apiBase}/repos/${owner}/${repo}/contents/${path}?ref=${branch}`;
      const response = await fetch(apiUrl, {
        headers: {
          Authorization: `token ${this.settings.githubToken}`,
          Accept: 'application/vnd.github.v3+json',
        },
      });

      if (response.ok) {
        return await response.json();
      } else if (response.status === 404) {
        // File doesn't exist - this is expected for new files
        console.log(`File not found (creating new): ${path} on branch ${branch}`);
        return null;
      } else {
        console.error(`Failed to get file from GitHub: HTTP ${response.status} - ${response.statusText} (URL: ${apiUrl})`);
        return null;
      }
    } catch (error) {
      console.error(`Failed to get file from GitHub: ${error.message} (URL: ${apiUrl})`);
      return null;
    }
  }

  parseRepositoryPath() {
    // Parse repository path like "username/repo-name"
    // Check both githubRepo and repositoryPath for backwards compatibility
    const repoPath = this.settings.githubRepo || this.settings.repositoryPath;
    
    if (!repoPath) {
      throw new Error('Repository path is not configured. Please set up your GitHub repository in settings.');
    }
    
    const parts = repoPath.trim().split('/');
    if (parts.length !== 2 || !parts[0] || !parts[1]) {
      throw new Error(`Invalid repository path format: '${repoPath}'. Use format: username/repository`);
    }
    
    console.log('Parsed repository path:', { owner: parts[0], repo: parts[1] });
    return parts;
  }

  sanitizeFilenameForGitHub(filename) {
    if (!filename) return 'untitled.md';
    
    // Remove or replace characters that might cause issues with GitHub API
    let sanitized = filename
      // Replace spaces with hyphens
      .replace(/\s+/g, '-')
      // Remove characters that are problematic in URLs/file paths
      .replace(/[<>:"|?*\\\/]/g, '')
      // Replace multiple consecutive hyphens with single hyphen
      .replace(/-+/g, '-')
      // Remove leading/trailing hyphens
      .replace(/^-+|-+$/g, '')
      // Convert to lowercase for consistency
      .toLowerCase();
    
    // Ensure reasonable length (GitHub has path length limits)
    if (sanitized.length > 80) {
      const parts = sanitized.split('.');
      const extension = parts.length > 1 ? '.' + parts.pop() : '.md';
      const nameWithoutExt = parts.join('.');
      
      // Truncate the name part, keeping the extension
      sanitized = nameWithoutExt.substring(0, 80 - extension.length) + extension;
    }
    
    // Ensure it has .md extension
    if (!sanitized.endsWith('.md')) {
      sanitized += '.md';
    }
    
    return sanitized;
  }

  getImageExtension(pathname) {
    const match = pathname.match(/\.([a-zA-Z0-9]+)$/);
    return match ? match[1].toLowerCase() : null;
  }

  async downloadFile(processedContent) {
    try {
      // Fallback: download file locally using data URL (service worker compatible)
      const content = processedContent.content;
      const dataUrl = 'data:text/markdown;charset=utf-8,' + encodeURIComponent(content);

      await chrome.downloads.download({
        url: dataUrl,
        filename: `prismweave/${processedContent.filename}`,
        saveAs: false,
      });
    } catch (error) {
      console.error('Failed to download file:', error);
      throw new Error(`Download failed: ${error.message}`);
    }
  }

  async testConnection() {
    try {
      if (!this.settings || !this.settings.githubToken) {
        throw new Error('GitHub token not configured');
      }

      const apiUrl = `${this.apiBase}/user`;
      const response = await fetch(apiUrl, {
        headers: {
          Authorization: `token ${this.settings.githubToken}`,
          Accept: 'application/vnd.github.v3+json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error(`Invalid GitHub token. Please check your token and try again. (URL: ${apiUrl})`);
        } else if (response.status === 403) {
          throw new Error(`GitHub token lacks required permissions. (URL: ${apiUrl})`);
        } else {
          throw new Error(`GitHub API error: HTTP ${response.status} - ${response.statusText} (URL: ${apiUrl})`);
        }
      }

      const user = await response.json();
      return {
        success: true,
        username: user.login,
        name: user.name,
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
      };
    }
  }

  async validateRepository() {
    try {
      const [owner, repo] = this.parseRepositoryPath();
      const repoPath = this.settings.githubRepo || this.settings.repositoryPath;
      console.log('Validating repository:', { 
        owner, 
        repo, 
        fullPath: repoPath,
        settingsGithubRepo: this.settings.githubRepo,
        settingsRepositoryPath: this.settings.repositoryPath
      });

      const apiUrl = `${this.apiBase}/repos/${owner}/${repo}`;
      const response = await fetch(apiUrl, {
        headers: {
          Authorization: `token ${this.settings.githubToken}`,
          Accept: 'application/vnd.github.v3+json',
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Repository '${repoPath}' not found. Please check the repository name and ensure it exists. (URL: ${apiUrl})`);
        } else if (response.status === 403) {
          throw new Error(`Access denied to repository '${repoPath}'. Please check your GitHub token permissions. (URL: ${apiUrl})`);
        } else {
          let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
          try {
            const errorData = await response.json();
            errorMessage = errorData.message || errorMessage;
          } catch (parseError) {
            // Use default error message
          }
          throw new Error(`GitHub API error: ${errorMessage} (URL: ${apiUrl})`);
        }
      }

      const repoData = await response.json();
      console.log('Repository validation successful:', {
        name: repoData.name,
        fullName: repoData.full_name,
        permissions: repoData.permissions
      });
      
      return {
        success: true,
        name: repoData.name,
        fullName: repoData.full_name,
        private: repoData.private,
        hasWrite: repoData.permissions?.push || false,
      };
    } catch (error) {
      console.error('Repository validation failed:', error);
      return {
        success: false,
        error: error.message,
      };
    }
  }

  async createRepository(repositoryName, isPrivate = true) {
    try {
      const apiUrl = `${this.apiBase}/user/repos`;
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          Authorization: `token ${this.settings.githubToken}`,
          'Content-Type': 'application/json',
          Accept: 'application/vnd.github.v3+json',
        },
        body: JSON.stringify({
          name: repositoryName,
          description: 'PrismWeave document repository',
          private: isPrivate,
          auto_init: true,
        }),
      });

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.message || errorMessage;
        } catch (parseError) {
          // If we can't parse the error response, use the status text
        }
        throw new Error(`GitHub API error: ${errorMessage} (URL: ${apiUrl})`);
      }

      const repo = await response.json();

      // Initialize repository structure
      await this.initializeRepositoryStructure(repo.owner.login, repo.name, repo.default_branch || 'main');

      return {
        success: true,
        repository: repo.full_name,
        url: repo.html_url,
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
      };
    }
  }

  async initializeRepositoryStructure(owner, repo, branch = 'main') {
    console.log(`Initializing repository structure for ${owner}/${repo} on branch ${branch}`);
    
    // Create initial directory structure and README
    const files = [
      {
        path: 'documents/README.md',
        content: '# Documents\n\nCaptured web pages and articles organized by category.\n\n## Folder Structure\n- `tech/` - Technology and programming content\n- `business/` - Business and finance articles\n- `research/` - Academic and research papers\n- `news/` - News articles and current events\n- `tutorial/` - How-to guides and tutorials\n- `reference/` - Documentation and reference materials\n- `blog/` - Blog posts and personal content\n- `social/` - Social media content\n- `unsorted/` - Uncategorized content\n',
      },
      {
        path: 'images/README.md',
        content: '# Images\n\nImages extracted from captured pages, organized by date.\n\nImages are automatically saved when capturing pages that contain them.\n',
      },
      {
        path: '.prismweave/config.json',
        content: JSON.stringify(
          {
            version: '1.0.0',
            created: new Date().toISOString(),
            structure: {
              documents: 'documents/',
              images: 'images/',
              generated: 'generated/',
            },
            folders: {
              tech: 'Technology and programming content',
              business: 'Business and finance articles',
              research: 'Academic and research papers',
              news: 'News articles and current events',
              tutorial: 'How-to guides and tutorials',
              reference: 'Documentation and reference materials',
              blog: 'Blog posts and personal content',
              social: 'Social media content',
              unsorted: 'Uncategorized content'
            }
          },
          null,
          2
        ),
      },
    ];

    for (const file of files) {
      try {
        console.log(`Creating structure file: ${file.path}`);
        const response = await fetch(`${this.apiBase}/repos/${owner}/${repo}/contents/${file.path}`, {
          method: 'PUT',
          headers: {
            Authorization: `token ${this.settings.githubToken}`,
            'Content-Type': 'application/json',
            Accept: 'application/vnd.github.v3+json',
          },
          body: JSON.stringify({
            message: `Initialize: ${file.path}`,
            content: btoa(unescape(encodeURIComponent(file.content))),
            branch: branch,
          }),
        });
        
        if (response.ok) {
          console.log(`Successfully created: ${file.path}`);
        } else {
          console.warn(`Failed to create ${file.path}: HTTP ${response.status}`);
        }
      } catch (error) {
        console.error(`Failed to create ${file.path}:`, error);
      }
    }
    
    console.log('Repository structure initialization completed');
  }

  generateCommitMessage(processedContent) {
    if (!processedContent || !processedContent.title) {
      return 'Add new document';
    }

    const title = processedContent.title.substring(0, 50);
    const domain = processedContent.domain || 'web';
    
    return `Add: ${title} (from ${domain})`;
  }
}

// For use in service worker context
if (typeof module !== 'undefined' && module.exports) {
  module.exports = GitOperations;
}

// For browser extension context
if (typeof window !== 'undefined') {
  window.GitOperations = GitOperations;
}
