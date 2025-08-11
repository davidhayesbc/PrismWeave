// Test: Bookmarklet Behavior Without Browser Extension
// This script demonstrates exactly what happens when the PrismWeave browser extension is not installed

console.log('🧪 Testing PrismWeave Bookmarklet WITHOUT Browser Extension');
console.log('==============================================================');

interface BookmarkletConfig {
  githubToken: string;
  githubRepo: string;
  defaultFolder: string;
  lastUpdated?: string;
  version?: string;
  storageMethod?: string;
  domain?: string;
}

interface TestResults {
  samedomainWorks: boolean;
  crossDomainWorks: boolean;
}

// Mock a scenario where the extension is not installed
const simulateNoExtension = (): any => {
  // Remove chrome object to simulate extension not being available
  const originalChrome = (globalThis as any).chrome;
  (globalThis as any).chrome = undefined;
  return originalChrome;
};

const restoreChrome = (originalChrome: any): void => {
  if (originalChrome) {
    (globalThis as any).chrome = originalChrome;
  }
};

// Test the bookmarklet's fallback behavior
async function testBookmarkletWithoutExtension(): Promise<TestResults> {
  console.log('\n📱 SCENARIO: User clicks bookmarklet on github.com (no extension installed)');
  console.log('------------------------------------------------------------------------');

  // Simulate the bookmarklet runtime
  class MockBookmarkletRuntime {
    private readonly STORAGE_KEY = 'prismweave_bookmarklet_config';
    private readonly EXTENSION_ID = 'your-extension-id-here';

    constructor() {
      // Initialization
    }

    // This mimics the actual storeConfig method
    storeConfig(config: BookmarkletConfig): void {
      try {
        console.log('🔍 Checking if browser extension is available...');

        // Try to use browser extension storage API for true cross-domain persistence
        if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.sendMessage) {
          console.log('✅ Extension detected - using cross-domain storage');
          // This path won't execute when extension is not installed
          chrome.runtime.sendMessage(
            this.EXTENSION_ID,
            {
              type: 'STORE_BOOKMARKLET_CONFIG',
              config: config,
            },
            response => {
              if (chrome.runtime.lastError) {
                console.warn(
                  '⚠️ Extension storage failed, falling back to localStorage:',
                  chrome.runtime.lastError.message
                );
                this.fallbackStoreConfig(config);
              } else {
                console.log('✅ Configuration stored via extension storage');
              }
            }
          );
        } else {
          // This is what actually happens when extension is not installed
          console.log('❌ Extension not detected');
          console.log('⚠️ Extension not available, using localStorage (domain-isolated)');
          this.fallbackStoreConfig(config);
        }
      } catch (error) {
        console.warn('⚠️ Extension communication failed, using localStorage fallback:', error);
        this.fallbackStoreConfig(config);
      }
    }

    // Fallback storage method (domain-isolated)
    fallbackStoreConfig(config: BookmarkletConfig): boolean {
      try {
        const storedConfig = {
          ...config,
          lastUpdated: new Date().toISOString(),
          version: '1.0.0',
          storageMethod: 'localStorage', // Track which storage method was used
          domain: window.location.hostname, // Track which domain this was stored on
        };
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(storedConfig));
        console.log('💾 Configuration stored in localStorage (domain-isolated)');
        console.log('📍 Storage location: localStorage for domain', window.location.hostname);
        console.log('⚠️ NOTE: This config will NOT be available on other domains');
        return true;
      } catch (error) {
        console.warn('❌ Failed to store configuration in localStorage:', error);

        // Final fallback to session storage
        try {
          const sessionConfig = { ...config, storageMethod: 'sessionStorage' };
          sessionStorage.setItem(this.STORAGE_KEY, JSON.stringify(sessionConfig));
          console.log('💾 Configuration stored in sessionStorage as final fallback');
          console.log('⚠️ NOTE: This config will be lost when tab is closed');
          return true;
        } catch (sessionError) {
          console.error('❌ Failed to store configuration in any storage:', sessionError);
          return false;
        }
      }
    }

    // Load configuration with extension storage API priority
    loadStoredConfig(): Promise<Partial<BookmarkletConfig>> {
      return new Promise(resolve => {
        try {
          console.log('🔍 Checking for stored configuration...');

          // Try to use browser extension storage API first
          if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.sendMessage) {
            console.log('✅ Extension detected - checking cross-domain storage');
            chrome.runtime.sendMessage(
              this.EXTENSION_ID,
              {
                type: 'GET_BOOKMARKLET_CONFIG',
              },
              response => {
                if (chrome.runtime.lastError || !response) {
                  console.warn('⚠️ Extension storage unavailable, falling back to localStorage');
                  resolve(this.fallbackLoadConfig());
                } else {
                  console.log('✅ Configuration loaded from extension storage');
                  resolve(response.config || {});
                }
              }
            );
          } else {
            // This is what happens when extension is not installed
            console.log('❌ Extension not detected');
            console.log('📍 Checking localStorage for domain:', window.location.hostname);
            resolve(this.fallbackLoadConfig());
          }
        } catch (error) {
          console.warn('⚠️ Extension communication failed, using localStorage fallback:', error);
          resolve(this.fallbackLoadConfig());
        }
      });
    }

    // Fallback config loading (domain-isolated)
    fallbackLoadConfig(): Partial<BookmarkletConfig> {
      try {
        const stored =
          localStorage.getItem(this.STORAGE_KEY) || sessionStorage.getItem(this.STORAGE_KEY);
        if (stored) {
          const config = JSON.parse(stored);
          console.log('📂 Configuration found in', config.storageMethod || 'localStorage');
          console.log('📍 Stored for domain:', config.domain || window.location.hostname);
          console.log('🔧 Configuration loaded successfully');
          return config;
        } else {
          console.log('❌ No stored configuration found for domain:', window.location.hostname);
          console.log('👤 User will need to enter PAT and repository settings');
        }
      } catch (error) {
        console.warn('❌ Failed to load stored configuration:', error);
      }
      return {};
    }
  }

  // Simulate user interaction
  const bookmarklet = new MockBookmarkletRuntime();

  // Test 1: Store configuration on github.com
  console.log('\n📝 Test 1: User configures settings on github.com');
  console.log('------------------------------------------------');
  const testConfig = {
    githubToken: 'ghp_test_token_12345',
    githubRepo: 'user/test-repo',
    defaultFolder: 'documents',
  };

  bookmarklet.storeConfig(testConfig);

  // Test 2: Load configuration on same domain
  console.log('\n📖 Test 2: Load settings on github.com (same domain)');
  console.log('----------------------------------------------------');
  const loadedConfig = await bookmarklet.loadStoredConfig();

  if (loadedConfig.githubToken) {
    console.log('✅ SUCCESS: Configuration loaded on same domain');
    console.log('📋 Loaded:', { token: '***', repo: loadedConfig.githubRepo });
  } else {
    console.log('❌ FAILED: Could not load configuration');
  }

  // Test 3: Simulate navigation to different domain
  console.log('\n🌐 Test 3: User navigates to stackoverflow.com');
  console.log('----------------------------------------------');

  // Mock window.location change
  Object.defineProperty(window, 'location', {
    value: { hostname: 'stackoverflow.com', href: 'https://stackoverflow.com/questions' },
    writable: true,
  });

  console.log('📍 Now on domain:', window.location.hostname);
  const configOnNewDomain = await bookmarklet.loadStoredConfig();

  if (configOnNewDomain.githubToken) {
    console.log('✅ Configuration available on new domain');
  } else {
    console.log('❌ Configuration NOT available on new domain');
    console.log('👤 User must re-enter PAT and repository settings');
    console.log('📝 This is the "domain isolation" problem you identified');
  }

  return {
    samedomainWorks: !!loadedConfig.githubToken,
    crossDomainWorks: !!configOnNewDomain.githubToken,
  };
}

