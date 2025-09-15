import { BOOKMARKLET_CONFIG } from './config';

/**
 * Form data interface for bookmarklet generator input fields.
 * Contains all the user-provided configuration values needed to generate a personalized bookmarklet.
 */
interface IFormData {
  githubToken: string;
  githubRepo: string;
  defaultFolder: string;
  commitMessage: string;
  fileNaming: string;
}

/**
 * Configuration interface for bookmarklet functionality.
 * Defines the complete set of options that can be embedded in a generated bookmarklet.
 */
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

/**
 * Bookmarklet Generator UI Class
 *
 * This class provides a complete web-based interface for generating personalized bookmarklets
 * for the PrismWeave browser extension. It handles form validation, bookmarklet generation,
 * and provides download/copy functionality for the generated bookmarklets.
 *
 * Key Features:
 * - Real-time form validation with user-friendly error messages
 * - Automatic detection of injectable script URLs (local vs production)
 * - Secure handling of GitHub tokens (not saved in localStorage)
 * - Generation of compact, self-contained bookmarklets
 * - Download functionality for bookmarklet HTML pages
 * - Clipboard copy functionality with fallback for older browsers
 *
 * Security Considerations:
 * - GitHub tokens are embedded in bookmarklets but never saved to localStorage
 * - Form validation prevents common input errors
 * - Generated bookmarklets include security warnings in download pages
 */
class BookmarkletGeneratorUI {
  private form: HTMLFormElement;
  private statusMessage: HTMLElement;
  private resultSection: HTMLElement;
  private bookmarkletLink: HTMLAnchorElement;
  private bookmarkletCodeDisplay: HTMLElement;
  private currentBookmarkletCode: string = '';

  private readonly injectableBaseUrl: string = this.detectInjectableBaseUrl();

  /**
   * Creates a new BookmarkletGeneratorUI instance.
   * Initializes DOM element references and sets up the injectable base URL for bookmarklet generation.
   * @throws Error if required DOM elements are not found
   */
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

  /**
   * Detects the appropriate base URL for the injectable content extractor script.
   * Automatically determines whether to use local development URLs or production URLs
   * based on the current page location.
   *
   * @returns The base URL for the injectable script
   * @private
   */
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

  /**
   * Initializes the bookmarklet generator interface.
   * Sets up event listeners and loads any previously saved settings from localStorage.
   * This method is called automatically by the constructor.
   */
  init(): void {
    this.bindEvents();
    this.loadSavedSettings();
  }

  /**
   * Binds all event listeners for the bookmarklet generator interface.
   * Sets up form submission, real-time validation, and result section interactions.
   * This method establishes the complete event-driven behavior of the UI.
   */
  bindEvents(): void {
    this.form.addEventListener('submit', e => this.handleSubmit(e));

    // Real-time validation
    const tokenInput = document.getElementById('github-token') as HTMLInputElement;
    const repoInput = document.getElementById('github-repo') as HTMLInputElement;

    tokenInput.addEventListener('blur', () => this.validateToken());
    repoInput.addEventListener('blur', () => this.validateRepo());
  }

  /**
   * Loads previously saved settings from localStorage.
   * Restores user preferences while maintaining security by not restoring the GitHub token.
   * Gracefully handles any localStorage errors to prevent initialization failures.
   */
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

  /**
   * Saves user settings to localStorage for future sessions.
   * Excludes the GitHub token from storage for security reasons.
   * Gracefully handles localStorage errors without disrupting the user experience.
   *
   * @param formData - The form data containing user settings to save
   */
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

  /**
   * Handles form submission for bookmarklet generation.
   * Validates form data, generates the bookmarklet, displays results, and saves settings.
   * Provides user feedback through status messages and handles errors gracefully.
   *
   * @param e - The form submission event
   */
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

  /**
   * Extracts and validates form data from the HTML form elements.
   * Collects all user input values and trims whitespace for consistent processing.
   *
   * @returns The validated form data object
   */
  getFormData(): IFormData {
    return {
      githubToken: (document.getElementById('github-token') as HTMLInputElement).value.trim(),
      githubRepo: (document.getElementById('github-repo') as HTMLInputElement).value.trim(),
      defaultFolder: (document.getElementById('default-folder') as HTMLSelectElement).value,
      commitMessage: (document.getElementById('commit-message') as HTMLInputElement).value.trim(),
      fileNaming: (document.getElementById('file-naming') as HTMLSelectElement).value,
    };
  }

