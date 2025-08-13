// Alternative Storage Strategies for PAT - Beyond localStorage and Extension Storage
// Exploring creative solutions for truly cross-domain PAT persistence

interface IStorageStrategy {
  name: string;
  description: string;
  availability: 'universal' | 'modern-browsers' | 'limited';
  security: 'high' | 'medium' | 'low';
  persistence: 'permanent' | 'session' | 'until-cleared';
  crossDomain: boolean;
  implementation: string;
}

interface IPATConfig {
  githubToken: string;
  githubRepo: string;
  defaultFolder: string;
}

// Strategy 1: Encode PAT directly in bookmarklet URL
class BookmarkletEmbeddedStorage {
  static createPersonalizedBookmarklet(config: IPATConfig): string {
    const encodedConfig = btoa(JSON.stringify(config));

    const bookmarkletCode = `
javascript:(function() {
  // Embedded configuration (base64 encoded)
  const EMBEDDED_CONFIG = '${encodedConfig}';
  
  function getEmbeddedConfig() {
    try {
      return JSON.parse(atob(EMBEDDED_CONFIG));
    } catch (error) {
      console.error('Failed to decode embedded config:', error);
      return null;
    }
  }
  
  // Load PrismWeave with pre-configured settings
  const script = document.createElement('script');
  script.src = 'https://your-domain.com/bookmarklet.js';
  script.onload = function() {
    window.PrismWeave.initialize(getEmbeddedConfig());
  };
  document.head.appendChild(script);
})();`;

    return bookmarkletCode;
  }

  static generatePersonalBookmarkletHTML(config: IPATConfig): string {
    const bookmarklet = this.createPersonalizedBookmarklet(config);

    return `
<!DOCTYPE html>
<html>
<head>
    <title>Your Personal PrismWeave Bookmarklet</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .bookmarklet { 
            background: #f0f8ff; 
            border: 2px dashed #007acc; 
            padding: 20px; 
            margin: 20px 0;
            border-radius: 8px;
        }
        .bookmarklet a {
            font-weight: bold;
            color: #007acc;
            text-decoration: none;
            padding: 10px 20px;
            background: #007acc;
            color: white;
            border-radius: 4px;
            display: inline-block;
        }
        .security-note {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <h1>🔖 Your Personal PrismWeave Bookmarklet</h1>
    
    <p>This bookmarklet has your GitHub PAT and repository pre-configured. 
    It will work on <strong>any website, any domain, any browser</strong> without requiring storage or extensions.</p>
    
    <div class="bookmarklet">
        <h3>📌 Drag this to your bookmarks bar:</h3>
        <a href="${bookmarklet}">📚 PrismWeave (Personal)</a>
    </div>
    
    <div class="security-note">
        <h4>🔒 Security Notes:</h4>
        <ul>
            <li><strong>Private:</strong> Keep this bookmarklet private - it contains your GitHub token</li>
            <li><strong>Secure:</strong> Token is base64 encoded (not encrypted, but obfuscated)</li>
            <li><strong>Revocable:</strong> You can revoke the GitHub token anytime in GitHub settings</li>
            <li><strong>Local:</strong> No external servers involved - runs entirely in your browser</li>
        </ul>
    </div>
    
    <h3>✅ Benefits of this approach:</h3>
    <ul>
        <li>Works on ANY domain without configuration</li>
        <li>No browser extension required</li>
        <li>No localStorage limitations</li>
        <li>No external services or privacy concerns</li>
        <li>One-time setup, universal functionality</li>
    </ul>
    
    <h3>⚠️ Trade-offs:</h3>
    <ul>
        <li>Token visible in bookmarklet (though encoded)</li>
        <li>Need new bookmarklet if token changes</li>
        <li>Bookmarklet URL becomes longer</li>
    </ul>
</body>
</html>`;
  }
}

// Strategy 2: File System Access API (Modern browsers)
class FileSystemStorage {
  private fileHandle: FileSystemFileHandle | null = null;

  async requestFileAccess(): Promise<boolean> {
    try {
      if ('showOpenFilePicker' in window) {
        const [fileHandle] = await (window as any).showOpenFilePicker({
          types: [
            {
              description: 'PrismWeave Config',
              accept: { 'application/json': ['.json'] },
            },
          ],
        });
        this.fileHandle = fileHandle;
        return true;
      }
    } catch (error) {
      console.warn('File system access not available or denied:', error);
    }
    return false;
  }

