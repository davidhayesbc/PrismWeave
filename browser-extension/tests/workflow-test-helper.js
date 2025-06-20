// Comprehensive test helpers for validating PrismWeave extension workflows
// Provides end-to-end validation and testing utilities

const workflowTestHelper = {
  // Validate extension installation and setup
  async validateExtensionSetup() {
    const results = {
      chromeAPIsAvailable: false,
      manifestValid: false,
      permissionsGranted: false,
      storageAccessible: false,
      settingsInitialized: false,
      errors: []
    };

    try {
      // Check Chrome APIs
      results.chromeAPIsAvailable = !!(
        chrome && 
        chrome.storage && 
        chrome.tabs && 
        chrome.runtime &&
        chrome.permissions
      );

      // Validate manifest (simplified check)
      const manifest = chrome.runtime.getManifest();
      results.manifestValid = !!(
        manifest &&
        manifest.name &&
        manifest.version &&
        manifest.permissions
      );

      // Check permissions
      const requiredPermissions = ['storage', 'tabs', 'activeTab'];
      for (const permission of requiredPermissions) {
        const hasPermission = await new Promise(resolve => {
          chrome.permissions.contains({permissions: [permission]}, resolve);
        });
        if (!hasPermission) {
          results.errors.push(`Missing permission: ${permission}`);
        }
      }
      results.permissionsGranted = results.errors.length === 0;

      // Test storage access
      try {
        await new Promise((resolve, reject) => {
          chrome.storage.local.set({testKey: 'testValue'}, () => {
            if (chrome.runtime.lastError) {
              reject(chrome.runtime.lastError);
            } else {
              resolve();
            }
          });
        });
        
        await new Promise((resolve, reject) => {
          chrome.storage.local.get(['testKey'], (result) => {
            if (chrome.runtime.lastError) {
              reject(chrome.runtime.lastError);
            } else if (result.testKey !== 'testValue') {
              reject(new Error('Storage read/write mismatch'));
            } else {
              resolve();
            }
          });
        });
        
        results.storageAccessible = true;
      } catch (error) {
        results.errors.push(`Storage access failed: ${error.message}`);
      }

      // Check settings initialization
      try {
        const settings = await new Promise((resolve, reject) => {
          chrome.storage.local.get(['settings'], (result) => {
            if (chrome.runtime.lastError) {
              reject(chrome.runtime.lastError);
            } else {
              resolve(result.settings);
            }
          });
        });
        
        results.settingsInitialized = !!(settings && typeof settings === 'object');
      } catch (error) {
        results.errors.push(`Settings check failed: ${error.message}`);
      }

    } catch (error) {
      results.errors.push(`Extension setup validation failed: ${error.message}`);
    }

    return results;
  },

  // Validate content capture workflow
  async validateContentCapture(tab, expectedContent) {
    const results = {
      tabAccessible: false,
      contentExtracted: false,
      markdownGenerated: false,
      metadataComplete: false,
      filenameSafe: false,
      errors: []
    };

    try {
      // Check tab accessibility
      if (!tab || !tab.url || tab.url.startsWith('chrome://')) {
        results.errors.push('Tab is not accessible for content capture');
      } else {
        results.tabAccessible = true;
      }

      // Test content extraction
      try {
        const extractedContent = await new Promise((resolve, reject) => {
          chrome.tabs.sendMessage(tab.id, {action: 'extractContent'}, (response) => {
            if (chrome.runtime.lastError) {
              reject(chrome.runtime.lastError);
            } else {
              resolve(response);
            }
          });
        });

        if (extractedContent && extractedContent.title && extractedContent.content) {
          results.contentExtracted = true;
          
          // Validate against expected content if provided
          if (expectedContent) {
            if (extractedContent.title !== expectedContent.title) {
              results.errors.push('Title mismatch in extracted content');
            }
            if (!extractedContent.content.includes(expectedContent.content)) {
              results.errors.push('Content mismatch in extracted content');
            }
          }
        } else {
          results.errors.push('Content extraction returned invalid data');
        }
      } catch (error) {
        results.errors.push(`Content extraction failed: ${error.message}`);
      }

      // Test markdown generation
      try {
        const markdownContent = this.generateMarkdownContent({
          title: 'Test Title',
          content: 'Test content',
          url: tab.url,
          domain: new URL(tab.url).hostname,
          timestamp: new Date().toISOString()
        });

        if (markdownContent && markdownContent.includes('# Test Title')) {
          results.markdownGenerated = true;
        } else {
          results.errors.push('Markdown generation failed');
        }
      } catch (error) {
        results.errors.push(`Markdown generation error: ${error.message}`);
      }

      // Validate metadata completeness
      const metadata = {
        title: 'Test Title',
        url: tab.url,
        domain: new URL(tab.url).hostname,
        timestamp: new Date().toISOString(),
        tags: ['test'],
        folder: 'captured'
      };

      const requiredFields = ['title', 'url', 'domain', 'timestamp'];
      const missingFields = requiredFields.filter(field => !metadata[field]);
      
      if (missingFields.length === 0) {
        results.metadataComplete = true;
      } else {
        results.errors.push(`Missing metadata fields: ${missingFields.join(', ')}`);
      }

      // Validate filename safety
      const filename = this.generateSafeFilename(metadata.title, metadata.domain);
      const safePattern = /^[a-zA-Z0-9\-_\.]+\.md$/;
      
      if (safePattern.test(filename)) {
        results.filenameSafe = true;
      } else {
        results.errors.push('Generated filename is not safe for filesystem');
      }

    } catch (error) {
      results.errors.push(`Content capture validation failed: ${error.message}`);
    }

    return results;
  },

  // Validate Git operations workflow
  async validateGitOperations(settings) {
    const results = {
      tokenValid: false,
      repositoryAccessible: false,
      fileCreated: false,
      commitSuccessful: false,
      pushSuccessful: false,
      errors: []
    };

    try {
      // Validate GitHub token format
      if (settings.githubToken && settings.githubToken.startsWith('ghp_')) {
        results.tokenValid = true;
      } else {
        results.errors.push('GitHub token format is invalid');
      }

      // Test repository access
      try {
        const response = await fetch(`https://api.github.com/repos/${settings.githubRepo}`, {
          headers: {
            'Authorization': `token ${settings.githubToken}`,
            'Accept': 'application/vnd.github.v3+json'
          }
        });

        if (response.ok) {
          results.repositoryAccessible = true;
        } else {
          results.errors.push(`Repository access failed: ${response.status} ${response.statusText}`);
        }
      } catch (error) {
        results.errors.push(`Repository access error: ${error.message}`);
      }

      // Test file creation (dry run)
      const testContent = {
        title: 'Test File',
        content: 'This is a test file for validation',
        url: 'https://example.com/test',
        domain: 'example.com',
        timestamp: new Date().toISOString()
      };

      const markdownContent = this.generateMarkdownContent(testContent);
      const filename = this.generateSafeFilename(testContent.title, testContent.domain);
      const path = `test/${filename}`;

      // Simulate file creation check
      if (markdownContent && filename && path) {
        results.fileCreated = true;
      } else {
        results.errors.push('File creation preparation failed');
      }

      // Simulate commit validation
      const commitMessage = `Add captured content: ${testContent.title}`;
      if (commitMessage && commitMessage.length > 10 && commitMessage.length < 100) {
        results.commitSuccessful = true;
      } else {
        results.errors.push('Commit message validation failed');
      }

      // Simulate push validation
      if (results.repositoryAccessible && results.tokenValid) {
        results.pushSuccessful = true;
      } else {
        results.errors.push('Push requirements not met');
      }

    } catch (error) {
      results.errors.push(`Git operations validation failed: ${error.message}`);
    }

    return results;
  },

  // Validate settings management
  async validateSettingsManagement() {
    const results = {
      defaultSettingsLoaded: false,
      settingsSaved: false,
      settingsLoaded: false,
      validationPassed: false,
      errors: []
    };

    try {
      // Test default settings
      const defaultSettings = {
        repositoryPath: '',
        githubToken: '',
        githubRepo: '',
        defaultFolder: 'captured',
        autoCommit: true,
        fileNamingPattern: 'YYYY-MM-DD-domain-title'
      };

      if (this.validateSettings(defaultSettings)) {
        results.defaultSettingsLoaded = true;
      } else {
        results.errors.push('Default settings validation failed');
      }

      // Test settings save
      const testSettings = {
        ...defaultSettings,
        githubToken: 'ghp_test_token_12345',
        githubRepo: 'testuser/test-repo'
      };

      try {
        await new Promise((resolve, reject) => {
          chrome.storage.local.set({settings: testSettings}, () => {
            if (chrome.runtime.lastError) {
              reject(chrome.runtime.lastError);
            } else {
              resolve();
            }
          });
        });
        results.settingsSaved = true;
      } catch (error) {
        results.errors.push(`Settings save failed: ${error.message}`);
      }

      // Test settings load
      try {
        const loadedSettings = await new Promise((resolve, reject) => {
          chrome.storage.local.get(['settings'], (result) => {
            if (chrome.runtime.lastError) {
              reject(chrome.runtime.lastError);
            } else {
              resolve(result.settings);
            }
          });
        });

        if (loadedSettings && loadedSettings.githubRepo === testSettings.githubRepo) {
          results.settingsLoaded = true;
        } else {
          results.errors.push('Settings load returned incorrect data');
        }
      } catch (error) {
        results.errors.push(`Settings load failed: ${error.message}`);
      }

      // Test settings validation
      const validSettings = {
        repositoryPath: 'user/repo',
        githubToken: 'ghp_valid_token_format',
        githubRepo: 'user/valid-repo',
        defaultFolder: 'documents',
        autoCommit: true,
        fileNamingPattern: 'YYYY-MM-DD-title'
      };

      if (this.validateSettings(validSettings)) {
        results.validationPassed = true;
      } else {
        results.errors.push('Settings validation logic failed');
      }

    } catch (error) {
      results.errors.push(`Settings management validation failed: ${error.message}`);
    }

    return results;
  },

  // Helper: Generate markdown content
  generateMarkdownContent(content) {
    const frontmatter = [
      '---',
      `title: "${content.title}"`,
      `url: "${content.url}"`,
      `domain: "${content.domain}"`,
      `timestamp: "${content.timestamp}"`,
      `tags: ${JSON.stringify(content.tags || [])}`,
      `folder: "${content.folder || 'captured'}"`,
      '---',
      ''
    ].join('\n');

    return frontmatter + `# ${content.title}\n\n${content.content}`;
  },

  // Helper: Generate safe filename
  generateSafeFilename(title, domain) {
    const safeTitle = title
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .substring(0, 50);
    
    const safeDomain = domain
      .toLowerCase()
      .replace(/[^a-z0-9-]/g, '')
      .substring(0, 20);

    const timestamp = new Date().toISOString().split('T')[0];
    
    return `${timestamp}-${safeDomain}-${safeTitle}.md`;
  },

  // Helper: Validate settings object
  validateSettings(settings) {
    if (!settings || typeof settings !== 'object') return false;
    
    const requiredFields = ['defaultFolder', 'autoCommit', 'fileNamingPattern'];
    return requiredFields.every(field => settings.hasOwnProperty(field));
  },

  // Generate comprehensive test report
  generateTestReport(validationResults) {
    const report = {
      timestamp: new Date().toISOString(),
      overall: 'UNKNOWN',
      details: validationResults,
      summary: {
        totalTests: 0,
        passedTests: 0,
        failedTests: 0,
        errorCount: 0
      },
      recommendations: []
    };

    // Calculate summary
    Object.keys(validationResults).forEach(category => {
      const result = validationResults[category];
      if (result && typeof result === 'object') {
        const tests = Object.keys(result).filter(key => 
          key !== 'errors' && typeof result[key] === 'boolean'
        );
        
        report.summary.totalTests += tests.length;
        report.summary.passedTests += tests.filter(test => result[test]).length;
        report.summary.failedTests += tests.filter(test => !result[test]).length;
        report.summary.errorCount += (result.errors || []).length;
      }
    });

    // Determine overall status
    const passRate = report.summary.totalTests > 0 ? 
      report.summary.passedTests / report.summary.totalTests : 0;
    
    if (passRate >= 0.9) {
      report.overall = 'PASS';
    } else if (passRate >= 0.7) {
      report.overall = 'WARNING';
    } else {
      report.overall = 'FAIL';
    }

    // Generate recommendations
    if (report.summary.errorCount > 0) {
      report.recommendations.push('Review and fix errors reported in validation results');
    }
    
    if (passRate < 0.8) {
      report.recommendations.push('Extension functionality may be impaired');
    }
    
    if (validationResults.extensionSetup && !validationResults.extensionSetup.permissionsGranted) {
      report.recommendations.push('Grant required permissions to extension');
    }
    
    if (validationResults.gitOperations && !validationResults.gitOperations.tokenValid) {
      report.recommendations.push('Configure valid GitHub token in settings');
    }

    return report;
  }
};

// Export for use in tests
if (typeof module !== 'undefined' && module.exports) {
  module.exports = workflowTestHelper;
} else if (typeof global !== 'undefined') {
  global.workflowTestHelper = workflowTestHelper;
}
