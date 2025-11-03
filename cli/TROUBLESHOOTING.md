# PrismWeave CLI - Troubleshooting Guide

Common issues and their solutions.

## Installation Issues

### "npm install" fails

**Symptom**: Dependencies fail to install

**Solutions**:

```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and try again
rm -rf node_modules package-lock.json
npm install

# Use a different registry (if behind firewall)
npm install --registry https://registry.npmjs.org/
```

### "npm run build" fails

**Symptom**: TypeScript compilation errors

**Solutions**:

```bash
# Ensure TypeScript is installed
npm install -g typescript

# Check Node.js version (needs 18+)
node --version

# Rebuild from scratch
npm run clean
npm run build
```

### "npm link" permission denied

**Symptom**: Permission errors on Unix/Linux/Mac

**Solution**:

```bash
# Option 1: Use sudo (not recommended)
sudo npm link

# Option 2: Fix npm permissions (recommended)
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
npm link
```

## Configuration Issues

### "GitHub token and repository are required"

**Symptom**: Trying to capture without configuration

**Solution**:

```bash
# Set required configuration
prismweave config --set githubToken=ghp_your_token_here
prismweave config --set githubRepo=owner/repo

# Verify configuration
prismweave config --list

# Test connection
prismweave config --test
```

### "Invalid repository path format"

**Symptom**: Repository format not recognized

**Problem**: Repository must be in `owner/repo` format

**Solutions**:

```bash
# ❌ Wrong formats
prismweave config --set githubRepo=https://github.com/owner/repo
prismweave config --set githubRepo=https://github.com/owner/repo.git
prismweave config --set githubRepo=github.com/owner/repo

# ✅ Correct format
prismweave config --set githubRepo=owner/repo
```

### Configuration not persisting

**Symptom**: Settings reset after restart

**Problem**: Config file permissions or path issue

**Solutions**:

```bash
# Check config location
# Windows: C:\Users\<username>\.prismweave\config.json
# Mac/Linux: ~/.prismweave/config.json

# Check if directory exists
ls -la ~/.prismweave  # Mac/Linux
dir %USERPROFILE%\.prismweave  # Windows

# Manually create if needed
mkdir ~/.prismweave
echo '{}' > ~/.prismweave/config.json
```

## Browser/Puppeteer Issues

### "Failed to launch browser"

**Symptom**: Puppeteer can't start Chromium

**Solutions**:

```bash
# Solution 1: Install Chromium manually
npx puppeteer browsers install chrome

# Solution 2: Set executable path
export PUPPETEER_EXECUTABLE_PATH=/path/to/chrome

# Solution 3: Skip download and use system Chrome
npm install --ignore-scripts
```

### Browser launch fails on Linux

**Symptom**: Missing dependencies on Linux

**Solution**:

```bash
# Ubuntu/Debian
sudo apt-get install -y \
  ca-certificates \
  fonts-liberation \
  libappindicator3-1 \
  libasound2 \
  libatk-bridge2.0-0 \
  libatk1.0-0 \
  libc6 \
  libcairo2 \
  libcups2 \
  libdbus-1-3 \
  libexpat1 \
  libfontconfig1 \
  libgbm1 \
  libgcc1 \
  libglib2.0-0 \
  libgtk-3-0 \
  libnspr4 \
  libnss3 \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libstdc++6 \
  libx11-6 \
  libx11-xcb1 \
  libxcb1 \
  libxcomposite1 \
  libxcursor1 \
  libxdamage1 \
  libxext6 \
  libxfixes3 \
  libxi6 \
  libxrandr2 \
  libxrender1 \
  libxss1 \
  libxtst6 \
  lsb-release \
  wget \
  xdg-utils

# CentOS/RHEL
sudo yum install -y \
  alsa-lib.x86_64 \
  atk.x86_64 \
  cups-libs.x86_64 \
  gtk3.x86_64 \
  libXcomposite.x86_64 \
  libXcursor.x86_64 \
  libXdamage.x86_64 \
  libXext.x86_64 \
  libXi.x86_64 \
  libXrandr.x86_64 \
  libXScrnSaver.x86_64 \
  libXtst.x86_64 \
  pango.x86_64 \
  xorg-x11-fonts-100dpi \
  xorg-x11-fonts-75dpi \
  xorg-x11-fonts-cyrillic \
  xorg-x11-fonts-misc \
  xorg-x11-fonts-Type1 \
  xorg-x11-utils
```

### Browser timeout

**Symptom**: "Navigation timeout" errors

**Solutions**:

```bash
# Increase timeout for slow sites
prismweave capture https://slow-site.com --timeout 60000

# Or set default timeout in config
prismweave config --set timeout=60000
```

## GitHub API Issues

### "GitHub API error: 401"

**Symptom**: Authentication failed

**Solutions**:

1. Check token is valid: Visit https://github.com/settings/tokens
2. Token has correct scopes:
   - Private repos: `repo` scope
   - Public repos: `public_repo` scope
3. Regenerate token if expired
4. Update config with new token

### "GitHub API error: 404"

**Symptom**: Repository not found

**Solutions**:

```bash
# Verify repository exists
# Go to: https://github.com/owner/repo

# Check repository format
prismweave config --get githubRepo
# Should be: owner/repo

# Test connection
prismweave config --test
```

### "GitHub API error: 403"

**Symptom**: Rate limit or permission denied

**Solutions**:

1. **Rate limit exceeded**: Wait 1 hour or use different token
2. **Permission denied**:
   - Check token scopes
   - Verify you have write access to repository
   - Try `prismweave config --test`