  async saveConfig(config: IPATConfig): Promise<boolean> {
    try {
      if (!this.fileHandle) {
        // Request save location
        this.fileHandle = await (window as any).showSaveFilePicker({
          suggestedName: 'prismweave-config.json',
          types: [
            {
              description: 'PrismWeave Config',
              accept: { 'application/json': ['.json'] },
            },
          ],
        });
      }

      // TypeScript null check: ensure fileHandle exists after potential assignment
      if (!this.fileHandle) {
        throw new Error('Failed to obtain file handle');
      }

      const writable = await this.fileHandle.createWritable();
      await writable.write(JSON.stringify(config, null, 2));
      await writable.close();

      return true;
    } catch (error) {
      console.error('Failed to save config to file:', error);
      return false;
    }
  }

  async loadConfig(): Promise<IPATConfig | null> {
    try {
      if (!this.fileHandle) {
        await this.requestFileAccess();
      }

      if (this.fileHandle) {
        const file = await this.fileHandle.getFile();
        const text = await file.text();
        return JSON.parse(text);
      }
    } catch (error) {
      console.error('Failed to load config from file:', error);
    }
    return null;
  }
}

// Strategy 3: Secure External Service (Optional)
class SecureCloudStorage {
  private readonly endpoint = 'https://api.prismweave.com/config'; // Hypothetical
  private userId: string | null = null;

  async authenticateUser(): Promise<string | null> {
    // Use GitHub OAuth to authenticate without storing PAT on server
    try {
      const response = await fetch(`${this.endpoint}/auth`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: 'github',
          returnUrl: window.location.href,
        }),
      });

      const { authUrl } = await response.json();

      // Open auth popup
      const popup = window.open(authUrl, 'auth', 'width=600,height=600');

      return new Promise(resolve => {
        const checkClosed = setInterval(() => {
          if (popup?.closed) {
            clearInterval(checkClosed);
            // Get user ID from URL fragment or postMessage
            const urlParams = new URLSearchParams(window.location.search);
            const userId = urlParams.get('userId');
            this.userId = userId;
            resolve(userId);
          }
        }, 1000);
      });
    } catch (error) {
      console.error('Authentication failed:', error);
      return null;
    }
  }

  async saveEncryptedConfig(config: IPATConfig): Promise<boolean> {
    if (!this.userId) {
      await this.authenticateUser();
    }

    try {
      // Encrypt config client-side before sending
      const encryptedConfig = await this.encryptConfig(config);

      const response = await fetch(`${this.endpoint}/users/${this.userId}/config`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ encryptedConfig }),
      });

      return response.ok;
    } catch (error) {
      console.error('Failed to save encrypted config:', error);
      return false;
    }
  }

  private async encryptConfig(config: IPATConfig): Promise<string> {
    // Use Web Crypto API for client-side encryption
    const key = await crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, true, [
      'encrypt',
      'decrypt',
    ]);

    const encoded = new TextEncoder().encode(JSON.stringify(config));
    const iv = crypto.getRandomValues(new Uint8Array(12));

    const encrypted = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, encoded);

    return btoa(String.fromCharCode(...new Uint8Array(encrypted)));
  }
}

// Strategy 4: Inter-Tab Communication (Same origin)
class TabSyncStorage {
  private channel: BroadcastChannel | null = null;

  constructor() {
    this.channel = new BroadcastChannel('prismweave-config');
    this.setupMessageListener();
  }

  private setupMessageListener(): void {
    this.channel?.addEventListener('message', event => {
      if (event.data.type === 'CONFIG_REQUEST') {
        // Another tab is requesting config
        const config = this.getLocalConfig();
        if (config) {
          this.channel?.postMessage({
            type: 'CONFIG_RESPONSE',
            config,
            tabId: event.data.tabId,
          });
        }
      }
    });
  }

  private getLocalConfig(): IPATConfig | null {
    try {
      const stored = localStorage.getItem('prismweave_bookmarklet_config');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  }

  async requestConfigFromOtherTabs(): Promise<IPATConfig | null> {
    return new Promise(resolve => {
      const tabId = Date.now().toString();
      let responded = false;

      const timeout = setTimeout(() => {
        if (!responded) {
          resolve(null);
        }
      }, 2000);

      const messageHandler = (event: MessageEvent) => {
        if (event.data.type === 'CONFIG_RESPONSE' && event.data.tabId === tabId) {
          responded = true;
          clearTimeout(timeout);
          this.channel?.removeEventListener('message', messageHandler);
          resolve(event.data.config);
        }
      };

      this.channel?.addEventListener('message', messageHandler);
      this.channel?.postMessage({ type: 'CONFIG_REQUEST', tabId });
    });
  }
}

// Comprehensive Storage Manager with multiple strategies
class UniversalStorageManager {
  private strategies: Array<{
    name: string;
    instance: any;
    priority: number;
    available: () => Promise<boolean>;
  }> = [];

