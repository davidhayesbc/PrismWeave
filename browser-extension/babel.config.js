// Babel configuration for PrismWeave Browser Extension
module.exports = {
  presets: [
    [
      '@babel/preset-env',
      {
        targets: {
          node: 'current',
        },
      },
    ],
    '@babel/preset-typescript',
  ],
  env: {
    test: {
      // No istanbul plugin - using c8 for coverage
      plugins: [],
    },
  },
};
