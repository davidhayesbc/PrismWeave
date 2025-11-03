(function () {
  var storageKey = 'prismweave-theme';
  var root = document.documentElement;
  var toggle = document.querySelector('[data-theme-toggle]');

  function systemTheme() {
    try {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    } catch (e) {
      return 'light';
    }
  }

  function getStoredTheme() {
    try {
      return localStorage.getItem(storageKey);
    } catch (error) {
      return null;
    }
  }

  function setStoredTheme(theme) {
    try {
      localStorage.setItem(storageKey, theme);
    } catch (error) {
      /* storage might be unavailable */
    }
  }

  function setTheme(theme) {
    root.dataset.theme = theme;
    if (toggle) {
      toggle.setAttribute(
        'aria-label',
        'Switch to ' + (theme === 'dark' ? 'light' : 'dark') + ' theme',
      );
    }
  }

  // Initialize from stored or system preference (root dataset may already be set early inline)
  var initial = getStoredTheme() || root.dataset.theme || systemTheme();
  setTheme(initial);

  // React to system theme changes if no manual override exists
  try {
    var media = window.matchMedia('(prefers-color-scheme: dark)');
    media.addEventListener('change', function (event) {
      if (!getStoredTheme()) {
        setTheme(event.matches ? 'dark' : 'light');
      }
    });
  } catch (e) {
    /* older browsers */
  }

  // Toggle click handler
  if (toggle) {
    toggle.addEventListener('click', function () {
      var nextTheme = root.dataset.theme === 'dark' ? 'light' : 'dark';
      setTheme(nextTheme);
      setStoredTheme(nextTheme);
    });
  }
})();
