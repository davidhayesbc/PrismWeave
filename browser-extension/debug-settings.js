// Test script to debug settings persistence
// Run this in the browser console on the options page

async function testSettingsPersistence() {
  console.log('=== Testing Settings Persistence ===');
  
  // Test 1: Load current settings
  console.log('1. Loading current settings...');
  try {
    const response = await chrome.runtime.sendMessage({ action: 'GET_SETTINGS' });
    console.log('Current settings:', response);
  } catch (error) {
    console.error('Failed to load settings:', error);
  }
  
  // Test 2: Check raw storage contents
  console.log('2. Checking raw storage...');
  try {
    const syncData = await chrome.storage.sync.get(null);
    console.log('Sync storage contents:', syncData);
    
    const localData = await chrome.storage.local.get(null);
    console.log('Local storage contents:', localData);
  } catch (error) {
    console.error('Failed to check storage:', error);
  }
  
  // Test 3: Save a test setting
  console.log('3. Saving test settings...');
  try {
    const testSettings = {
      githubToken: 'test-token-' + Date.now(),
      githubRepo: 'test/repo',
      defaultFolder: 'tech'
    };
    
    const response = await chrome.runtime.sendMessage({ 
      action: 'UPDATE_SETTINGS', 
      settings: testSettings 
    });
    console.log('Save response:', response);
    
    // Verify save by loading again
    const verifyResponse = await chrome.runtime.sendMessage({ action: 'GET_SETTINGS' });
    console.log('Verification load:', verifyResponse);
    
  } catch (error) {
    console.error('Failed to save/verify settings:', error);
  }
}

// Run the test
testSettingsPersistence();