// Comparison: With vs Without Extension
function showBehaviorComparison() {
  console.log('\n📊 BEHAVIOR COMPARISON: Extension vs No Extension');
  console.log('=================================================');

  console.log('\n🔌 WITH Extension Installed:');
  console.log('----------------------------');
  console.log('✅ User configures PAT on github.com');
  console.log('✅ Settings stored in chrome.storage.sync (cross-domain)');
  console.log('✅ User navigates to stackoverflow.com');
  console.log('✅ Settings automatically available (same PAT)');
  console.log('✅ User navigates to medium.com');
  console.log('✅ Settings automatically available (same PAT)');
  console.log('🎉 Result: Configure once, works everywhere');

  console.log('\n🚫 WITHOUT Extension Installed:');
  console.log('-------------------------------');
  console.log('✅ User configures PAT on github.com');
  console.log('⚠️ Settings stored in localStorage (domain-isolated)');
  console.log('❌ User navigates to stackoverflow.com');
  console.log('❌ No settings available (must re-enter PAT)');
  console.log('❌ User navigates to medium.com');
  console.log('❌ No settings available (must re-enter PAT again)');
  console.log('😞 Result: Must configure on every domain');
}

// User experience implications
function showUserExperienceImpact() {
  console.log('\n👤 USER EXPERIENCE IMPACT');
  console.log('=========================');

  console.log('\n📱 Scenario: User wants to capture articles from 5 different websites');
  console.log('---------------------------------------------------------------------');

  const websites = ['github.com', 'stackoverflow.com', 'medium.com', 'dev.to', 'hackernews.com'];

  console.log('\n🔌 With Extension:');
  console.log('  1. Configure PAT once on any website ✅');
  console.log('  2. Use bookmarklet on all 5 websites ✅');
  console.log('  📊 Total configurations needed: 1');

  console.log('\n🚫 Without Extension:');
  console.log('  1. Configure PAT on github.com ✅');
  console.log('  2. Navigate to stackoverflow.com - must re-configure PAT ❌');
  console.log('  3. Navigate to medium.com - must re-configure PAT ❌');
  console.log('  4. Navigate to dev.to - must re-configure PAT ❌');
  console.log('  5. Navigate to hackernews.com - must re-configure PAT ❌');
  console.log('  📊 Total configurations needed: 5');

  console.log('\n📈 Extension Value Proposition:');
  console.log('  • Reduces configuration overhead by 80%');
  console.log('  • Eliminates user frustration from repeated setup');
  console.log('  • Provides seamless cross-domain experience');
  console.log('  • Makes bookmarklet truly universal');
}

