import type { IDocumentMetadata, IFileOperationResult, IGitHubSettings } from '../types.js';
import { createConsoleLogger, type ILogger } from '../util/index.js';

interface IFolderMapping {
  [key: string]: string[];
}

interface IFileNameComponents {
  date: string;
  domain: string;
  title: string;
  extension: string;
}

interface IFileManagerOptions {
  customNamingPattern?: string;
  fileNamingPattern?: string;
  defaultFolder?: string;
  customFolder?: string;
}

export interface IGitHubCommitParams {
  token: string;
  repo: string;
  filePath: string;
  content: string;
  message: string;
  url?: string;
  alreadyBase64?: boolean;
}

export interface IGitHubCommitResult {
  success: boolean;
  data?: {
    html_url?: string;
    sha?: string;
    [key: string]: unknown;
  };
  error?: string;
}

export interface IGitHubFileInfo {
  sha: string;
  content: string;
  encoding: string;
}

export interface IRepositoryInfo {
  owner: string;
  repo: string;
}

function encodeContentToBase64(content: string): string {
  if (typeof btoa === 'function') {
    return btoa(unescape(encodeURIComponent(content)));
  }

  if (typeof Buffer !== 'undefined') {
    return Buffer.from(content, 'utf-8').toString('base64');
  }

  throw new Error('Base64 encoding is not supported in this environment');
}

/**
 * Shared file manager responsible for deterministic file naming and GitHub
 * interactions. Works in both browser and Node contexts.
 */
export class FileManager {
  private static readonly API_BASE = 'https://api.github.com';
  private static readonly USER_AGENT = 'PrismWeave-Shared/1.0';
  private readonly folderMapping: IFolderMapping;
  private readonly logger: ILogger;

  constructor(logger: ILogger = createConsoleLogger('FileManager')) {
    this.logger = logger;
    this.folderMapping = {
      tech: [
        'programming',
        'software',
        'coding',
        'development',
        'technology',
        'tech',
        'javascript',
        'python',
        'react',
        'node',
        'github',
        'stackoverflow',
        'dev',
        'developer',
        'mozilla',
        'typescript',
        'haskell',
        'unison',
        'testing',
        'frontend',
        'backend',
        'api',
        'web',
        'code',
        'engineering',
        'computer',
        'ai',
        'machine-learning',
        'ocr',
        'document-processing',
        'ai-assisted-programming',
        'llm',
      ],
      business: [
        'business',
        'marketing',
        'finance',
        'startup',
        'entrepreneur',
        'sales',
        'management',
        'strategy',
        'linkedin',
        'leadership',
        'ceo',
        'fortune',
      ],
      tutorial: [
        'tutorial',
        'guide',
        'how-to',
        'learn',
        'course',
        'lesson',
        'walkthrough',
        'step-by-step',
        'complete',
        'beginner',
        'introduction',
        'getting-started',
        'setup',
        'install',
        'configure',
      ],
      news: [
        'news',
        'article',
        'blog',
        'opinion',
        'analysis',
        'update',
        'announcement',
        'breaking',
        'industry',
      ],
      research: [
        'research',
        'study',
        'paper',
        'academic',
        'journal',
        'thesis',
        'analysis',
        'data',
        'arxiv',
        'institute',
      ],
      design: ['design', 'ui', 'ux', 'css', 'figma', 'adobe', 'creative', 'visual', 'art'],
      tools: ['tool', 'utility', 'software', 'app', 'service', 'platform', 'extension'],
      personal: ['personal', 'diary', 'journal', 'thoughts', 'reflection', 'life', 'experience'],
      reference: ['reference', 'documentation', 'manual', 'spec', 'api', 'docs', 'wiki'],
    };
  }

  generateFilename(metadata: IDocumentMetadata, options: IFileManagerOptions = {}): string {
    try {
      const components = this.extractFileNameComponents(metadata);
      const pattern = options.fileNamingPattern || 'YYYY-MM-DD-domain-title';

      return this.applyNamingPattern(components, pattern, options);
    } catch (error) {
      this.logger.error('Error generating filename:', error);
      return this.getFallbackFilename(metadata);
    }
  }

  determineFolder(metadata: IDocumentMetadata, options: IFileManagerOptions = {}): string {
    if (options.defaultFolder === 'custom' && options.customFolder) {
      return this.sanitizeFolderName(options.customFolder);
    }

    if (options.defaultFolder && options.defaultFolder !== 'auto') {
      return options.defaultFolder;
    }

    const detectedFolder = this.autoDetectFolder(metadata);
    return detectedFolder || 'unsorted';
  }

