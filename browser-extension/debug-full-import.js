// Mock chrome storage
global.chrome = {
  storage: {
    sync: {
      set: () => Promise.resolve(),
    },
    local: {
      set: () => Promise.resolve(),
      get: () => Promise.resolve({})
    }
  }
};

const SettingsManager = require('./src/utils/settings-manager.js');

async function testImport() {
  const manager = new SettingsManager();
  
  const importData = {
    settings: {
      githubRepo: 'imported/repo',
      defaultFolder: 'tech',
      autoCommit: false
    }
  };

  console.log('Testing full import flow...');
  const result = await manager.importSettings(importData);
  console.log('Import result:', result);
}

testImport().catch(console.error);