### "File already exists"

**Symptom**: Duplicate files or commit conflicts

**Solution**:

```bash
# The CLI automatically handles updates
# If you see this error, it might be a bug

# Workaround: Use dry-run to preview
prismweave capture URL --dry-run

# Then manually check GitHub for conflicts
```

## Capture Issues

### "No content extracted from page"

**Symptom**: Empty or minimal content captured

**Solutions**:

```bash
# Try with longer timeout
prismweave capture URL --timeout 60000

# Some sites block headless browsers
# Check if site requires JavaScript
# Check if site blocks automated access

# Workaround: Use browser extension instead
```

### "Content looks broken or incomplete"

**Symptom**: Markdown has formatting issues

**Solutions**:

1. Site might have dynamic content loading
2. Wait for specific selector:
   - Modify capture code to add `waitForSelector`
3. Use `--dry-run` to preview before saving
4. Some sites are not well-structured for conversion

### Invalid or broken URLs

**Symptom**: Capture fails for certain URLs

**Solutions**:

```bash
# Ensure URL is valid and accessible
curl -I URL

# Try with different user agent
# (requires code modification)

# Check if site requires authentication
# (not currently supported)
```

## Batch Processing Issues

### "File not found" when using --file

**Symptom**: Can't read URL file

**Solutions**:

```bash
# Use absolute path
prismweave capture --file /full/path/to/urls.txt

# Or relative path from current directory
cd /directory/with/file
prismweave capture --file urls.txt

# Check file exists and is readable
cat urls.txt
```

### "Some URLs failed"

**Symptom**: Batch processing has failures

**Solution**:

```bash
# Check the error messages for each URL
# Common causes:
# - Invalid URLs
# - Timeout (increase with --timeout)
# - Site blocking headless browsers
# - Network issues

# Retry failed URLs separately
prismweave capture FAILED_URL --timeout 60000
```

### Batch processing is slow

**Symptom**: Takes too long for many URLs

**Explanation**:

- Each URL requires browser startup (~3-5 seconds)
- Page load time varies by site
- GitHub API calls add overhead

**Optimization**:

```bash
# Process URLs in smaller batches
split -l 10 all-urls.txt batch-

# Process each batch
for file in batch-*; do
  prismweave capture --file $file
done
```

## Performance Issues

### High memory usage

**Symptom**: Process uses lots of RAM

**Solution**:

```bash
# Puppeteer uses significant memory
# Close browser between captures (automatic)
# Process URLs in smaller batches

# Monitor memory
# Unix/Linux: top
# Windows: Task Manager
```

### Slow captures

**Symptom**: Each capture takes very long

**Causes**:

1. Slow internet connection
2. Slow website
3. Large page with many resources
4. JavaScript-heavy site

**Solutions**:

```bash
# Increase timeout
prismweave capture URL --timeout 120000

# Skip images to speed up
prismweave capture URL --no-images
```

## Command Not Found

### "prismweave: command not found"

**Symptom**: After `npm link`, command not available

**Solutions**:

```bash
# Option 1: Reinstall with npm link
cd cli
npm unlink
npm link

# Option 2: Run directly
npm start -- capture URL

# Option 3: Use npx
npx prismweave capture URL

# Option 4: Add to PATH (Unix/Linux/Mac)
export PATH="$PATH:$HOME/.npm-global/bin"
```

## Windows-Specific Issues

### PowerShell execution policy

**Symptom**: Scripts blocked by execution policy

**Solution**:

```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Path issues on Windows

**Symptom**: Can't find executables

**Solution**:

1. Add Node.js to PATH
2. Restart terminal/PowerShell
3. Use full paths if needed

## Getting More Help

### Enable debug logging

```bash
# Set environment variable
export DEBUG=prismweave:*  # Unix/Linux/Mac
set DEBUG=prismweave:*     # Windows CMD
$env:DEBUG="prismweave:*"  # PowerShell

# Run command
prismweave capture URL
```

### Check versions

```bash
# Node.js version (needs 18+)
node --version

# npm version
npm --version

# PrismWeave CLI version
prismweave --version
```

### Clean reinstall

```bash
# Complete clean reinstall
cd cli
rm -rf node_modules package-lock.json dist
npm install
npm run build
npm link
```

### Still stuck?

1. Check existing issues: https://github.com/davidhayesbc/PrismWeave/issues
2. Create new issue with:
   - Error message
   - Command you ran
   - Output from `prismweave --version`
   - Operating system
   - Node.js version
3. Include relevant logs

## Common Error Messages

| Error              | Cause              | Solution                        |
| ------------------ | ------------------ | ------------------------------- |
| `ECONNREFUSED`     | Network issue      | Check internet connection       |
| `EACCES`           | Permission denied  | Use sudo or fix npm permissions |
| `MODULE_NOT_FOUND` | Missing dependency | Run `npm install`               |
| `ETIMEDOUT`        | Operation timeout  | Increase `--timeout`            |
| `ENOENT`           | File not found     | Check file path                 |
| `401 Unauthorized` | Invalid token      | Check GitHub token              |
| `404 Not Found`    | Invalid repo/URL   | Verify repository format        |
| `403 Forbidden`    | No permission      | Check token scopes              |

## Need More Help?

- Read the [README.md](README.md) for full documentation
- See [QUICKSTART.md](QUICKSTART.md) for setup guide
- Check [COMPARISON.md](COMPARISON.md) for use case guidance
- Visit GitHub Issues for community support
