import { BOOKMARKLET_CONFIG } from './config';

interface IFormData {
  githubToken: string;
  githubRepo: string;
  defaultFolder: string;
  commitMessage: string;
  fileNaming: string;
}

interface IBookmarkletConfig {
  githubToken: string;
  githubRepo: string;
  defaultFolder?: string;
  commitMessageTemplate?: string;
  fileNamingPattern?: string;
  captureImages?: boolean;
  removeAds?: boolean;
  removeNavigation?: boolean;
}

class BookmarkletGeneratorUI {
  private form: HTMLFormElement;
  private statusMessage: HTMLElement;
  private resultSection: HTMLElement;
  private bookmarkletLink: HTMLAnchorElement;
  private bookmarkletCodeDisplay: HTMLElement;
  private currentBookmarkletCode: string = '';

  private readonly injectableBaseUrl: string = this.detectInjectableBaseUrl();

  constructor() {
    this.form = document.getElementById('generator-form') as HTMLFormElement;
    this.statusMessage = document.getElementById('status-message') as HTMLElement;
    this.resultSection = document.getElementById('result-section') as HTMLElement;
    this.bookmarkletLink = document.getElementById('bookmarklet-link') as HTMLAnchorElement;
    this.bookmarkletCodeDisplay = document.getElementById(
      'bookmarklet-code-display'
    ) as HTMLElement;

    this.init();
  }

  private detectInjectableBaseUrl(): string {
    const configElement = document.querySelector('[data-injectable-url]') as HTMLElement;
    if (configElement?.dataset.injectableUrl) {
      return configElement.dataset.injectableUrl;
    }

    const currentUrl = window.location.href;

    if (currentUrl.includes('localhost') || currentUrl.startsWith('file://')) {
      return BOOKMARKLET_CONFIG.LOCAL_INJECTABLE_BASE;
    }

    return BOOKMARKLET_CONFIG.DEFAULT_INJECTABLE_BASE;
  }

  init(): void {
    this.bindEvents();
    this.loadSavedSettings();
  }

  bindEvents(): void {
    this.form.addEventListener('submit', e => this.handleSubmit(e));

    // Real-time validation
    const tokenInput = document.getElementById('github-token') as HTMLInputElement;
    const repoInput = document.getElementById('github-repo') as HTMLInputElement;

    tokenInput.addEventListener('blur', () => this.validateToken());
    repoInput.addEventListener('blur', () => this.validateRepo());

    // Result section buttons
    document.getElementById('copy-btn')?.addEventListener('click', () => this.copyBookmarklet());
    document
      .getElementById('download-btn')
      ?.addEventListener('click', () => this.downloadBookmarklet());
  }

  loadSavedSettings(): void {
    try {
      const saved = localStorage.getItem('prismweave_generator_settings');
      if (saved) {
        const settings = JSON.parse(saved);

        // Don't restore the token for security
        if (settings.githubRepo) {
          (document.getElementById('github-repo') as HTMLInputElement).value = settings.githubRepo;
        }
        if (settings.defaultFolder) {
          (document.getElementById('default-folder') as HTMLSelectElement).value =
            settings.defaultFolder;
        }
        if (settings.commitMessage) {
          (document.getElementById('commit-message') as HTMLInputElement).value =
            settings.commitMessage;
        }
        if (settings.fileNaming) {
          (document.getElementById('file-naming') as HTMLSelectElement).value = settings.fileNaming;
        }
      }
    } catch (error) {
      console.warn('Failed to load saved settings:', error);
    }
  }

  saveSettings(formData: IFormData): void {
    try {
      const settingsToSave = {
        githubRepo: formData.githubRepo,
        defaultFolder: formData.defaultFolder,
        commitMessage: formData.commitMessage,
        fileNaming: formData.fileNaming,
        // Intentionally not saving the token
      };

      localStorage.setItem('prismweave_generator_settings', JSON.stringify(settingsToSave));
    } catch (error) {
      console.warn('Failed to save settings:', error);
    }
  }

  handleSubmit(e: Event): void {
    e.preventDefault();

    const formData = this.getFormData();

    if (!this.validateForm(formData)) {
      this.showStatus('Please fix the validation errors above.', 'error');
      return;
    }

    this.showStatus('Generating your personalized bookmarklet...', 'info');

    try {
      // Generate a compact, self-contained bookmarklet instead of the loader version
      const bookmarkletCode = this.generateCompactBookmarklet(formData);

      this.currentBookmarkletCode = bookmarkletCode;
      this.displayResult(bookmarkletCode, formData);
      this.saveSettings(formData);

      this.showStatus('✅ Bookmarklet generated successfully!', 'success');
    } catch (error) {
      this.showStatus(`❌ Generation failed: ${(error as Error).message}`, 'error');
      console.error('Bookmarklet generation failed:', error);
    }
  }

