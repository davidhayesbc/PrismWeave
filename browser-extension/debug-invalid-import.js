const SettingsManager = require('./src/utils/settings-manager.js');

const manager = new SettingsManager();

const invalidImportData = {
  settings: {
    githubRepo: 'invalid-format',
    defaultFolder: 'nonexistent-folder'
  }
};

console.log('Testing invalid import validation...');
const validation = manager.validateImportData(invalidImportData);
console.log('Validation result:', validation);