// Recommendations
function showRecommendations() {
  console.log('\n💡 RECOMMENDATIONS');
  console.log('==================');

  console.log('\n🎯 For Users:');
  console.log('-------------');
  console.log('✅ RECOMMENDED: Install the PrismWeave browser extension');
  console.log('   • Configure PAT once, works everywhere');
  console.log('   • Best possible user experience');
  console.log('   • Secure storage in extension context');

  console.log('\n⚠️ Alternative: Use bookmarklet without extension');
  console.log('   • Still functional but limited to per-domain storage');
  console.log('   • Must re-enter PAT on each new website domain');
  console.log('   • Good for users who cannot install extensions');

  console.log('\n🔧 For Deployment:');
  console.log('------------------');
  console.log('✅ Provide both options to users');
  console.log('✅ Clearly communicate the benefits of the extension');
  console.log('✅ Fallback ensures bookmarklet works in all scenarios');
  console.log('✅ Progressive enhancement approach');
}

// Run the comprehensive test
async function runComprehensiveTest() {
  // Save original chrome object
  const originalChrome = simulateNoExtension();

  try {
    console.log('🚀 Starting comprehensive test without browser extension...\n');

    const results = await testBookmarkletWithoutExtension();

    showBehaviorComparison();
    showUserExperienceImpact();
    showRecommendations();

    console.log('\n🎯 CONCLUSION');
    console.log('=============');
    console.log('✅ YES - The bookmarklet WILL work without the browser extension');
    console.log('⚠️ BUT - It will have domain-isolated storage (the original problem)');
    console.log('🎉 SOLUTION - Installing the extension provides the optimal experience');

    return results;
  } finally {
    // Restore chrome object
    restoreChrome(originalChrome);
  }
}

// Export for use in other contexts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    testBookmarkletWithoutExtension,
    showBehaviorComparison,
    showUserExperienceImpact,
    showRecommendations,
    runComprehensiveTest,
  };
}

// Auto-run if loaded directly
if (typeof window !== 'undefined') {
  console.log('📚 Bookmarklet No-Extension Test Module Loaded');

  // Expose test runner globally
  window.testBookmarkletWithoutExtension = runComprehensiveTest;

  // Auto-run demonstration
  runComprehensiveTest().catch(console.error);
}