  constructor() {
    this.initializeStrategies();
  }

  private initializeStrategies(): void {
    this.strategies = [
      {
        name: 'extension',
        instance: null, // Extension storage (already implemented)
        priority: 1,
        available: () => Promise.resolve(typeof chrome !== 'undefined' && !!chrome.runtime),
      },
      {
        name: 'embedded',
        instance: BookmarkletEmbeddedStorage,
        priority: 2,
        available: () => Promise.resolve(true), // Always available
      },
      {
        name: 'filesystem',
        instance: new FileSystemStorage(),
        priority: 3,
        available: () => Promise.resolve('showOpenFilePicker' in window),
      },
      {
        name: 'tabsync',
        instance: new TabSyncStorage(),
        priority: 4,
        available: () => Promise.resolve('BroadcastChannel' in window),
      },
      {
        name: 'localStorage',
        instance: null, // Already implemented
        priority: 5,
        available: () => Promise.resolve(typeof localStorage !== 'undefined'),
      },
    ];
  }

  async getAvailableStrategies(): Promise<Array<{ name: string; available: boolean }>> {
    const results = await Promise.all(
      this.strategies.map(async strategy => ({
        name: strategy.name,
        available: await strategy.available(),
      }))
    );

    return results;
  }

  async saveConfigWithBestStrategy(
    config: IPATConfig
  ): Promise<{ success: boolean; strategy: string }> {
    for (const strategy of this.strategies.sort((a, b) => a.priority - b.priority)) {
      if (await strategy.available()) {
        try {
          let success = false;

          switch (strategy.name) {
            case 'filesystem':
              success = await strategy.instance.saveConfig(config);
              break;
            case 'tabsync':
              // TabSync doesn't save, it just distributes
              localStorage.setItem('prismweave_bookmarklet_config', JSON.stringify(config));
              success = true;
              break;
            case 'embedded':
              // Generate personalized bookmarklet
              console.log('Generate your personal bookmarklet:');
              console.log(strategy.instance.createPersonalizedBookmarklet(config));
              success = true;
              break;
          }

          if (success) {
            return { success: true, strategy: strategy.name };
          }
        } catch (error) {
          console.warn(`Strategy ${strategy.name} failed:`, error);
          continue;
        }
      }
    }

    return { success: false, strategy: 'none' };
  }
}

// Export all strategies
export {
  BookmarkletEmbeddedStorage,
  FileSystemStorage,
  SecureCloudStorage,
  TabSyncStorage,
  UniversalStorageManager,
  type IPATConfig,
  type IStorageStrategy,
};

// Storage strategy comparison
export const STORAGE_STRATEGIES: IStorageStrategy[] = [
  {
    name: 'Extension Storage',
    description: 'Chrome extension chrome.storage.sync API',
    availability: 'limited',
    security: 'high',
    persistence: 'permanent',
    crossDomain: true,
    implementation: 'Already implemented',
  },
  {
    name: 'Embedded in Bookmarklet',
    description: 'Encode PAT directly in bookmarklet URL',
    availability: 'universal',
    security: 'medium',
    persistence: 'permanent',
    crossDomain: true,
    implementation: 'BookmarkletEmbeddedStorage',
  },
  {
    name: 'File System Access API',
    description: 'Save to local JSON file',
    availability: 'modern-browsers',
    security: 'high',
    persistence: 'permanent',
    crossDomain: true,
    implementation: 'FileSystemStorage',
  },
  {
    name: 'Tab Sync (BroadcastChannel)',
    description: 'Share between tabs on same origin',
    availability: 'modern-browsers',
    security: 'medium',
    persistence: 'session',
    crossDomain: false,
    implementation: 'TabSyncStorage',
  },
  {
    name: 'Secure Cloud Service',
    description: 'Encrypted storage on remote server',
    availability: 'universal',
    security: 'high',
    persistence: 'permanent',
    crossDomain: true,
    implementation: 'SecureCloudStorage',
  },
  {
    name: 'localStorage',
    description: 'Browser localStorage API',
    availability: 'universal',
    security: 'medium',
    persistence: 'permanent',
    crossDomain: false,
    implementation: 'Already implemented',
  },
];

// Usage example and demonstration
if (typeof window !== 'undefined') {
  console.log('🔧 Universal Storage Strategies Loaded');
  console.log(
    'Available strategies:',
    STORAGE_STRATEGIES.map(s => s.name)
  );

  // Expose for testing
  (window as any).PrismWeaveStorage = {
    BookmarkletEmbeddedStorage,
    FileSystemStorage,
    TabSyncStorage,
    UniversalStorageManager,
    STORAGE_STRATEGIES,
  };
}
