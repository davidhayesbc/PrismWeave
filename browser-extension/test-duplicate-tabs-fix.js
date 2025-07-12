// Enhanced test script to debug duplicate tab opening issue - NOTIFICATION FOCUS
// Run this in the popup console to debug and track exactly what's happening

(function testDuplicateTabsFixEnhanced() {
  console.log('🧪 Enhanced Duplicate Tabs Fix Test - NOTIFICATION FOCUS...');

  let tabCreateCallCount = 0;
  let windowOpenCallCount = 0;
  let openRepositoryCallCount = 0;

  // Mock chrome.tabs.create to count and trace all calls
  const originalCreate = chrome.tabs?.create;
  if (originalCreate) {
    chrome.tabs.create = function (createProperties, callback) {
      tabCreateCallCount++;
      console.log(`🚨 chrome.tabs.create called ${tabCreateCallCount} times`);
      console.log('📝 Create properties:', createProperties);
      console.log('📍 Call stack:');
      console.trace();

      // Call original method
      return originalCreate.call(this, createProperties, callback);
    };
  }

  // Mock window.open to count and trace all calls
  const originalWindowOpen = window.open;
  window.open = function (url, target, features) {
    windowOpenCallCount++;
    console.log(`🚨 window.open called ${windowOpenCallCount} times`);
    console.log('📝 URL:', url, 'Target:', target, 'Features:', features);
    console.log('📍 Call stack:');
    console.trace();

    // Call original method
    return originalWindowOpen.call(this, url, target, features);
  };

  // Test for existing notifications with click handlers
  const checkExistingNotifications = () => {
    console.log('\n🔔 Checking for existing notifications with click handlers...');

    const notifications = document.querySelectorAll(
      '[class*="notification"], [id*="notification"], .prismweave-notification'
    );
    console.log(`📊 Found ${notifications.length} potential notification elements`);

    notifications.forEach((notification, index) => {
      console.log(
        `  ${index + 1}. ${notification.tagName} (class: ${notification.className}, id: ${notification.id})`
      );

      // Check for click handlers
      if (typeof getEventListeners === 'function') {
        const listeners = getEventListeners(notification);
        const clickListeners = listeners.click ? listeners.click.length : 0;
        console.log(`    Click listeners: ${clickListeners}`);

        if (notification.onclick) {
          console.log(`    Has onclick handler: true`);
        }

        if (clickListeners > 1 || (clickListeners > 0 && notification.onclick)) {
          console.log(`    🚨 POTENTIAL DUPLICATE CLICK HANDLERS DETECTED`);
        }
      }

      // Check if it's clickable
      const isClickable =
        notification.style.cursor === 'pointer' ||
        notification.getAttribute('title')?.includes('Click to open');
      if (isClickable) {
        console.log(`    ✅ Clickable notification found`);
      }
    });
  };

  // Test 1: Check for popup instance protection
  const checkPopupInstances = () => {
    console.log('\n📊 Checking popup instances...');

    if (window.popupInstance) {
      console.log('✅ Found protected popup instance');
    } else {
      console.log('❌ No popup instance protection found');
    }

    // Check if PrismWeavePopup exists globally
    if (window.PrismWeavePopup) {
      console.log('✅ PrismWeavePopup class available globally');
    } else {
      console.log('❌ PrismWeavePopup class not found globally');
    }
  };

  // Test 2: Check event listeners
  const checkEventListeners = () => {
    console.log('\n🎯 Checking event listeners...');

    const buttons = [
      { id: 'view-repo', name: 'View Repository' },
      { id: 'capture-page', name: 'Capture Page' },
      { id: 'capture-selection', name: 'Capture Selection' },
      { id: 'settings-btn', name: 'Settings' },
    ];

    buttons.forEach(({ id, name }) => {
      const button = document.getElementById(id);
      if (!button) {
        console.log(`❌ Button ${name} (${id}) not found`);
        return;
      }

      // Check for listeners (Chrome DevTools only)
      if (typeof getEventListeners === 'function') {
        const listeners = getEventListeners(button);
        const clickListeners = listeners.click ? listeners.click.length : 0;
        console.log(
          `${clickListeners === 1 ? '✅' : '⚠️'} ${name} has ${clickListeners} click listeners`
        );

        if (clickListeners > 1) {
          console.log('  📍 Multiple listeners detected for:', name);
        }
      } else {
        console.log(`ℹ️ Cannot inspect listeners for ${name} (getEventListeners not available)`);
      }
    });
  };

  // Test 3: Check status action buttons
  const checkStatusActions = () => {
    console.log('\n📋 Checking status action buttons...');

    const statusActions = document.getElementById('status-actions');
    if (statusActions) {
      const actionButtons = statusActions.querySelectorAll('button');
      console.log(`📊 Found ${actionButtons.length} status action buttons`);

      actionButtons.forEach((button, index) => {
        const text = button.textContent || '';
        const actionType = button.getAttribute('data-action-type') || 'unknown';
        console.log(`  ${index + 1}. "${text}" (type: ${actionType})`);

        if (text.includes('Repository') || text.includes('GitHub')) {
          console.log(`    ⚠️ This button might conflict with main repository button`);
        }
      });

      if (actionButtons.length > 0) {
        console.log('💡 Status action buttons are present - they might be causing conflicts');
      }
    } else {
      console.log('✅ No status actions container found');
    }
  };

  // Test 4: Monitor openRepository calls
  const monitorOpenRepository = () => {
    console.log('\n� Setting up openRepository monitoring...');

    // Try to access the popup instance method
    if (window.popupInstance && window.popupInstance.openRepository) {
      const originalOpenRepository = window.popupInstance.openRepository.bind(window.popupInstance);

      window.popupInstance.openRepository = function () {
        openRepositoryCallCount++;
        console.log(`� openRepository called ${openRepositoryCallCount} times`);
        console.log('� Call stack:');
        console.trace();

        return originalOpenRepository.apply(this, arguments);
      };

      console.log('✅ openRepository monitoring active');
    } else {
      console.log('❌ Cannot monitor openRepository - method not accessible');
    }
  };

  // Test 5: Simulate clicking the view repository button
  const testViewRepositoryClick = () => {
    console.log('\n🖱️ Testing view repository button click...');

    const viewRepoBtn = document.getElementById('view-repo');
    if (!viewRepoBtn) {
      console.log('❌ View repository button not found');
      return;
    }

    console.log('🎯 Simulating click on view-repo button...');
    console.log('📊 Current state before click:');
    console.log(`  - chrome.tabs.create calls: ${tabCreateCallCount}`);
    console.log(`  - openRepository calls: ${openRepositoryCallCount}`);

    // Reset counters
    tabCreateCallCount = 0;
    openRepositoryCallCount = 0;

    // Click the button
    viewRepoBtn.click();

    // Check results after a short delay
    setTimeout(() => {
      console.log('\n📊 Results after button click:');
      console.log(`  - chrome.tabs.create calls: ${tabCreateCallCount}`);
      console.log(`  - openRepository calls: ${openRepositoryCallCount}`);

      if (tabCreateCallCount === 0) {
        console.log('❌ No tabs were created (repository might not be configured)');
      } else if (tabCreateCallCount === 1) {
        console.log('✅ Exactly one tab was created (fix working!)');
      } else {
        console.log(`🚨 ${tabCreateCallCount} tabs were created - DUPLICATE ISSUE STILL EXISTS`);
      }

      // Restore original method
      chrome.tabs.create = originalCreate;

      console.log('\n🏁 Test completed. Check console output above for details.');
    }, 1000);
  };

  // Run all tests
  checkPopupInstances();
  checkEventListeners();
  checkStatusActions();
  monitorOpenRepository();

  // Wait a bit then run the actual test
  setTimeout(() => {
    testViewRepositoryClick();
  }, 500);
})();
