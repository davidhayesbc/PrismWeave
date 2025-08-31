export interface IGitHubAPIConfig {
  token: string;
  repository: string;
  branch: string;
  baseUrl?: string;
}

export interface IGitHubCommitResult {
  success: boolean;
  data?: {
    sha: string;
    html_url: string;
    commit: {
      message: string;
      author: {
        name: string;
        email: string;
        date: string;
      };
    };
  };
  error?: string;
}

export interface IGitHubFileContent {
  type: string;
  encoding: string;
  size: number;
  name: string;
  path: string;
  content: string;
  sha: string;
  url: string;
  git_url: string;
  html_url: string;
  download_url: string;
}

export class GitHubAPIClient {
  private _config: IGitHubAPIConfig;
  private _baseUrl: string;

  constructor(config: IGitHubAPIConfig) {
    this._config = {
      baseUrl: 'https://api.github.com',
      ...config,
    };
    this._baseUrl = this._config.baseUrl!;
  }

  async commitFile(
    path: string,
    content: string,
    message: string,
    skipExistenceCheck: boolean = false
  ): Promise<IGitHubCommitResult> {
    try {
      const [owner, repo] = this.parseRepository(this._config.repository);

      let existingFile: IGitHubFileContent | null = null;

      if (!skipExistenceCheck) {
        existingFile = await this.getFile(path);
      }

      const commitData: any = {
        message,
        content: this.encodeBase64(content),
        branch: this._config.branch,
      };

      if (existingFile) {
        commitData.sha = existingFile.sha;
      }

      const response = await this.makeRequest(
        `repos/${owner}/${repo}/contents/${path}`,
        'PUT',
        commitData
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        if (skipExistenceCheck && response.status === 409) {
          return this.commitFile(path, content, message, false);
        }

        throw new Error(
          `GitHub API error: ${response.status} - ${errorData.message || 'Unknown error'}`
        );
      }

      const result = await response.json();

      return {
        success: true,
        data: {
          sha: result.commit.sha,
          html_url: result.content.html_url,
          commit: {
            message: result.commit.message,
            author: {
              name: result.commit.author.name,
              email: result.commit.author.email,
              date: result.commit.author.date,
            },
          },
        },
      };
    } catch (error) {
      if (
        !(
          error instanceof Error &&
          (error.message.includes('404') ||
            error.message.includes('Not Found') ||
            error.message.toLowerCase().includes('file not found'))
        )
      ) {
        console.error('GitHub commit failed:', error);
      }
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async getFile(path: string): Promise<IGitHubFileContent | null> {
    try {
      const [owner, repo] = this.parseRepository(this._config.repository);

      const response = await this.makeRequest(
        `repos/${owner}/${repo}/contents/${path}?ref=${this._config.branch}`,
        'GET',
        undefined,
        true
      );

      if (response.status === 404) {
        return null;
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          `GitHub API error: ${response.status} - ${errorData.message || 'Unknown error'}`
        );
      }

      return await response.json();
    } catch (error) {
      if (
        error instanceof Error &&
        (error.message.includes('404') ||
          error.message.includes('Not Found') ||
          error.message.toLowerCase().includes('file not found'))
      ) {
        return null;
      }

      console.error('Failed to get file from GitHub:', error);
      return null;
    }
  }

  async testConnection(): Promise<{
    success: boolean;
    user?: {
      login: string;
      name: string;
      email: string;
    };
    repository?: {
      name: string;
      full_name: string;
      private: boolean;
      permissions: {
        admin: boolean;
        push: boolean;
        pull: boolean;
      };
    };
    error?: string;
  }> {
    try {
      const userResponse = await this.makeRequest('user', 'GET');

      if (!userResponse.ok) {
        const errorData = await userResponse.json().catch(() => ({}));
        return {
          success: false,
          error: `Invalid GitHub token (${userResponse.status}): ${errorData.message || 'Unknown error'}`,
        };
      }

      const userData = await userResponse.json();

      const [owner, repo] = this.parseRepository(this._config.repository);
      const repoResponse = await this.makeRequest(`repos/${owner}/${repo}`, 'GET');

      if (!repoResponse.ok) {
        const errorMsg =
          repoResponse.status === 404
            ? 'Repository not found or no access'
            : `Repository access failed (${repoResponse.status})`;
        return {
          success: false,
          error: errorMsg,
        };
      }

      const repoData = await repoResponse.json();

      return {
        success: true,
        user: {
          login: userData.login,
          name: userData.name || userData.login,
          email: userData.email || '',
        },
        repository: {
          name: repoData.name,
          full_name: repoData.full_name,
          private: repoData.private,
          permissions: repoData.permissions || { admin: false, push: false, pull: true },
        },
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Connection test failed',
      };
    }
  }

  async listFiles(path: string = ''): Promise<{
    success: boolean;
    files?: Array<{
      name: string;
      path: string;
      type: 'file' | 'dir';
      size: number;
      sha: string;
      url: string;
    }>;
    error?: string;
  }> {
    try {
      const [owner, repo] = this.parseRepository(this._config.repository);

      const response = await this.makeRequest(
        `repos/${owner}/${repo}/contents/${path}?ref=${this._config.branch}`,
        'GET'
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return {
          success: false,
          error: `Failed to list files: ${response.status} - ${errorData.message || 'Unknown error'}`,
        };
      }

      const data = await response.json();
      const files = Array.isArray(data) ? data : [data];

      return {
        success: true,
        files: files.map(file => ({
          name: file.name,
          path: file.path,
          type: file.type === 'dir' ? 'dir' : 'file',
          size: file.size || 0,
          sha: file.sha,
          url: file.html_url,
        })),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to list files',
      };
    }
  }

  async createDirectory(path: string): Promise<IGitHubCommitResult> {
    const placeholderPath = `${path}/.gitkeep`;
    const placeholderContent = '# This file maintains the directory structure\n';
    const message = `Create directory: ${path}`;

    return await this.commitFile(placeholderPath, placeholderContent, message);
  }

  async getRepositoryStats(): Promise<{
    success: boolean;
    stats?: {
      size: number;
      stargazers_count: number;
      watchers_count: number;
      forks_count: number;
      open_issues_count: number;
      default_branch: string;
      updated_at: string;
    };
    error?: string;
  }> {
    try {
      const [owner, repo] = this.parseRepository(this._config.repository);

      const response = await this.makeRequest(`repos/${owner}/${repo}`, 'GET');

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return {
          success: false,
          error: `Failed to get repository stats: ${response.status} - ${errorData.message || 'Unknown error'}`,
        };
      }

      const data = await response.json();

      return {
        success: true,
        stats: {
          size: data.size,
          stargazers_count: data.stargazers_count,
          watchers_count: data.watchers_count,
          forks_count: data.forks_count,
          open_issues_count: data.open_issues_count,
          default_branch: data.default_branch,
          updated_at: data.updated_at,
        },
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get repository stats',
      };
    }
  }

