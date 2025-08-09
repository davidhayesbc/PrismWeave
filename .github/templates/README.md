# Website Templates

This directory contains template files for the PrismWeave website deployment.

## Template Files

### `index.html`
- Main landing page template
- Professional responsive design with CSS Grid layout
- Features hero section, extension showcase, and download links
- Uses `{{VERSION}}` placeholder for dynamic version substitution

### `404.html`
- Custom 404 error page
- Branded with PrismWeave styling
- Provides navigation back to home page

### `robots.txt`
- SEO optimization file
- Allows all crawlers and references sitemap

### `sitemap.xml`
- XML sitemap for search engines
- Uses `{{LAST_MODIFIED}}` placeholder for dynamic date substitution
- Includes all main pages with priorities

## Template Variables

- `{{VERSION}}` - Replaced with version from package.json
- `{{LAST_MODIFIED}}` - Replaced with current timestamp in ISO format

## Usage

These templates are processed by the GitHub Actions workflow in `deploy-website.yml`:

1. Variables are substituted using `sed` commands
2. Files are copied to `dist/web/` directory
3. Deployed to GitHub Pages

## Benefits

- Clean separation of HTML content from YAML workflow
- Prevents YAML syntax conflicts with HTML/CSS
- Maintains professional website design
- Enables dynamic content with template variables
