// Embedded Bookmarklet Generator - Store PAT directly in bookmarklet URL
// This solves the cross-domain storage problem by eliminating the need for storage

interface IPATConfiguration {
  githubToken: string;
  githubRepo: string;
  defaultFolder?: string;
  commitMessage?: string;
}

class EmbeddedBookmarkletGenerator {
  /**
   * Creates a personalized bookmarklet with PAT embedded in the code
   * This bookmarklet will work on ANY domain without requiring any storage
   */
  static generatePersonalBookmarklet(config: IPATConfiguration): string {
    // Encode configuration to base64 (obfuscation, not encryption)
    const configString = JSON.stringify({
      githubToken: config.githubToken,
      githubRepo: config.githubRepo,
      defaultFolder: config.defaultFolder || 'documents',
      commitMessage: config.commitMessage || 'Add document via PrismWeave',
      generatedAt: new Date().toISOString(),
      version: '1.0.0',
    });

    const encodedConfig = btoa(configString);

    // Minified bookmarklet code with embedded configuration
    const bookmarkletCode = `javascript:(function(){
const cfg=JSON.parse(atob('${encodedConfig}'));
const s=document.createElement('script');
s.onload=()=>window.PrismWeave?.init(cfg);
s.onerror=()=>{
  const h='<div style="position:fixed;top:20px;right:20px;background:#333;color:white;padding:20px;border-radius:8px;z-index:9999;font-family:Arial;max-width:300px"><h3>🔖 PrismWeave</h3><p>Capturing page content...</p><div id="pw-status">Initializing...</div></div>';
  document.body.insertAdjacentHTML('beforeend',h);
  const st=document.getElementById('pw-status');
  st.innerText='Extracting content...';
  const t=document.title||'Untitled';
  const u=window.location.href;
  const c=document.querySelector('article,main,[role="main"],.content,#content')||document.body;
  const md='# '+t+'\\n\\n'+Array.from(c.querySelectorAll('p,h1,h2,h3,h4,h5,h6')).map(e=>e.innerText.trim()).filter(t=>t.length>0).join('\\n\\n');
  const fn=t.replace(/[^a-zA-Z0-9]/g,'-').toLowerCase().substring(0,50)+'.md';
  const fp=cfg.defaultFolder+'/'+fn;
  st.innerText='Committing to GitHub...';
  fetch('https://api.github.com/repos/'+cfg.githubRepo+'/contents/'+fp,{
    method:'PUT',
    headers:{'Authorization':'token '+cfg.githubToken,'Content-Type':'application/json'},
    body:JSON.stringify({message:cfg.commitMessage+' - '+t,content:btoa(unescape(encodeURIComponent('---\\ntitle: '+t+'\\nurl: '+u+'\\ncaptured: '+new Date().toISOString()+'\\n---\\n\\n'+md)))})
  }).then(r=>r.ok?st.innerText='✅ Saved successfully!':st.innerText='❌ Failed: '+r.status).catch(e=>st.innerText='❌ Error: '+e.message);
};
s.src='https://cdn.jsdelivr.net/npm/turndown@7.1.1/dist/turndown.js';
document.head.appendChild(s);
})();`;

    return bookmarkletCode;
  }