  /**
   * Converts form data to the bookmarklet configuration format.
   * Maps form field values to the configuration structure expected by the bookmarklet.
   * Sets sensible defaults for optional configuration values.
   *
   * @param formData - The form data to convert
   * @returns The bookmarklet configuration object
   */
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

  /**
   * Generates a compact, self-contained bookmarklet with embedded configuration.
   * Creates a bookmarklet that loads the sophisticated content extractor and processes
   * the current page using the user's GitHub configuration.
   *
   * The generated bookmarklet:
   * - Embeds user configuration directly in the code
   * - Dynamically loads the content extractor script
   * - Processes the page with advanced extraction options
   * - Provides user feedback through browser alerts
   * - Handles errors gracefully with informative messages
   *
   * @param formData - The form data containing user configuration
   * @returns The complete bookmarklet code as a javascript: URL
   */
  generateCompactBookmarklet(formData: IFormData): string {
    const token = formData.githubToken;
    const repo = formData.githubRepo;
    const folder = formData.defaultFolder;
    const msgTemplate = formData.commitMessage || 'PrismWeave: Add {title}';
    const injectableUrl = this.injectableBaseUrl + '/content-extractor-injectable.js';

    // Build the bookmarklet JavaScript using script injection to load sophisticated extractor
    const jsCode = [
      '(function(){',
      // Check if toast utility is loaded from injectable bundle
      'if(!window.prismweaveShowToast){',
      '  alert("❌ PrismWeave utilities not loaded. Please ensure the injectable script is available.");',
      '  return;',
      '}',

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
      '    var commitUrl = result.data && result.data.html_url ? result.data.html_url : null;',
      "    window.prismweaveShowToast('✅ Page captured successfully!', {type: 'success', clickUrl: commitUrl, linkLabel: 'View on GitHub'});",
      '  } else {',
      "    var errMsg='❌ Capture failed: ' + (result.error || 'Unknown error');window.prismweaveShowToast(errMsg, {type: 'error'});",
      '  }',
      '}).catch(function(error){',
      "  var bmErr='❌ Bookmarklet error: ' + error.message;window.prismweaveShowToast(bmErr, {type: 'error'});",
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

  /**
   * Validates the GitHub token field in real-time.
   * Checks for presence, length, and proper token format.
   * Updates the validation error message display accordingly.
   */
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

  /**
   * Validates the GitHub repository field in real-time.
   * Checks for presence and proper repository format (owner/repo).
   * Updates the validation error message display accordingly.
   */
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

  /**
   * Displays a validation error message for a specific form field.
   * Updates the error message element with the provided error text.
   *
   * @param fieldId - The ID of the error message element to update
   * @param message - The error message to display
   */
  showFieldError(fieldId: string, message: string): void {
    const errorEl = document.getElementById(fieldId);
    if (errorEl) {
      errorEl.textContent = message;
    }
  }

  /**
   * Displays a status message to the user with appropriate styling.
   * Automatically hides success messages after 5 seconds.
   * Used for providing feedback during bookmarklet generation and other operations.
   *
   * @param message - The status message to display
   * @param type - The type of status message (info, success, or error)
   */
  showStatus(message: string, type: 'info' | 'success' | 'error'): void {
    this.statusMessage.innerHTML = `<div class="status-message status-${type}">${message}</div>`;

    // Auto-hide success messages
    if (type === 'success') {
      setTimeout(() => {
        this.statusMessage.innerHTML = '';
      }, 5000);
    }
  }

  /**
   * Displays the generated bookmarklet results to the user.
   * Updates the bookmarklet link, shows the truncated code, and reveals the result section.
   * Provides visual feedback that the bookmarklet has been successfully generated.
   *
   * @param bookmarkletCode - The generated bookmarklet code
   * @param formData - The form data used to generate the bookmarklet
   */
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
}

// =============================================================================
// INITIALIZATION
// =============================================================================

/**
 * Initializes the BookmarkletGeneratorUI when the DOM is ready.
 * Ensures the generator is only created after all DOM elements are available.
 * Uses both immediate initialization (if DOM is already loaded) and event listener
 * (if DOM is still loading) to handle all scenarios.
 */
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new BookmarkletGeneratorUI();
  });
} else {
  new BookmarkletGeneratorUI();
}
