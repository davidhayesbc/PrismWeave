# Better URL Configuration Approaches for PrismWeave Bookmarklet

The bookmarklet now supports multiple flexible approaches for configuring the injectable script URL, eliminating the need for hardcoded URLs.

## Implemented Solutions

### 1. Auto-Detection (Current Implementation) ✅

The bookmarklet automatically detects the correct URL based on where it's running:

```typescript
private detectInjectableBaseUrl(): string {
  // Check HTML data attribute first
  const configElement = document.querySelector('[data-injectable-url]');
  if (configElement && configElement.dataset.injectableUrl) {
    return configElement.dataset.injectableUrl;
  }

  const currentUrl = window.location.href;
  
  // Development mode
  if (currentUrl.includes('localhost') || currentUrl.startsWith('file://')) {
    return 'http://localhost:3000/injectable';
  }
  
  // GitHub Pages auto-detection
  if (currentUrl.includes('github.io')) {
    const url = new URL(window.location.href);
    const basePath = url.pathname.split('/').slice(0, -1).join('/');
    return `${url.origin}${basePath}/injectable`;
  }
  
  // Default fallback
  return 'https://davidhayesbc.github.io/prismweave/injectable';
}
```

### 2. HTML Data Attribute Configuration

You can override the URL by adding a data attribute to any element on the page:

```html
<!-- Option 1: On a dedicated config element -->
<div data-injectable-url="https://my-custom-cdn.com/injectable"></div>

<!-- Option 2: On the form itself -->
<form id="generator-form" data-injectable-url="https://my-custom-cdn.com/injectable">
  <!-- form content -->
</form>

<!-- Option 3: On the container -->
<div id="main-container" data-injectable-url="https://my-custom-cdn.com/injectable">
  <!-- page content -->
</div>
```

### 3. Environment Variable Support (Build-time)

During build, you can set environment variables:

```bash
# For development
PRISMWEAVE_INJECTABLE_URL=http://localhost:3000/injectable npm run build

# For staging
PRISMWEAVE_INJECTABLE_URL=https://staging.example.com/injectable npm run build

# For custom deployment
PRISMWEAVE_INJECTABLE_URL=https://my-cdn.com/prismweave/injectable npm run build
```

## Priority Order

The system uses this priority order for URL detection:

1. **HTML Data Attribute** (`data-injectable-url`) - Highest priority
2. **Environment Variable** (`PRISMWEAVE_INJECTABLE_URL`) - Build-time only
3. **Auto-Detection** based on current URL:
   - `localhost` or `file://` → `http://localhost:3000/injectable`
   - `github.io` → Auto-construct from current URL path
4. **Default Fallback** → `https://davidhayesbc.github.io/prismweave/injectable`

## Benefits

- ✅ **No Hardcoded URLs**: Automatically adapts to deployment environment
- ✅ **Development Friendly**: Works seamlessly with localhost development
- ✅ **Flexible Deployment**: Easy to customize for different hosting providers
- ✅ **Path Intelligence**: Automatically constructs correct paths on GitHub Pages
- ✅ **Override Capability**: HTML data attributes allow page-specific customization
- ✅ **Fallback Safety**: Always has a working default URL

## Testing

You can test different configurations:

```javascript
// Test the detection logic in browser console
const generator = new BookmarkletGeneratorUI();
console.log('Injectable URL:', generator.injectableBaseUrl);

// Test with custom data attribute
document.body.setAttribute('data-injectable-url', 'https://example.com/test');
// Reload the page to see the new URL being used
```

This approach eliminates hardcoded URLs while providing flexibility for different deployment scenarios.