  generateFilePath(metadata: IDocumentMetadata, options: IFileManagerOptions = {}): string {
    const folder = this.determineFolder(metadata, options);
    const filename = this.generateFilename(metadata, options);

    return `documents/${folder}/${filename}`;
  }

  generatePDFFilePath(title: string, url: string): string {
    const date = this.formatDate(new Date());
    const domain = this.extractDomain(url);
    const sanitizedTitle = this.sanitizeTitle(title);
    const filename = `${date}-${domain}-${sanitizedTitle}.pdf`;
    return `documents/pdfs/${filename}`;
  }

  validateFilePath(filePath: string): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    const dangerousChars = /[<>:"|?*\x00-\x1f]/;
    if (dangerousChars.test(filePath)) {
      errors.push('File path contains invalid characters');
    }

    if (filePath.length > 260) {
      errors.push('File path is too long (max 260 characters)');
    }

    const reservedNames = [
      'CON',
      'PRN',
      'AUX',
      'NUL',
      'COM1',
      'COM2',
      'COM3',
      'COM4',
      'COM5',
      'COM6',
      'COM7',
      'COM8',
      'COM9',
      'LPT1',
      'LPT2',
      'LPT3',
      'LPT4',
      'LPT5',
      'LPT6',
      'LPT7',
      'LPT8',
      'LPT9',
    ];
    const filename = filePath.split('/').pop()?.split('.')[0]?.toUpperCase();
    if (filename && reservedNames.includes(filename)) {
      errors.push('Filename uses reserved system name');
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  createUniqueFilename(basePath: string, existingFiles: string[] = []): string {
    const pathParts = basePath.split('/');
    const filename = pathParts.pop() || '';
    const directory = pathParts.join('/');

    const [name, extension] = this.splitFilename(filename);

    let counter = 1;
    let uniquePath = basePath;

    while (existingFiles.includes(uniquePath)) {
      const uniqueName = `${name}-${counter}.${extension}`;
      uniquePath = directory ? `${directory}/${uniqueName}` : uniqueName;
      counter++;
    }

    return uniquePath;
  }

  organizeFiles(
    files: Array<{ metadata: IDocumentMetadata; content: string }>,
    options: IFileManagerOptions = {}
  ): Record<string, Array<{ filename: string; content: string; metadata: IDocumentMetadata }>> {
    const organized: Record<
      string,
      Array<{ filename: string; content: string; metadata: IDocumentMetadata }>
    > = {};

    files.forEach(file => {
      const folder = this.determineFolder(file.metadata, options);
      const filename = this.generateFilename(file.metadata, options);

      if (!organized[folder]) {
        organized[folder] = [];
      }

      organized[folder].push({
        filename,
        content: file.content,
        metadata: file.metadata,
      });
    });

    return organized;
  }

  async saveToGitHub(
    content: string,
    metadata: IDocumentMetadata,
    githubSettings: IGitHubSettings,
    options: IFileManagerOptions = {}
  ): Promise<IFileOperationResult> {
    try {
      const fullPath = this.generateFilePath(metadata, options);
      const validation = this.validateFilePath(fullPath);

      if (!validation.isValid) {
        return {
          success: false,
          filePath: fullPath,
          error: `Invalid file path: ${validation.errors.join(', ')}`,
        };
      }

      const commitMessage = this.generateCommitMessage(metadata, fullPath);

      const githubResult = await this.commitToGitHub({
        token: githubSettings.token,
        repo: githubSettings.repository,
        filePath: fullPath,
        content,
        message: commitMessage,
        url: metadata.url,
      });

      const result: IFileOperationResult = {
        success: githubResult.success,
        filePath: fullPath,
      };

      if (githubResult.data?.sha) {
        result.sha = githubResult.data.sha;
      }

      if (githubResult.data?.html_url) {
        result.url = githubResult.data.html_url;
      }

      if (githubResult.error) {
        result.error = githubResult.error;
      }

      return result;
    } catch (error) {
      this.logger.error('Error saving to GitHub:', error);
      return {
        success: false,
        filePath: '',
        error: (error as Error).message,
      };
    }
  }

  async savePDFToGitHub(
    pdfBase64: string,
    title: string,
    url: string,
    githubSettings: IGitHubSettings
  ): Promise<IFileOperationResult> {
    try {
      const filePath = this.generatePDFFilePath(title, url);
      const commitMessage = `Add PDF document: ${title} (${this.extractDomain(url)})`;

      const result = await this.commitToGitHub({
        token: githubSettings.token,
        repo: githubSettings.repository,
        filePath,
        content: pdfBase64,
        message: commitMessage,
        url,
        alreadyBase64: true,
      });

      return {
        success: result.success,
        filePath,
        sha: result.data?.sha,
        url: result.data?.html_url,
        error: result.error,
      };
    } catch (error) {
      return {
        success: false,
        filePath: '',
        error: (error as Error).message,
      };
    }
  }

  async commitToGitHub(params: IGitHubCommitParams): Promise<IGitHubCommitResult> {
    try {
      const { token, repo, filePath, content, message, alreadyBase64 } = params;

      this.logger.info('Starting GitHub commit process:', {
        repo,
        filePath,
        messageLength: message.length,
        contentLength: content.length,
      });

      const repoInfo = this.parseRepositoryPath(repo);
      this.logger.debug('Parsed repository:', repoInfo);

      const existingFile = await this.getFileInfo(token, repoInfo, filePath);
      this.logger.debug('File existence check:', {
        exists: !!existingFile,
        sha: existingFile?.sha,
      });

      const result = await this.createOrUpdateFile(
        token,
        repoInfo,
        filePath,
        content,
        message,
        existingFile?.sha,
        alreadyBase64
      );

      this.logger.info('Successfully committed to GitHub:', result.content?.html_url);

      return {
        success: true,
        data: result.content,
      };
    } catch (error) {
      this.logger.error('GitHub commit failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async testGitHubConnection(
    token: string,
    repo: string
  ): Promise<{
    success: boolean;
    status: string;
    message?: string;
    details?: Record<string, unknown>;
    error?: string;
  }> {
    try {
      this.logger.info('Testing GitHub connection...');

      if (!token || !repo) {
        return {
          success: false,
          status: 'failed',
          error: 'GitHub token and repository are required',
        };
      }

      const repoInfo = this.parseRepositoryPath(repo);

      const userData = await this.validateToken(token);
      const repoData = await this.validateRepository(token, repoInfo);
      const hasWriteAccess = await this.checkWritePermissions(token, repoInfo);

      return {
        success: true,
        status: 'connected',
        message: 'GitHub connection test successful',
        details: {
          user: userData.login,
          userType: userData.type,
          repository: repoData.full_name,
          repositoryPrivate: repoData.private,
          hasWriteAccess,
          permissions: repoData.permissions || { admin: false, push: false, pull: true },
        },
      };
    } catch (error) {
      this.logger.error('GitHub connection test failed:', error);
      return {
        success: false,
        status: 'failed',
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  getAvailableFolders(): string[] {
    return Object.keys(this.folderMapping);
  }

  getFolderKeywords(folder: string): string[] {
    return this.folderMapping[folder] || [];
  }

  addFolderKeywords(folder: string, keywords: string[]): void {
    if (!this.folderMapping[folder]) {
      this.folderMapping[folder] = [];
    }

    keywords.forEach(keyword => {
      if (!this.folderMapping[folder].includes(keyword.toLowerCase())) {
        this.folderMapping[folder].push(keyword.toLowerCase());
      }
    });
  }

  getFileStats(filePath: string): { folder: string; filename: string; extension: string } {
    const parts = filePath.split('/');
    const filename = parts.pop() || '';
    const folder = parts.join('/') || '';
    const [name, extension] = this.splitFilename(filename);

    return { folder, filename: name, extension };
  }

  private extractFileNameComponents(metadata: IDocumentMetadata): IFileNameComponents {
    const date = this.formatDate(new Date(metadata.captureDate));
    const domain = this.extractDomain(metadata.url);
    const title = this.sanitizeTitle(metadata.title);

    return {
      date,
      domain,
      title,
      extension: 'md',
    };
  }

  private applyNamingPattern(
    components: IFileNameComponents,
    pattern: string,
    options: IFileManagerOptions = {}
  ): string {
    if (pattern === 'custom' && options.customNamingPattern) {
      pattern = options.customNamingPattern;
    }

    let filename = pattern
      .replace(/YYYY/g, components.date.substring(0, 4))
      .replace(/MM/g, components.date.substring(5, 7))
      .replace(/DD/g, components.date.substring(8, 10))
      .replace(/domain/g, components.domain)
      .replace(/title/g, components.title);

    if (!filename.endsWith(`.${components.extension}`)) {
      filename += `.${components.extension}`;
    }

    return this.sanitizeFilename(filename);
  }

  private formatDate(date: Date): string {
    return date.toISOString().split('T')[0];
  }

  private extractDomain(url: string): string {
    try {
      const urlObj = new URL(url);
      let domain = urlObj.hostname;

      if (domain.startsWith('www.')) {
        domain = domain.substring(4);
      }

      const meaningfulSubdomains = ['developer', 'docs', 'api', 'blog', 'news'];
      const domainParts = domain.split('.');

      if (domainParts.length > 2) {
        const subdomain = domainParts[0];
        const mainDomain = domainParts.slice(-2).join('.');

        if (meaningfulSubdomains.includes(subdomain.toLowerCase())) {
          domain = `${subdomain}.${mainDomain}`;
        } else {
          domain = mainDomain;
        }
      }

      return domain.replace(/\./g, '-');
    } catch {
      return 'unknown-site';
    }
  }

  private sanitizeTitle(title: string): string {
    return title
      .toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '')
      .substring(0, 50);
  }

  private sanitizeFilename(filename: string): string {
    return filename
      .replace(/[<>:"|?*\x00-\x1f]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');
  }

  private sanitizeFolderName(folderName: string): string {
    return folderName
      .toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');
  }

  private getFallbackFilename(metadata: IDocumentMetadata): string {
    const date = this.formatDate(new Date(metadata.captureDate));
    const title = this.sanitizeTitle(metadata.title || 'untitled');
    return `${date}-${title}.md`;
  }

  private autoDetectFolder(metadata: IDocumentMetadata): string | null {
    const searchSources = [
      metadata.title.toLowerCase(),
      metadata.url.toLowerCase(),
      ...metadata.tags.map(tag => tag.toLowerCase()),
      ...this.extractUrlKeywords(metadata.url),
    ];

    const searchText = searchSources.join(' ');

    const folderScores: Record<string, number> = {};

    Object.entries(this.folderMapping).forEach(([folder, keywords]) => {
      let score = 0;

      keywords.forEach(keyword => {
        const wordBoundaryRegex = new RegExp(
          `\\b${keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`,
          'gi'
        );
        const matches = searchText.match(wordBoundaryRegex);
        if (matches) {
          score += matches.length;
        }

        if (metadata.url.toLowerCase().includes(keyword)) {
          score += 0.5;
        }
      });

      if (score > 0) {
        folderScores[folder] = score;
      }
    });

    const sortedFolders = Object.entries(folderScores).sort(([, a], [, b]) => b - a);
    const bestMatch = sortedFolders[0];

    return bestMatch && bestMatch[1] >= 1 ? bestMatch[0] : null;
  }

  private extractUrlKeywords(url: string): string[] {
    try {
      const urlObj = new URL(url);
      const keywords: string[] = [];

      const hostname = urlObj.hostname.toLowerCase();
      const domainParts = hostname.replace(/^www\./, '').split('.');
      keywords.push(...domainParts);

      if (hostname.includes('github')) keywords.push('github', 'development', 'code');
      if (hostname.includes('stackoverflow'))
        keywords.push('stackoverflow', 'programming', 'development');
      if (hostname.includes('developer')) keywords.push('developer', 'development', 'tech');
      if (hostname.includes('mozilla')) keywords.push('mozilla', 'developer', 'web', 'tech');
      if (hostname.includes('linkedin')) keywords.push('linkedin', 'business', 'professional');
      if (hostname.includes('dev.to') || hostname.includes('dev'))
        keywords.push('dev', 'development', 'programming');
      if (hostname.includes('blog')) keywords.push('blog', 'article');
      if (hostname.includes('tutorial')) keywords.push('tutorial', 'guide');
      if (hostname.includes('news')) keywords.push('news', 'article');
      if (hostname.includes('research') || hostname.includes('arxiv'))
        keywords.push('research', 'academic');

      const pathParts = urlObj.pathname
        .toLowerCase()
        .split('/')
        .filter(part => part.length > 2);
      keywords.push(...pathParts);

      return keywords
        .map(keyword => keyword.replace(/[^a-z0-9]/g, ''))
        .filter(keyword => keyword.length > 2)
        .filter(keyword => !['com', 'org', 'net', 'www', 'http', 'https'].includes(keyword));
    } catch (error) {
      return [];
    }
  }

  private splitFilename(filename: string): [string, string] {
    const lastDot = filename.lastIndexOf('.');
    if (lastDot === -1) {
      return [filename, 'md'];
    }

    return [filename.substring(0, lastDot), filename.substring(lastDot + 1)];
  }

  private generateCommitMessage(metadata: IDocumentMetadata, filePath: string): string {
    const folder = this.getFileStats(filePath).folder;
    const domain = this.extractDomain(metadata.url);
    return `Add ${folder} article from ${domain}: ${metadata.title}`;
  }

  private parseRepositoryPath(repoPath: string): IRepositoryInfo {
    if (!repoPath) {
      throw new Error('Repository path is required');
    }

    let cleanPath = repoPath;
    cleanPath = cleanPath.replace(/^https?:\/\/github\.com\//, '');
    cleanPath = cleanPath.replace(/\.git$/, '');

    const parts = cleanPath.split('/');

    if (parts.length < 2) {
      throw new Error('Invalid repository path format. Expected: owner/repo');
    }

    return {
      owner: parts[0],
      repo: parts[1],
    };
  }

  private async getFileInfo(
    token: string,
    repoInfo: IRepositoryInfo,
    path: string
  ): Promise<IGitHubFileInfo | null> {
    this.logger.debug('Fetching file info for:', {
      owner: repoInfo.owner,
      repo: repoInfo.repo,
      path,
    });

    try {
      const response = await fetch(
        `${FileManager.API_BASE}/repos/${repoInfo.owner}/${repoInfo.repo}/contents/${path}`,
        {
          method: 'GET',
          headers: this.getAuthHeaders(token),
        }
      );

      if (response.status === 404) {
        this.logger.debug('File not found (404), returning null');
        return null;
      }

      if (!response.ok) {
        throw new Error(`GitHub API error: ${response.status} ${response.statusText}`);
      }

      const data = (await response.json()) as IGitHubFileInfo;

      if (!data.sha) {
        throw new Error('Invalid file info from GitHub: missing SHA');
      }

      return data;
    } catch (error) {
      if ((error as Error).message.includes('404')) {
        return null;
      }
      throw error;
    }
  }

  private async createOrUpdateFile(
    token: string,
    repoInfo: IRepositoryInfo,
    path: string,
    content: string,
    message: string,
    existingSha?: string,
    alreadyBase64?: boolean
  ): Promise<any> {
    this.logger.debug('Creating or updating file:', {
      owner: repoInfo.owner,
      repo: repoInfo.repo,
      path,
      contentLength: content.length,
      operation: existingSha ? 'UPDATE' : 'CREATE',
    });

    const requestBody: any = {
      message,
      content: alreadyBase64 ? content : encodeContentToBase64(content),
      branch: 'main',
    };

    if (existingSha) {
      requestBody.sha = existingSha;
      this.logger.info('Including SHA for file update:', existingSha);
    }

    const response = await fetch(
      `${FileManager.API_BASE}/repos/${repoInfo.owner}/${repoInfo.repo}/contents/${path}`,
      {
        method: 'PUT',
        headers: {
          ...this.getAuthHeaders(token),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = `GitHub API error: ${response.status} - ${errorData.message || 'Unknown error'}`;
      throw new Error(errorMessage);
    }

    return await response.json();
  }

  private async validateToken(token: string): Promise<any> {
    this.logger.debug('Validating GitHub token...');

    const response = await fetch(`${FileManager.API_BASE}/user`, {
      headers: this.getAuthHeaders(token),
    });

    if (!response.ok) {
      throw new Error(`Invalid GitHub token (${response.status})`);
    }

    const userData = await response.json();
    this.logger.debug('GitHub user validated:', userData.login);
    return userData;
  }

  private async validateRepository(token: string, repoInfo: IRepositoryInfo): Promise<any> {
    this.logger.debug('Validating repository access...');

    const response = await fetch(
      `${FileManager.API_BASE}/repos/${repoInfo.owner}/${repoInfo.repo}`,
      {
        headers: this.getAuthHeaders(token),
      }
    );

    if (!response.ok) {
      const errorMsg =
        response.status === 404
          ? 'Repository not found or no access'
          : `Repository access failed (${response.status})`;
      throw new Error(errorMsg);
    }

    const repoData = await response.json();
    this.logger.debug('Repository access confirmed:', repoData.full_name);
    return repoData;
  }

  private async checkWritePermissions(token: string, repoInfo: IRepositoryInfo): Promise<boolean> {
    this.logger.debug('Testing write permissions...');

    try {
      const response = await fetch(
        `${FileManager.API_BASE}/repos/${repoInfo.owner}/${repoInfo.repo}/contents`,
        {
          headers: this.getAuthHeaders(token),
        }
      );

      const hasAccess = response.ok;
      if (!hasAccess) {
        this.logger.warn('Limited repository access - may not have write permissions');
      }

      return hasAccess;
    } catch (error) {
      this.logger.warn('Write permission check failed:', error);
      return false;
    }
  }

  private getAuthHeaders(token: string): Record<string, string> {
    return {
      Authorization: `token ${token}`,
      Accept: 'application/vnd.github.v3+json',
      'User-Agent': FileManager.USER_AGENT,
    };
  }
}