  getFormData(): IFormData {
    return {
      githubToken: (document.getElementById('github-token') as HTMLInputElement).value.trim(),
      githubRepo: (document.getElementById('github-repo') as HTMLInputElement).value.trim(),
      defaultFolder: (document.getElementById('default-folder') as HTMLSelectElement).value,
      commitMessage: (document.getElementById('commit-message') as HTMLInputElement).value.trim(),
      fileNaming: (document.getElementById('file-naming') as HTMLSelectElement).value,
    };
  }

  convertToBookmarkletConfig(formData: IFormData): IBookmarkletConfig {
    return {
      githubToken: formData.githubToken,
      githubRepo: formData.githubRepo,
      defaultFolder: formData.defaultFolder,
      commitMessageTemplate: formData.commitMessage,
      fileNamingPattern: formData.fileNaming,
      captureImages: true,
      removeAds: true,
      removeNavigation: true,
    };
  }

  generateCompactBookmarklet(formData: IFormData): string {
    const token = formData.githubToken;
    const repo = formData.githubRepo;
    const folder = formData.defaultFolder;
    const msgTemplate = formData.commitMessage || 'PrismWeave: Add {title}';
    const injectableUrl = this.injectableBaseUrl + '/content-extractor-injectable.js';

    // Build the bookmarklet JavaScript using script injection to load sophisticated extractor
    const jsCode = [
      '(function(){',
      // Configuration for the extractor (match the IGitHubConfig interface)
      'var config = {',
      "  token: '" + token + "',",
      "  repository: '" + repo + "',",
      "  folder: '" + folder + "',",
      "  commitMessage: '" + msgTemplate + "'",
      '};',

      // Load the injectable content extractor
      'function loadExtractor(){',
      '  return new Promise(function(resolve, reject){',
      '    if(window.prismweaveExtractAndCommit){',
      '      resolve();',
      '      return;',
      '    }',
      '    var script = document.createElement("script");',
      '    script.src = "' + injectableUrl + '";',
      '    script.onload = function(){',
      '      if(window.prismweaveExtractAndCommit){',
      '        resolve();',
      '      } else {',
      '        reject(new Error("Failed to load extractor API"));',
      '      }',
      '    };',
      '    script.onerror = function(){',
      '      reject(new Error("Failed to load extractor script"));',
      '    };',
      '    document.head.appendChild(script);',
      '  });',
      '}',

      // Process the page using the sophisticated extractor
      'function processPage(){',
      '  var extractionOptions = {',
      '    includeImages: true,',
      '    includeLinks: true,',
      '    cleanHtml: true,',
      '    generateFrontmatter: true,',
      '    includeMetadata: true',
      '  };',

      '  return window.prismweaveExtractAndCommit(config, extractionOptions);',
      '}',

      // Main execution flow
      'loadExtractor().then(function(){',
      '  return processPage();',
      '}).then(function(result){',
      '  if(result.success){',
      "    alert('✅ Page captured successfully with advanced extraction!');",
      '  } else {',
      "    alert('❌ Capture failed: ' + (result.error || 'Unknown error'));",
      '  }',
      '}).catch(function(error){',
      "  alert('❌ Bookmarklet error: ' + error.message);",
      '});',
      '})();',
    ].join('');

    return 'javascript:' + encodeURIComponent(jsCode);
  }

  validateForm(formData: IFormData): boolean {
    let isValid = true;

    // Clear previous errors
    document.querySelectorAll('.validation-error').forEach(el => {
      el.textContent = '';
    });

    // Validate token
    if (!formData.githubToken) {
      this.showFieldError('token-error', 'GitHub token is required');
      isValid = false;
    } else if (formData.githubToken.length < 20) {
      this.showFieldError('token-error', 'GitHub token appears to be invalid (too short)');
      isValid = false;
    } else if (
      !formData.githubToken.startsWith('ghp_') &&
      !formData.githubToken.startsWith('github_pat_')
    ) {
      this.showFieldError(
        'token-error',
        'Token should start with "ghp_" (classic) or "github_pat_" (fine-grained)'
      );
      isValid = false;
    }

    // Validate repository
    if (!formData.githubRepo) {
      this.showFieldError('repo-error', 'GitHub repository is required');
      isValid = false;
    } else if (!/^[\w\-\.]+\/[\w\-\.]+$/.test(formData.githubRepo)) {
      this.showFieldError('repo-error', 'Repository must be in format: owner/repo');
      isValid = false;
    }

    return isValid;
  }

  validateToken(): void {
    const token = (document.getElementById('github-token') as HTMLInputElement).value.trim();
    const errorEl = document.getElementById('token-error') as HTMLElement;

    if (!token) {
      errorEl.textContent = 'GitHub token is required';
    } else if (token.length < 20) {
      errorEl.textContent = 'GitHub token appears to be invalid (too short)';
    } else if (!token.startsWith('ghp_') && !token.startsWith('github_pat_')) {
      errorEl.textContent = 'Token should start with "ghp_" or "github_pat_"';
    } else {
      errorEl.textContent = '';
    }
  }

