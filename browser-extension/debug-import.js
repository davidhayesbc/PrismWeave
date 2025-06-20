const SettingsManager = require('./src/utils/settings-manager.js');

const manager = new SettingsManager();

const importData = {
  settings: {
    githubRepo: 'imported/repo',
    defaultFolder: 'tech',
    autoCommit: false
  }
};

console.log('Testing import validation...');
const validation = manager.validateImportData(importData);
console.log('Validation result:', validation);

if (!validation.isValid) {
  console.log('Validation errors:', validation.errors);
} else {
  console.log('Validation passed');
}

console.log('\nTesting direct settings validation...');
const directValidation = manager.validateSettings(importData.settings);
console.log('Direct validation result:', directValidation);
