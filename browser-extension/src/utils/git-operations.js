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
    
    if (!this.settings.repositoryPath) {
      throw new Error('Repository path not configured');
    }
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
    const { filename, content } = processedContent;
    const [owner, repo] = this.parseRepositoryPath();
    
    // Determine the target path
    const targetPath = `documents/${this.settings.defaultFolder}/${filename}`;
    
    // Check if file already exists
    const existingFile = await this.getFileFromGitHub(owner, repo, targetPath);
    
    // Prepare the commit
    const commitData = {
      message: `Add: ${processedContent.metadata.domain} - ${processedContent.metadata.title}`,
      content: btoa(unescape(encodeURIComponent(content))), // Base64 encode
      branch: 'main'
    };

    if (existingFile) {
      commitData.sha = existingFile.sha;
    }

    // Create or update the file
    const response = await fetch(
      `${this.apiBase}/repos/${owner}/${repo}/contents/${targetPath}`,
      {
        method: 'PUT',
        headers: {
          'Authorization': `token ${this.settings.githubToken}`,
          'Content-Type': 'application/json',
          'Accept': 'application/vnd.github.v3+json'
        },
        body: JSON.stringify(commitData)
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`GitHub API error: ${error.message}`);
    }

    const result = await response.json();
    
    // Save images if any
    if (processedContent.images && processedContent.images.length > 0) {
      await this.saveImages(processedContent.images, owner, repo);
    }

    return result;
  }

  async saveImages(images, owner, repo) {
    const savedImages = [];
    
    for (const image of images) {
      try {
        if (!image.src || image.src.startsWith('data:')) {
          continue; // Skip data URLs and empty sources
        }

        // Download the image
        const imageResponse = await fetch(image.src);
        if (!imageResponse.ok) continue;

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
          branch: 'main'
        };

        const response = await fetch(
          `${this.apiBase}/repos/${owner}/${repo}/contents/${imagePath}`,
          {
            method: 'PUT',
            headers: {
              'Authorization': `token ${this.settings.githubToken}`,
              'Content-Type': 'application/json',
              'Accept': 'application/vnd.github.v3+json'
            },
            body: JSON.stringify(commitData)
          }
        );

        if (response.ok) {
          savedImages.push({
            original: image.src,
            saved: imagePath,
            filename: filename
          });
        }

      } catch (error) {
        console.error('Failed to save image:', image.src, error);
      }
    }

    return savedImages;
  }

  async getFileFromGitHub(owner, repo, path) {
    try {
      const response = await fetch(
        `${this.apiBase}/repos/${owner}/${repo}/contents/${path}`,
        {
          headers: {
            'Authorization': `token ${this.settings.githubToken}`,
            'Accept': 'application/vnd.github.v3+json'
          }
        }
      );

      if (response.ok) {
        return await response.json();
      }
      
      return null;
    } catch (error) {
      return null;
    }
  }

  parseRepositoryPath() {
    // Parse repository path like "username/repo-name"
    const parts = this.settings.repositoryPath.split('/');
    if (parts.length !== 2) {
      throw new Error('Invalid repository path format. Use: username/repository');
    }
    return parts;
  }

  getImageExtension(pathname) {
    const match = pathname.match(/\.([a-zA-Z0-9]+)$/);
    return match ? match[1].toLowerCase() : null;
  }

  async downloadFile(processedContent) {
    // Fallback: download file locally
    const blob = new Blob([processedContent.content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    
    await chrome.downloads.download({
      url: url,
      filename: `prismweave/${processedContent.filename}`,
      saveAs: false
    });

    URL.revokeObjectURL(url);
  }

  async testConnection() {
    try {
      if (!this.settings || !this.settings.githubToken) {
        throw new Error('GitHub token not configured');
      }

      const response = await fetch(`${this.apiBase}/user`, {
        headers: {
          'Authorization': `token ${this.settings.githubToken}`,
          'Accept': 'application/vnd.github.v3+json'
        }
      });

      if (!response.ok) {
        throw new Error('Invalid GitHub token');
      }

      const user = await response.json();
      return {
        success: true,
        username: user.login,
        name: user.name
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  async validateRepository() {
    try {
      const [owner, repo] = this.parseRepositoryPath();
      
      const response = await fetch(`${this.apiBase}/repos/${owner}/${repo}`, {
        headers: {
          'Authorization': `token ${this.settings.githubToken}`,
          'Accept': 'application/vnd.github.v3+json'
        }
      });

      if (!response.ok) {
        throw new Error('Repository not found or no access');
      }

      const repoData = await response.json();
      return {
        success: true,
        name: repoData.name,
        fullName: repoData.full_name,
        private: repoData.private,
        hasWrite: repoData.permissions?.push || false
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  async createRepository(repositoryName, isPrivate = true) {
    try {
      const response = await fetch(`${this.apiBase}/user/repos`, {
        method: 'POST',
        headers: {
          'Authorization': `token ${this.settings.githubToken}`,
          'Content-Type': 'application/json',
          'Accept': 'application/vnd.github.v3+json'
        },
        body: JSON.stringify({
          name: repositoryName,
          description: 'PrismWeave document repository',
          private: isPrivate,
          auto_init: true
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message);
      }

      const repo = await response.json();
      
      // Initialize repository structure
      await this.initializeRepositoryStructure(repo.owner.login, repo.name);
      
      return {
        success: true,
        repository: repo.full_name,
        url: repo.html_url
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  async initializeRepositoryStructure(owner, repo) {
    // Create initial directory structure and README
    const files = [
      {
        path: 'documents/README.md',
        content: '# Documents\n\nCaptured web pages and articles.\n'
      },
      {
        path: 'images/README.md',
        content: '# Images\n\nImages extracted from captured pages.\n'
      },
      {
        path: '.prismweave/config.json',
        content: JSON.stringify({
          version: '1.0.0',
          created: new Date().toISOString(),
          structure: {
            documents: 'documents/',
            images: 'images/',
            generated: 'generated/'
          }
        }, null, 2)
      }
    ];

    for (const file of files) {
      try {
        await fetch(`${this.apiBase}/repos/${owner}/${repo}/contents/${file.path}`, {
          method: 'PUT',
          headers: {
            'Authorization': `token ${this.settings.githubToken}`,
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.github.v3+json'
          },
          body: JSON.stringify({
            message: `Initialize: ${file.path}`,
            content: btoa(unescape(encodeURIComponent(file.content))),
            branch: 'main'
          })
        });
      } catch (error) {
        console.error(`Failed to create ${file.path}:`, error);
      }
    }
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