  validateRepo(): void {
    const repo = (document.getElementById('github-repo') as HTMLInputElement).value.trim();
    const errorEl = document.getElementById('repo-error') as HTMLElement;

    if (!repo) {
      errorEl.textContent = 'GitHub repository is required';
    } else if (!/^[\w\-\.]+\/[\w\-\.]+$/.test(repo)) {
      errorEl.textContent = 'Repository must be in format: owner/repo';
    } else {
      errorEl.textContent = '';
    }
  }

  showFieldError(fieldId: string, message: string): void {
    const errorEl = document.getElementById(fieldId);
    if (errorEl) {
      errorEl.textContent = message;
    }
  }

  showStatus(message: string, type: 'info' | 'success' | 'error'): void {
    this.statusMessage.innerHTML = `<div class="status-message status-${type}">${message}</div>`;

    // Auto-hide success messages
    if (type === 'success') {
      setTimeout(() => {
        this.statusMessage.innerHTML = '';
      }, 5000);
    }
  }

  displayResult(bookmarkletCode: string, formData: IFormData): void {
    // Update bookmarklet link
    this.bookmarkletLink.href = bookmarkletCode;
    this.bookmarkletLink.title = `PrismWeave → ${formData.githubRepo}`;

    // Update code display (truncated for security/readability)
    const truncatedCode =
      bookmarkletCode.length > 200
        ? bookmarkletCode.substring(0, 200) + '...[truncated]'
        : bookmarkletCode;
    this.bookmarkletCodeDisplay.textContent = truncatedCode;

    // Show result section with animation
    this.resultSection.classList.add('show');
    this.resultSection.scrollIntoView({ behavior: 'smooth' });
  }

  async copyBookmarklet(): Promise<void> {
    try {
      await navigator.clipboard.writeText(this.currentBookmarkletCode);
      this.showStatus('📋 Bookmarklet copied to clipboard!', 'success');
    } catch (error) {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = this.currentBookmarkletCode;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);

      this.showStatus('📋 Bookmarklet copied to clipboard! (fallback method)', 'success');
    }
  }

  downloadBookmarklet(): void {
    const formData = this.getFormData();
    const repoName = formData.githubRepo.split('/')[1] || 'repository';

    const html = this.generateBookmarkletPage(formData);
    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `prismweave-bookmarklet-${repoName}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    this.showStatus('💾 Bookmarklet HTML page downloaded!', 'success');
  }

  generateBookmarkletPage(formData: IFormData): string {
    const repoName = formData.githubRepo.split('/')[1] || 'repository';
    const currentDate = new Date().toLocaleDateString();

    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PrismWeave Bookmarklet - ${repoName}</title>
  <!-- Use shared UI styles and a lightweight page stylesheet to avoid inline CSS -->
  <link rel="stylesheet" href="../styles/shared-ui.css">
  <link rel="stylesheet" href="../styles/bookmarklet-download.css">
</head>
<body class="pw-font-sans">
  <div class="pw-page-header">
        <h1>🌟 PrismWeave Bookmarklet</h1>
        <p>Personal bookmarklet for <strong>${formData.githubRepo}</strong></p>
        <p><em>Generated on ${currentDate}</em></p>
    </div>

  <div class="pw-card pw-bookmarklet-cta">
        <h3>Drag this to your bookmarks bar:</h3>
    <a href="${this.currentBookmarkletCode}" class="pw-btn pw-btn-primary">📄 PrismWeave → ${repoName}</a>
    <p class="pw-note"><small>Your GitHub settings are embedded - no setup required!</small></p>
    </div>

  <div class="pw-card pw-section">
        <h3>📋 Installation Instructions:</h3>
        <ol>
            <li><strong>Drag & Drop:</strong> Drag the bookmarklet button above to your browser's bookmarks bar</li>
            <li><strong>Manual Method:</strong>
        <ul class="pw-list">
                    <li>Right-click the bookmarklet button and copy the link</li>
                    <li>Add a new bookmark in your browser</li>
                    <li>Set the name to "PrismWeave → ${repoName}" and paste the copied link as the URL</li>
                </ul>
            </li>
            <li><strong>Usage:</strong> Visit any webpage and click your bookmarklet to capture content</li>
        </ol>
    </div>

  <div class="pw-info pw-section">
        <h4>⚙️ Configuration Summary:</h4>
        <ul>
            <li><strong>Repository:</strong> ${formData.githubRepo}</li>
            <li><strong>Default Folder:</strong> ${formData.defaultFolder}</li>
            <li><strong>Commit Message:</strong> ${formData.commitMessage}</li>
            <li><strong>File Naming:</strong> ${formData.fileNaming}</li>
        </ul>
    </div>

  <div class="pw-info pw-section">
        <h4>🔒 Security Note:</h4>
        <p>This bookmarklet contains your GitHub Personal Access Token. Keep this file private and only share the bookmarklet with trusted parties.</p>
    </div>
</body>
</html>`;
  }
}

// Initialize the generator when the DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new BookmarkletGeneratorUI();
  });
} else {
  new BookmarkletGeneratorUI();
}
