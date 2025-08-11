#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Ensure output directory exists
const outputDir = path.join(process.cwd(), 'dist', 'web');
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// Read package.json for version info
let version = '1.0.0';
try {
  const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
  version = pkg.version || version;
} catch (e) {
  console.log('No package.json found, using default version');
}

// Generate HTML
const html = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PrismWeave - Document Capture Tools</title>
    <meta name="description" content="Capture web pages as clean markdown and sync to your GitHub repository">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            line-height: 1.6; 
            color: #333; 
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 2rem; }
        .hero { 
            background: linear-gradient(135deg, #2563eb, #1d4ed8); 
            color: white; 
            text-align: center; 
            padding: 4rem 0; 
        }
        .hero h1 { font-size: 3rem; font-weight: 700; margin-bottom: 1rem; }
        .hero p { font-size: 1.25rem; opacity: 0.9; }
        .features { padding: 4rem 0; background: #f8fafc; }
        .features h2 { 
            text-align: center; 
            font-size: 2.5rem; 
            margin-bottom: 3rem; 
            color: #1e293b; 
        }
        .feature-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 2rem; 
        }
        .feature { 
            background: white; 
            padding: 2rem; 
            border-radius: 12px; 
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); 
            text-align: center; 
        }
        .feature-icon { font-size: 3rem; margin-bottom: 1rem; }
        .feature h3 { font-size: 1.5rem; margin-bottom: 1rem; color: #1e293b; }
        .components { padding: 4rem 0; }
        .components h2 { 
            text-align: center; 
            font-size: 2.5rem; 
            margin-bottom: 3rem; 
            color: #1e293b; 
        }
        .component { 
            background: white; 
            border: 2px solid #e2e8f0; 
            border-radius: 12px; 
            padding: 2rem; 
            margin: 2rem 0; 
        }
        .component h3 { font-size: 2rem; margin-bottom: 1rem; color: #2563eb; }
        .component p { font-size: 1.125rem; margin-bottom: 2rem; color: #64748b; }
        .btn-group { 
            display: flex; 
            gap: 1rem; 
            flex-wrap: wrap; 
            justify-content: center; 
        }
        .btn { 
            display: inline-flex; 
            align-items: center; 
            gap: 0.5rem; 
            padding: 0.75rem 1.5rem; 
            background: #2563eb; 
            color: white; 
            text-decoration: none; 
            border-radius: 8px; 
            font-weight: 600; 
            transition: background 0.2s; 
        }
        .btn:hover { background: #1d4ed8; }
        .btn-secondary { background: #64748b; }
        .btn-secondary:hover { background: #475569; }
        footer { 
            background: #1e293b; 
            color: white; 
            text-align: center; 
            padding: 3rem 0; 
        }
        footer a { color: #60a5fa; text-decoration: none; }
        footer a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="hero">
        <div class="container">
            <h1>🌟 PrismWeave</h1>
            <p>Capture web pages as clean markdown and sync to your document repository</p>
        </div>
    </div>
    
    <div class="features">
        <div class="container">
            <h2>Why PrismWeave?</h2>
            <div class="feature-grid">
                <div class="feature">
                    <div class="feature-icon">📝</div>
                    <h3>Clean Markdown</h3>
                    <p>Converts cluttered web pages into clean, readable markdown format</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">🔄</div>
                    <h3>GitHub Sync</h3>
                    <p>Automatically commits captured content to your GitHub repository</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">⚡</div>
                    <h3>Multiple Methods</h3>
                    <p>Choose between a full browser extension or lightweight bookmarklet</p>
                </div>
            </div>
        </div>
    </div>
    
    <div class="components">
        <div class="container">
            <h2>Choose Your Tool</h2>
            
            <div class="component">
                <h3>🧩 Browser Extension</h3>
                <p>Full-featured Chrome/Edge extension with keyboard shortcuts, advanced settings, and seamless integration.</p>
                <div class="btn-group">
                    <a href="https://github.com/davidhayesbc/PrismWeave/releases" class="btn">
                        📁 Download Extension
                    </a>
                    <a href="https://github.com/davidhayesbc/PrismWeave#installation" class="btn btn-secondary">
                        📖 Installation Guide
                    </a>
                </div>
            </div>
            
            <div class="component">
                <h3>🔖 Bookmarklet</h3>
                <p>Lightweight bookmarklet for quick page capture without installing an extension. Works in any browser.</p>
                <div style="background: #f1f5f9; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
                    <h4 style="margin-bottom: 1rem; color: #1e293b;">📌 Drag this link to your bookmarks bar:</h4>
                    <a href="javascript:(function(){if(window.prismweaveBookmarklet){return;}var s=document.createElement('script');s.src='https://davidhayesbc.github.io/PrismWeave/bookmarklet/loader.js';s.onload=function(){if(window.executeBookmarklet){window.executeBookmarklet();}};document.head.appendChild(s);window.prismweaveBookmarklet=true;})();" 
                       style="display: inline-block; padding: 12px 24px; background: #059669; color: white; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; cursor: move;">
                        🌟 PrismWeave Capture
                    </a>
                    <p style="margin-top: 1rem; font-size: 0.9rem; color: #64748b;">
                        Drag the green button above to your bookmarks bar, then click it on any webpage to capture content.
                    </p>
                </div>
                <div class="btn-group">
                    <a href="https://github.com/davidhayesbc/PrismWeave#usage" class="btn btn-secondary">
                        📖 Usage Instructions
                    </a>
                </div>
            </div>
        </div>
    </div>
    
    <footer>
        <div class="container">
            <p><strong>PrismWeave</strong> v${version} • Open Source Document Capture</p>
            <p><a href="https://github.com/davidhayesbc/PrismWeave">View Source on GitHub</a></p>
        </div>
    </footer>
</body>
</html>`;

// Write files
fs.writeFileSync(path.join(outputDir, 'index.html'), html);
fs.writeFileSync(path.join(outputDir, 'robots.txt'), 'User-agent: *\nDisallow:');
fs.writeFileSync(path.join(outputDir, '404.html'), 
  '<!DOCTYPE html><html><head><title>Page Not Found</title></head><body><h1>404 - Page Not Found</h1><p><a href="/">Return to PrismWeave Home</a></p></body></html>'
);

console.log('✅ Website files generated successfully');
console.log('Files created:');
console.log('- dist/web/index.html');
console.log('- dist/web/robots.txt');
console.log('- dist/web/404.html');