  /**
   * Generates a complete HTML page with the personalized bookmarklet
   * Users can save this page and drag the bookmarklet to their bookmark bar
   */
  static generateBookmarkletPage(config: IPATConfiguration): string {
    const bookmarklet = this.generatePersonalBookmarklet(config);
    const bookmarkletDisplay =
      bookmarklet.length > 200 ? bookmarklet.substring(0, 200) + '...[truncated]' : bookmarklet;

    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Personal PrismWeave Bookmarklet</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .bookmarklet-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin: 20px 0;
        }
        .bookmarklet-link {
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            text-decoration: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-weight: bold;
            border: 2px solid rgba(255, 255, 255, 0.3);
            transition: all 0.3s ease;
        }
        .bookmarklet-link:hover {
            background: rgba(255, 255, 255, 0.3);
            border-color: rgba(255, 255, 255, 0.5);
        }
        .instructions {
            background: #e3f2fd;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #2196f3;
        }
        .security-warning {
            background: #fff3e0;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #ff9800;
            margin: 20px 0;
        }
        .feature-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .feature-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #4caf50;
        }
        .config-details {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 14px;
            word-break: break-all;
        }
        .step {
            margin: 15px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #2196f3;
        }
        .step-number {
            background: #2196f3;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔖 Your Personal PrismWeave Bookmarklet</h1>
        
        <p><strong>Congratulations!</strong> Your bookmarklet has been generated with your GitHub PAT pre-configured. 
        This bookmarklet will work on <strong>any website, any domain, any browser</strong> without requiring 
        storage, extensions, or additional setup.</p>
        
        <div class="bookmarklet-container">
            <h3>📌 Drag this bookmark to your bookmarks bar:</h3>
            <a href="${bookmarklet}" class="bookmarklet-link">
                🚀 PrismWeave (Personal)
            </a>
            <p style="margin-top: 15px; font-size: 14px; opacity: 0.9;">
                Right-click and "Add to Bookmarks" or drag to your bookmarks bar
            </p>
        </div>
        
        <div class="instructions">
            <h3>📋 How to Use:</h3>
            <div class="step">
                <span class="step-number">1</span>
                <strong>Install:</strong> Drag the bookmark above to your browser's bookmarks bar
            </div>
            <div class="step">
                <span class="step-number">2</span>
                <strong>Navigate:</strong> Go to any webpage you want to capture (article, blog post, etc.)
            </div>
            <div class="step">
                <span class="step-number">3</span>
                <strong>Capture:</strong> Click the "PrismWeave (Personal)" bookmark
            </div>
            <div class="step">
                <span class="step-number">4</span>
                <strong>Done:</strong> Content automatically saved to your GitHub repository!
            </div>
        </div>
        
        <div class="feature-list">
            <div class="feature-item">
                <h4>✅ Universal Compatibility</h4>
                <p>Works on any website domain without configuration</p>
            </div>
            <div class="feature-item">
                <h4>🔒 No External Storage</h4>
                <p>No localStorage, no extension required</p>
            </div>
            <div class="feature-item">
                <h4>⚡ One-Click Operation</h4>
                <p>Instant content capture and GitHub commit</p>
            </div>
            <div class="feature-item">
                <h4>📱 Cross-Device</h4>
                <p>Same bookmarklet works on all your devices</p>
            </div>
        </div>
        
        <div class="security-warning">
            <h4>🔒 Security & Privacy Notes:</h4>
            <ul>
                <li><strong>Private:</strong> Keep this bookmarklet private - it contains your GitHub token</li>
                <li><strong>Encoded:</strong> Your token is base64 encoded (obfuscated but not encrypted)</li>
                <li><strong>Revocable:</strong> You can revoke/regenerate the GitHub token anytime</li>
                <li><strong>Local:</strong> No external servers - runs entirely in your browser</li>
                <li><strong>Open Source:</strong> You can inspect the bookmarklet code anytime</li>
            </ul>
        </div>
        
        <details style="margin: 20px 0;">
            <summary style="cursor: pointer; font-weight: bold;">🔍 Configuration Details</summary>
            <div class="config-details">
                <strong>Repository:</strong> ${config.githubRepo}<br>
                <strong>Default Folder:</strong> ${config.defaultFolder || 'documents'}<br>
                <strong>Commit Message:</strong> ${config.commitMessage || 'Add document via PrismWeave'}<br>
                <strong>Token (first 10 chars):</strong> ${config.githubToken.substring(0, 10)}...<br>
                <strong>Generated:</strong> ${new Date().toISOString()}
            </div>
        </details>
        
        <details style="margin: 20px 0;">
            <summary style="cursor: pointer; font-weight: bold;">📝 Bookmarklet Code Preview</summary>
            <div class="config-details" style="font-size: 12px;">
                ${bookmarkletDisplay}
            </div>
        </details>
        
        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
            <p style="color: #666;">
                Generated by PrismWeave • 
                <a href="https://github.com/davidhayesbc/PrismWeave">View on GitHub</a>
            </p>
        </div>
    </div>
    
    <script>
        // Add some interactivity
        document.addEventListener('DOMContentLoaded', function() {
            const bookmarkletLink = document.querySelector('.bookmarklet-link');
            
            // Show instruction when user tries to click
            bookmarkletLink.addEventListener('click', function(e) {
                if (e.ctrlKey || e.metaKey) {
                    // Allow normal bookmark save behavior
                    return true;
                }
                
                e.preventDefault();
                
                // Show helpful message
                const message = document.createElement('div');
                message.style.cssText = \`
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    background: #333;
                    color: white;
                    padding: 20px;
                    border-radius: 8px;
                    z-index: 10000;
                    text-align: center;
                    font-family: Arial, sans-serif;
                \`;
                message.innerHTML = \`
                    <h3>📌 How to Install Bookmarklet</h3>
                    <p>Right-click the bookmark and select "Add to Bookmarks"<br>
                    or drag it to your bookmarks bar</p>
                    <button onclick="this.parentElement.remove()" style="margin-top: 10px; padding: 8px 16px; cursor: pointer;">Got it!</button>
                \`;
                document.body.appendChild(message);
                
                // Auto-remove after 5 seconds
                setTimeout(() => {
                    if (message.parentElement) {
                        message.remove();
                    }
                }, 5000);
            });
        });
    </script>
</body>
</html>`;
  }

  /**
   * Validates the configuration before generating bookmarklet
   */
  static validateConfiguration(config: IPATConfiguration): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!config.githubToken) {
      errors.push('GitHub token is required');
    } else if (
      !config.githubToken.startsWith('ghp_') &&
      !config.githubToken.startsWith('github_pat_')
    ) {
      errors.push('GitHub token format appears invalid');
    }

    if (!config.githubRepo) {
      errors.push('GitHub repository is required');
    } else if (!/^[\w\-\.]+\/[\w\-\.]+$/.test(config.githubRepo)) {
      errors.push('GitHub repository must be in format: owner/repo');
    }

    if (config.defaultFolder && config.defaultFolder.includes('..')) {
      errors.push('Default folder cannot contain ".." path segments');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  /**
   * Extracts configuration from an existing bookmarklet
   */
  static extractConfigFromBookmarklet(bookmarkletCode: string): IPATConfiguration | null {
    try {
      // Look for the base64 encoded configuration
      const match = bookmarkletCode.match(/atob\(['"]([A-Za-z0-9+/=]+)['"]\)/);
      if (match && match[1]) {
        const decoded = atob(match[1]);
        const config = JSON.parse(decoded);
        return config;
      }
    } catch (error) {
      console.error('Failed to extract config from bookmarklet:', error);
    }
    return null;
  }

  /**
   * Generates a setup form for collecting PAT and repository info
   */
  static generateSetupForm(): string {
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PrismWeave Bookmarklet Generator</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
            box-sizing: border-box;
        }
        button {
            background: #007acc;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
        }
        button:hover {
            background: #005fa3;
        }
        .help-text {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔖 Generate Your Personal PrismWeave Bookmarklet</h1>
        
        <form id="bookmarkletForm">
            <div class="form-group">
                <label for="githubToken">GitHub Personal Access Token *</label>
                <input type="password" id="githubToken" required 
                       placeholder="ghp_your_token_here">
                <div class="help-text">
                    Create a PAT at <a href="https://github.com/settings/tokens" target="_blank">GitHub Settings > Developer settings > Personal access tokens</a>
                </div>
            </div>
            
            <div class="form-group">
                <label for="githubRepo">GitHub Repository *</label>
                <input type="text" id="githubRepo" required 
                       placeholder="username/repository-name">
                <div class="help-text">
                    Format: owner/repository (e.g., john/my-documents)
                </div>
            </div>
            
            <div class="form-group">
                <label for="defaultFolder">Default Folder</label>
                <input type="text" id="defaultFolder" 
                       placeholder="documents" value="documents">
                <div class="help-text">
                    Folder where captured documents will be stored
                </div>
            </div>
            
            <div class="form-group">
                <label for="commitMessage">Commit Message Template</label>
                <input type="text" id="commitMessage" 
                       placeholder="Add document via PrismWeave" value="Add document via PrismWeave">
                <div class="help-text">
                    Template for commit messages (page title will be appended)
                </div>
            </div>
            
            <button type="submit">🚀 Generate My Personal Bookmarklet</button>
        </form>
    </div>
    
    <script>
        document.getElementById('bookmarkletForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const config = {
                githubToken: document.getElementById('githubToken').value,
                githubRepo: document.getElementById('githubRepo').value,
                defaultFolder: document.getElementById('defaultFolder').value || 'documents',
                commitMessage: document.getElementById('commitMessage').value || 'Add document via PrismWeave'
            };
            
            // Basic validation
            if (!config.githubToken || !config.githubRepo) {
                alert('Please fill in required fields');
                return;
            }
            
            // Generate bookmarklet page
            const bookmarkletPage = generateBookmarkletPage(config);
            
            // Open in new window
            const newWindow = window.open('', '_blank');
            newWindow.document.write(bookmarkletPage);
            newWindow.document.close();
        });
        
        // Include the bookmarklet generator functions
        ${this.generatePersonalBookmarklet.toString()}
        ${this.generateBookmarkletPage.toString()}
    </script>
</body>
</html>`;
  }
}

// Export the generator
export default EmbeddedBookmarkletGenerator;
export { EmbeddedBookmarkletGenerator, type IPATConfiguration };

// Example usage
if (typeof window !== 'undefined') {
  // Expose for browser usage
  (window as any).EmbeddedBookmarkletGenerator = EmbeddedBookmarkletGenerator;

  console.log('🔖 Embedded Bookmarklet Generator loaded');
  console.log('Usage: EmbeddedBookmarkletGenerator.generatePersonalBookmarklet(config)');
}
