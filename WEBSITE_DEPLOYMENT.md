# PrismWeave Website Deployment

This document explains how to deploy and maintain the PrismWeave website using GitHub Actions and GitHub Pages.

## 🌐 Website Overview

The PrismWeave website provides:
- **Browser Extension Downloads** - Pre-built extension files for Chrome/Edge
- **Bookmarklet Access** - Lightweight alternative for any browser
- **Installation Guides** - Step-by-step setup instructions
- **Configuration Help** - GitHub integration setup

## 🚀 Automated Deployment

### GitHub Actions Workflow

The website deploys automatically using GitHub Actions with these triggers:
- **Push to main branch** - Immediate deployment of changes
- **Pull requests** - Build testing without deployment
- **Manual trigger** - Deploy on-demand via GitHub web interface

### Deployment Process

1. **Build Phase**
   ```bash
   # Install dependencies
   npm install
   
   # Build all components
   node build.js all
   
   # Generate web deployment
   node build.js web
   ```

2. **Test Phase**
   ```bash
   # Run extension tests
   npm test
   
   # Validate build outputs
   ls -la dist/web/
   ```

3. **Deploy Phase**
   - Upload build artifacts to GitHub Pages
   - Configure custom domain (if specified)
   - Update DNS settings automatically

## 📁 Directory Structure

```
dist/web/                    # Web deployment root
├── index.html              # Main landing page
├── extension/              # Browser extension files
│   ├── manifest.json       # Extension manifest
│   ├── icons/              # Extension icons
│   ├── background/         # Service worker
│   ├── content/            # Content scripts
│   ├── popup/              # Extension popup
│   └── options/            # Settings pages
└── bookmarklet/            # Bookmarklet files
    ├── index.html          # Bookmarklet setup page
    ├── help.html           # Usage instructions
    └── runtime.js          # Bookmarklet code
```

## ⚙️ Configuration

### GitHub Pages Setup

1. **Enable GitHub Pages**
   - Go to repository Settings → Pages
   - Source: "GitHub Actions"
   - Save the configuration

2. **Custom Domain (Optional)**
   ```yaml
   # In .github/workflows/deploy-website.yml
   env:
     CUSTOM_DOMAIN: 'your-domain.com'  # Uncomment and set your domain
   ```

### Environment Variables

The workflow supports these configuration options:

| Variable | Description | Default |
|----------|-------------|---------|
| `CUSTOM_DOMAIN` | Custom domain name | None (uses GitHub Pages URL) |
| `NODE_VERSION` | Node.js version | 18 |
| `DEPLOY_BRANCH` | Deployment branch | gh-pages |

## 🔧 Manual Deployment

For manual deployment or testing:

```bash
# 1. Build the website
node build.js web

# 2. Test locally (optional)
cd dist/web
python -m http.server 8000
# Visit http://localhost:8000

# 3. Deploy to GitHub Pages
# Commit and push the workflow file to trigger deployment
git add .github/workflows/deploy-website.yml
git commit -m "Add website deployment workflow"
git push origin main
```

## 🌍 Hosting Recommendations

### GitHub Pages (Recommended)
- **Cost**: Free for public repositories
- **Features**: Custom domains, HTTPS, global CDN
- **Integration**: Native GitHub Actions support
- **Limits**: 1GB storage, 100GB bandwidth/month

### Alternative Hosting Options

1. **Netlify**
   - Free tier: 100GB bandwidth/month
   - Automatic deployments from Git
   - Form handling and serverless functions
   - Easy custom domain setup

2. **Vercel**
   - Free tier: 100GB bandwidth/month
   - Excellent performance optimization
   - Automatic HTTPS and global CDN
   - Built-in analytics

3. **Cloudflare Pages**
   - Unlimited bandwidth (free tier)
   - Excellent global performance
   - Direct Git integration
   - Built-in security features

## 📈 Monitoring & Analytics

### GitHub Pages Analytics
Access deployment stats at:
- Repository → Actions → Deploy Website workflow
- Repository → Settings → Pages → View deployment history

### Optional Analytics Integration
Add to `index.html` if desired:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_TRACKING_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_TRACKING_ID');
</script>
```

## 🛠️ Maintenance

### Updating the Website

1. **Content Updates**
   - Edit files in `/browser-extension/src/`
   - Update `build.js` for layout changes
   - Modify styles in the `generateWebIndex()` function

2. **Extension Updates**
   - Update extension code as normal
   - Run `node build.js web` to rebuild
   - Commit changes to trigger deployment

3. **Workflow Updates**
   - Edit `.github/workflows/deploy-website.yml`
   - Test changes with pull requests
   - Monitor Actions tab for deployment status

### Security Considerations

- **GitHub Token Permissions**: The workflow uses `GITHUB_TOKEN` with minimal required permissions
- **Content Security**: No user data is processed during deployment
- **Dependencies**: Regularly update Node.js dependencies for security
- **Access Control**: Use branch protection rules to control deployments

## 🚨 Troubleshooting

### Common Issues

1. **Deployment Fails**
   ```bash
   # Check workflow logs in GitHub Actions
   # Common causes: Build errors, permission issues, quota limits
   ```

2. **Website Not Updating**
   ```bash
   # Clear browser cache
   # Check GitHub Pages deployment status
   # Verify workflow completed successfully
   ```

3. **Custom Domain Issues**
   ```bash
   # Verify DNS CNAME record points to: username.github.io
   # Check domain configuration in repository settings
   # Allow 24-48 hours for DNS propagation
   ```

### Getting Help

- **GitHub Actions Issues**: Check repository Actions tab for error logs
- **GitHub Pages Issues**: GitHub Pages troubleshooting documentation
- **Build Issues**: Verify local build works with `node build.js web`
- **Extension Issues**: Test extension functionality before deployment

## 📊 Performance Optimization

The deployed website includes:
- **Minified CSS** - Reduced file sizes
- **Optimized Images** - Compressed extension icons
- **CDN Delivery** - GitHub Pages global CDN
- **Caching Headers** - Browser caching optimization
- **Mobile Responsive** - Optimized for all devices

## 📝 License & Credits

- **PrismWeave**: Open source document capture system
- **GitHub Pages**: Free static site hosting
- **GitHub Actions**: Automated deployment pipeline
- **Modern CSS**: Responsive design with CSS Grid and Flexbox
