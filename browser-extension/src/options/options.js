// PrismWeave Options/Settings Page Script

class PrismWeaveOptions {
  constructor() {
    this.settings = {};
    this.initializeOptions();
  }

  async initializeOptions() {
    await this.loadSettings();
    this.populateForm();
    this.setupEventListeners();
  }

  async loadSettings() {
    try {
      const response = await chrome.runtime.sendMessage({ action: 'GET_SETTINGS' });
      if (response.success) {
        this.settings = response.data;
      } else {
        this.settings = this.getDefaultSettings();
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
      this.settings = this.getDefaultSettings();
    }
  }

  getDefaultSettings() {
    return {
      githubToken: '',
      githubRepo: '',
      defaultFolder: 'unsorted',
      customFolder: '',
      namingPattern: 'YYYY-MM-DD-domain-title',
      autoCommit: false,
      autoPush: false,
      captureImages: true,
      removeAds: true,
      removeNavigation: true,
      preserveLinks: true,
      customSelectors: '',
      commitMessageTemplate: 'Add: {domain} - {title}',
      enableKeyboardShortcuts: true,
      showNotifications: true,
    };
  }

  populateForm() {
    // Repository settings
    document.getElementById('github-token').value = this.settings.githubToken || '';
    document.getElementById('github-repo').value = this.settings.githubRepo || '';

    // Capture settings
    document.getElementById('default-folder').value = this.settings.defaultFolder || 'unsorted';
    document.getElementById('custom-folder').value = this.settings.customFolder || '';
    document.getElementById('naming-pattern').value =
      this.settings.namingPattern || 'YYYY-MM-DD-domain-title';

    // Checkboxes
    document.getElementById('auto-commit').checked = this.settings.autoCommit || false;
    document.getElementById('auto-push').checked = this.settings.autoPush || false;
    document.getElementById('capture-images').checked = this.settings.captureImages !== false;

    // Content processing
    document.getElementById('remove-ads').checked = this.settings.removeAds !== false;
    document.getElementById('remove-navigation').checked = this.settings.removeNavigation !== false;
    document.getElementById('preserve-links').checked = this.settings.preserveLinks !== false;
    document.getElementById('custom-selectors').value = this.settings.customSelectors || '';

    // Advanced options
    document.getElementById('commit-message-template').value =
      this.settings.commitMessageTemplate || 'Add: {domain} - {title}';
    document.getElementById('enable-keyboard-shortcuts').checked =
      this.settings.enableKeyboardShortcuts !== false;
    document.getElementById('show-notifications').checked =
      this.settings.showNotifications !== false;

    // Handle custom folder visibility
    this.toggleCustomFolder();
  }

  setupEventListeners() {
    // Save settings button
    document.getElementById('save-settings').addEventListener('click', () => {
      this.saveSettings();
    });

    // Reset settings button
    document.getElementById('reset-settings').addEventListener('click', () => {
      this.resetSettings();
    });

    // Export/Import settings
    document.getElementById('export-settings').addEventListener('click', () => {
      this.exportSettings();
    });

    document.getElementById('import-settings').addEventListener('click', () => {
      document.getElementById('import-file').click();
    });

    document.getElementById('import-file').addEventListener('change', e => {
      this.importSettings(e.target.files[0]);
    });

    // Test GitHub connection
    document.getElementById('test-github').addEventListener('click', () => {
      this.testGitHubConnection();
    });

    // Default folder change handler
    document.getElementById('default-folder').addEventListener('change', () => {
      this.toggleCustomFolder();
    });

    // Real-time validation
    document.getElementById('github-token').addEventListener('input', () => {
      this.validateGitHubToken();
    });

    document.getElementById('github-repo').addEventListener('input', () => {
      this.validateGitHubRepo();
    });

    // Auto-save on certain changes
    const autoSaveFields = [
      'auto-commit',
      'auto-push',
      'capture-images',
      'remove-ads',
      'remove-navigation',
    ];
    autoSaveFields.forEach(fieldId => {
      document.getElementById(fieldId).addEventListener('change', () => {
        this.autoSave();
      });
    });
  }

  toggleCustomFolder() {
    const defaultFolder = document.getElementById('default-folder').value;
    const customFolderGroup = document.getElementById('custom-folder');
    const customFolderLabel = document.querySelector('label[for="custom-folder"]');

    if (defaultFolder === 'custom') {
      customFolderGroup.style.display = 'block';
      customFolderLabel.style.display = 'block';
    } else {
      customFolderGroup.style.display = 'none';
      customFolderLabel.style.display = 'none';
    }
  }

  async saveSettings() {
    try {
      // Collect form data
      const formData = {
        githubToken: document.getElementById('github-token').value.trim(),
        githubRepo: document.getElementById('github-repo').value.trim(),
        defaultFolder: document.getElementById('default-folder').value,
        customFolder: document.getElementById('custom-folder').value.trim(),
        namingPattern: document.getElementById('naming-pattern').value,
        autoCommit: document.getElementById('auto-commit').checked,
        autoPush: document.getElementById('auto-push').checked,
        captureImages: document.getElementById('capture-images').checked,
        removeAds: document.getElementById('remove-ads').checked,
        removeNavigation: document.getElementById('remove-navigation').checked,
        preserveLinks: document.getElementById('preserve-links').checked,
        customSelectors: document.getElementById('custom-selectors').value.trim(),
        commitMessageTemplate: document.getElementById('commit-message-template').value.trim(),
        enableKeyboardShortcuts: document.getElementById('enable-keyboard-shortcuts').checked,
        showNotifications: document.getElementById('show-notifications').checked,
      };

      // Validate required fields
      if (!this.validateSettings(formData)) {
        return;
      }

      // Save to storage
      const response = await chrome.runtime.sendMessage({
        action: 'UPDATE_SETTINGS',
        settings: formData,
      });

      if (response.success) {
        this.settings = formData;
        this.showStatus('Settings saved successfully!', 'success');
      } else {
        throw new Error(response.error);
      }
    } catch (error) {
      console.error('Failed to save settings:', error);
      this.showStatus('Failed to save settings: ' + error.message, 'error');
    }
  }

  validateSettings(settings) {
    // Basic validation
    if (settings.autoPush && !settings.githubToken) {
      this.showStatus('GitHub token is required for auto-push', 'error');
      return false;
    }

    if (settings.autoPush && !settings.githubRepo) {
      this.showStatus('GitHub repository is required for auto-push', 'error');
      return false;
    }

    if (settings.defaultFolder === 'custom' && !settings.customFolder) {
      this.showStatus('Custom folder name is required', 'error');
      return false;
    }

    return true;
  }

  async resetSettings() {
    if (confirm('Are you sure you want to reset all settings to defaults?')) {
      this.settings = this.getDefaultSettings();
      this.populateForm();
      await this.saveSettings();
      this.showStatus('Settings reset to defaults', 'success');
    }
  }

  exportSettings() {
    const dataStr = JSON.stringify(this.settings, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement('a');
    link.href = url;
    link.download = 'prismweave-settings.json';
    link.click();

    URL.revokeObjectURL(url);
    this.showStatus('Settings exported successfully', 'success');
  }

  async importSettings(file) {
    if (!file) return;

    try {
      const text = await file.text();
      const importedSettings = JSON.parse(text);

      // Validate imported settings structure
      const defaultSettings = this.getDefaultSettings();
      const validatedSettings = { ...defaultSettings };

      Object.keys(defaultSettings).forEach(key => {
        if (importedSettings.hasOwnProperty(key)) {
          validatedSettings[key] = importedSettings[key];
        }
      });

      this.settings = validatedSettings;
      this.populateForm();
      this.showStatus('Settings imported successfully', 'success');
    } catch (error) {
      console.error('Failed to import settings:', error);
      this.showStatus('Failed to import settings: Invalid file format', 'error');
    }
  }
  async testGitHubConnection() {
    const token = document.getElementById('github-token').value.trim();
    const repo = document.getElementById('github-repo').value.trim();
    const testButton = document.getElementById('test-github');

    if (!token) {
      this.showTestResult('GitHub token is required', 'error');
      return;
    }

    testButton.disabled = true;
    testButton.textContent = 'Testing...';

    try {
      // Pass repo and token to background script for connection test
      const response = await chrome.runtime.sendMessage({
        action: 'TEST_CONNECTION',
        githubRepo: repo,
        githubToken: token,
      });

      if (response.success && response.data.success) {
        let message = `✓ Connected as ${response.data.username}`;

        if (repo) {
          // Test repository access
          const repoResponse = await chrome.runtime.sendMessage({
            action: 'VALIDATE_REPOSITORY',
            githubRepo: repo,
            githubToken: token,
          });

          if (repoResponse.success && repoResponse.data.success) {
            message += `. Repository '${repoResponse.data.name}' accessible.`;
            if (!repoResponse.data.hasWrite) {
              message += ' (Read-only access)';
            }
          } else {
            message += `. ⚠ Repository not accessible: ${repoResponse.data?.error || 'Unknown error'}`;
          }
        }

        this.showTestResult(message, 'success');
      } else {
        throw new Error(response.data?.error || 'Connection test failed');
      }
    } catch (error) {
      console.error('GitHub connection test failed:', error);
      this.showTestResult('✗ Connection failed: ' + error.message, 'error');
    } finally {
      testButton.disabled = false;
      testButton.textContent = 'Test Connection';
    }
  }

  showTestResult(message, type) {
    const resultElement = document.getElementById('github-test-result');
    resultElement.textContent = message;
    resultElement.className = `test-result ${type}`;
    resultElement.style.display = 'block';

    setTimeout(() => {
      resultElement.style.display = 'none';
    }, 5000);
  }

  validateGitHubToken() {
    const token = document.getElementById('github-token').value.trim();
    const input = document.getElementById('github-token');

    if (token && !token.startsWith('ghp_') && !token.startsWith('github_pat_')) {
      input.style.borderColor = '#f44336';
    } else {
      input.style.borderColor = '#ddd';
    }
  }

  validateGitHubRepo() {
    const repo = document.getElementById('github-repo').value.trim();
    const input = document.getElementById('github-repo');

    if (repo && !repo.match(/^[a-zA-Z0-9._-]+\/[a-zA-Z0-9._-]+$/)) {
      input.style.borderColor = '#f44336';
    } else {
      input.style.borderColor = '#ddd';
    }
  }

  async autoSave() {
    // Debounced auto-save for certain settings
    clearTimeout(this.autoSaveTimeout);
    this.autoSaveTimeout = setTimeout(() => {
      this.saveSettings();
    }, 1000);
  }

  showStatus(message, type) {
    const statusElement = document.getElementById('status');
    statusElement.textContent = message;
    statusElement.className = `status ${type}`;
    statusElement.style.display = 'block';

    setTimeout(() => {
      statusElement.style.display = 'none';
    }, 5000);
  }
}

// Initialize options page when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new PrismWeaveOptions();
});
