// Quick debug script to see what's happening with Chrome mocking
console.log('Before setup:');
console.log('typeof chrome:', typeof chrome);
console.log('chrome:', chrome);

global.chrome = {
  storage: {
    sync: {
      get: () => console.log('sync.get called'),
      set: () => console.log('sync.set called'),
    },
  },
};

console.log('After setup:');
console.log('typeof chrome:', typeof chrome);
console.log('chrome:', chrome);
console.log('chrome.storage:', chrome.storage);
