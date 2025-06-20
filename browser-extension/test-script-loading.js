// Test script loading verification
// This script helps verify all imports work correctly

console.log('🔧 PrismWeave Script Loading Test');

try {
  // Test 1: Core utilities
  if (typeof PrismWeaveLogger !== 'undefined') {
    console.log('✅ Logger loaded');
  } else {
    console.error('❌ Logger not found');
  }

  if (typeof SettingsManager !== 'undefined') {
    console.log('✅ SettingsManager loaded');
  } else {
    console.error('❌ SettingsManager not found');
  }

  if (typeof ErrorHandler !== 'undefined') {
    console.log('✅ ErrorHandler loaded');
  } else {
    console.error('❌ ErrorHandler not found');
  }

  // Test 2: Main utilities
  if (typeof GitOperations !== 'undefined') {
    console.log('✅ GitOperations loaded');
  } else {
    console.error('❌ GitOperations not found');
  }

  if (typeof FileManager !== 'undefined') {
    console.log('✅ FileManager loaded');
  } else {
    console.error('❌ FileManager not found');
  }

  if (typeof SharedUtils !== 'undefined') {
    console.log('✅ SharedUtils loaded');
  } else {
    console.error('❌ SharedUtils not found');
  }

  // Test 3: Try instantiation
  try {
    const settingsManager = new SettingsManager();
    const gitOps = new GitOperations();
    const fileManager = new FileManager();
    console.log('✅ All classes can be instantiated');
  } catch (error) {
    console.error('❌ Instantiation failed:', error.message);
  }

  console.log('🎉 Script loading test complete!');
  
} catch (error) {
  console.error('❌ Test script failed:', error);
}
