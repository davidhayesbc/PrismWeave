# PrismWeave Browser Extension - Privacy Policy Template

**Last Updated:** [Current Date]

## Introduction

This privacy policy explains how the PrismWeave browser extension ("Extension")
handles user data. PrismWeave is committed to protecting your privacy and
ensuring transparency about data handling practices.

## Data Collection

### What We Collect

PrismWeave **does NOT collect** any of the following:

- Personal information (name, email, address, etc.)
- Browsing history
- Website visit data
- Usage analytics
- Performance metrics
- Error reports sent to third parties

### What the Extension Stores Locally

The Extension stores the following information **locally on your device only**
using browser storage APIs:

1. **GitHub Personal Access Token**
   - Stored securely in browser's encrypted storage
   - Used only for GitHub API authentication
   - Never transmitted to any server except GitHub's API

2. **GitHub Repository Information**
   - Repository name (e.g., "username/repo-name")
   - Target branch name (e.g., "main")
   - Folder structure preferences

3. **Extension Settings**
   - File naming preferences
   - Content extraction preferences
   - UI configuration options

**Important:** All stored data remains on your device and is never transmitted
to PrismWeave servers (we don't have any servers!).

## Data Processing

### Content Capture

When you capture a web page:

1. **Local Processing**: The Extension extracts content directly in your browser
   using JavaScript
2. **No External Transmission**: Content is processed entirely within your
   browser
3. **GitHub Direct Upload**: Processed content is sent **directly from your
   browser to GitHub** using your personal access token
4. **No Intermediary**: PrismWeave never sees, stores, or processes your
   captured content

### GitHub Integration

The Extension communicates directly with GitHub's API:

- **Purpose**: To commit captured content to your GitHub repository
- **Authentication**: Uses your personal GitHub access token
- **Data Transmitted**: Only the content you explicitly capture and your GitHub
  credentials
- **Recipient**: Only GitHub's servers (api.github.com)
- **No PrismWeave Servers**: We do not operate any servers that handle your data

## Third-Party Services

The Extension integrates with the following third-party service:

### GitHub (Required)

- **Purpose**: Version control and document storage
- **Data Sent**: Captured content, commit messages, file metadata
- **Privacy Policy**:
  https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement
- **Your Control**: You control what is captured and where it is stored in your
  GitHub repository

**No Other Third-Party Services**: The Extension does not use analytics
services, crash reporting tools, or any other third-party data processors.

## Data Security

### Security Measures

1. **Token Storage**: GitHub tokens are stored using browser's secure storage
   APIs with encryption
2. **HTTPS Only**: All communications with GitHub use HTTPS encryption
3. **No Server-Side Storage**: We don't operate servers, so there's nothing to
   breach
4. **Local Processing**: Content extraction happens entirely in your browser
5. **No Tracking**: No cookies, analytics, or tracking mechanisms

### Your Responsibilities

To keep your data secure:

- **Protect Your Token**: Keep your GitHub personal access token confidential
- **Use Strong Passwords**: Secure your GitHub account with a strong password
- **Review Permissions**: Only grant necessary permissions to the Extension
- **Uninstall When Done**: Remove the Extension when no longer needed

## Data Retention

### Local Storage

Data stored locally in your browser:

- **Retention Period**: Indefinite (until you clear browser data or uninstall)
- **Deletion**: Available through browser settings or extension uninstallation
- **Your Control**: You can clear stored data at any time through your browser

### GitHub Storage

Data committed to your GitHub repository:

- **Retention**: Determined by GitHub's policies and your repository settings
- **Deletion**: You control retention through Git history management
- **Your Control**: Full control over repository and its contents

## User Rights

### Your Rights

You have the right to:

1. **Access**: View all data stored by the Extension in browser storage
2. **Correction**: Update or modify stored settings at any time
3. **Deletion**: Remove all Extension data by:
   - Clearing browser storage
   - Uninstalling the Extension
   - Deleting your GitHub repository (for captured content)
4. **Data Portability**: Export your captured documents from your GitHub
   repository
5. **Opt-Out**: Choose not to use the Extension at any time

### Exercising Your Rights

To exercise these rights:

- **View Data**: Open Extension options page
- **Delete Data**: Clear browser data or uninstall Extension
- **Export Data**: Use Git to clone your repository
- **Questions**: Contact us at [your-email@example.com]

## Children's Privacy

The Extension is not directed to individuals under 13 years of age. We do not
knowingly collect information from children under 13. If you believe a child has
provided information to the Extension, please contact us.

## Changes to Privacy Policy

### Notification of Changes

We may update this privacy policy from time to time. When we do:

1. We will update the "Last Updated" date at the top
2. Significant changes will be communicated through:
   - Extension update notifications
   - GitHub repository announcements
   - Website updates

### Your Continued Use

Continued use of the Extension after privacy policy changes constitutes
acceptance of the updated policy.

## Open Source

### Transparency

PrismWeave is **open source software**:

- **Source Code**: Available at https://github.com/davidhayesbc/PrismWeave
- **Verification**: Anyone can review the code to verify our privacy claims
- **Contributions**: Community contributions are welcome

### No Hidden Functionality

Being open source means:

- No hidden data collection
- No secret server communications
- Complete transparency in how the Extension works
- Community oversight and verification

## Questions and Compliance

### Contact Information

For privacy-related questions or concerns:

- **Email**: [your-email@example.com]
- **GitHub Issues**: https://github.com/davidhayesbc/PrismWeave/issues
- **Website**: [your-website-url]

### Regulatory Compliance

This Extension complies with:

- **GDPR** (General Data Protection Regulation) - EU
- **CCPA** (California Consumer Privacy Act) - California, USA
- **Other Jurisdictions**: We respect privacy regulations in all jurisdictions

### Data Protection Officer

For GDPR-related inquiries:

- **Contact**: [DPO email if applicable]
- **Response Time**: Within 30 days

## Additional Information

### Permissions Explanation

The Extension requests the following browser permissions:

1. **activeTab**: Access current page content for capture
   - **Purpose**: Extract content from web pages you're viewing
   - **Limitation**: Only when you explicitly click the Extension icon

2. **storage**: Local data storage
   - **Purpose**: Store GitHub token and Extension settings
   - **Limitation**: Data never leaves your device

3. **scripting**: Inject content extraction scripts
   - **Purpose**: Analyze page structure and extract content
   - **Limitation**: Only on pages you choose to capture

4. **notifications**: Display capture status
   - **Purpose**: Inform you about capture success/failure
   - **Limitation**: Only related to Extension functionality

5. **contextMenus**: Right-click menu integration
   - **Purpose**: Quick access to capture functionality
   - **Limitation**: Displayed only in browser context menu

### Data Minimization

We practice data minimization:

- **Collect**: Only what's strictly necessary
- **Process**: Only for stated purposes
- **Retain**: Only as long as needed
- **Share**: Never (except direct GitHub API calls)

### International Data Transfers

If you use GitHub:

- GitHub may transfer data internationally
- See GitHub's privacy policy for details
- The Extension itself performs no international transfers

## Consent

By installing and using the PrismWeave Extension, you consent to:

- This privacy policy
- Local storage of configuration data
- Direct communication with GitHub's API using your credentials
- Processing of captured content as described

You may withdraw consent at any time by uninstalling the Extension.

---

## Summary (TL;DR)

**Privacy in Brief:**

✅ **No data collection** - We don't collect any personal data  
✅ **Local processing** - Everything happens in your browser  
✅ **Direct to GitHub** - Content goes straight from you to GitHub  
✅ **No servers** - We don't operate any servers  
✅ **Open source** - Anyone can verify our code  
✅ **Your control** - You control all data and settings

**Bottom Line:** PrismWeave is designed for your privacy. Your data stays yours.

---

**Questions?** Contact us at [your-email@example.com]

**Source Code:** https://github.com/davidhayesbc/PrismWeave

**Report Issues:** https://github.com/davidhayesbc/PrismWeave/issues