  private async makeRequest(
    endpoint: string,
    method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
    body?: any,
    suppressNetworkErrors: boolean = false
  ): Promise<Response> {
    const url = `${this._baseUrl}/${endpoint}`;

    const headers: HeadersInit = {
      Authorization: `token ${this._config.token}`,
      Accept: 'application/vnd.github.v3+json',
      'User-Agent': 'PrismWeave-Bookmarklet/1.0',
    };

    if (body && (method === 'POST' || method === 'PUT')) {
      headers['Content-Type'] = 'application/json';
    }

    const requestOptions: RequestInit = {
      method,
      headers,
      ...(body && { body: JSON.stringify(body) }),
    };

    try {
      const response = await fetch(url, requestOptions);

      if (response.status === 404 && method === 'GET' && endpoint.includes('/contents/')) {
        return response;
      }

      return response;
    } catch (error) {
      if (!suppressNetworkErrors) {
        console.error('Network request failed:', error);
      }
      throw error;
    }
  }

  private parseRepository(repository: string): [string, string] {
    const parts = repository.split('/');
    if (parts.length !== 2) {
      throw new Error(`Invalid repository format: ${repository}. Expected "owner/repo"`);
    }
    return [parts[0], parts[1]];
  }

  private encodeBase64(content: string): string {
    try {
      return btoa(unescape(encodeURIComponent(content)));
    } catch (error) {
      const bytes = new TextEncoder().encode(content);
      let binary = '';
      bytes.forEach(byte => {
        binary += String.fromCharCode(byte);
      });
      return btoa(binary);
    }
  }

  private decodeBase64(encoded: string): string {
    try {
      return decodeURIComponent(escape(atob(encoded)));
    } catch (error) {
      const binary = atob(encoded);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
      }
      return new TextDecoder().decode(bytes);
    }
  }

  updateConfig(updates: Partial<IGitHubAPIConfig>): void {
    this._config = { ...this._config, ...updates };
    if (updates.baseUrl) {
      this._baseUrl = updates.baseUrl;
    }
  }

  getConfig(): Omit<IGitHubAPIConfig, 'token'> {
    const { token, ...config } = this._config;
    return config;
  }
}
