// Test runner script for PrismWeave Browser Extension
// Provides testing utilities and test execution commands

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

class TestRunner {  constructor() {
    this.testDir = __dirname;
    this.coverageDir = path.join(this.testDir, 'coverage');
  }

  // Run all tests
  runAllTests() {
    console.log('🧪 Running all PrismWeave tests...\n');
    
    try {
      execSync('npm test', { 
        stdio: 'inherit', 
        cwd: this.testDir 
      });
      console.log('\n✅ All tests completed successfully!');
    } catch (error) {
      console.error('\n❌ Tests failed:', error.message);
      process.exit(1);
    }
  }

  // Run tests with coverage
  runTestsWithCoverage() {
    console.log('📊 Running tests with coverage report...\n');
    
    try {
      execSync('npm run test:coverage', { 
        stdio: 'inherit', 
        cwd: this.testDir 
      });
      
      this.displayCoverageSummary();
      console.log('\n✅ Tests with coverage completed!');
    } catch (error) {
      console.error('\n❌ Coverage tests failed:', error.message);
      process.exit(1);
    }
  }

  // Run tests in watch mode
  runTestsInWatchMode() {
    console.log('👀 Running tests in watch mode...\n');
    
    try {
      execSync('npm run test:watch', { 
        stdio: 'inherit', 
        cwd: this.testDir 
      });
    } catch (error) {
      console.error('\n❌ Watch mode failed:', error.message);
      process.exit(1);
    }
  }

  // Run specific test suite
  runTestSuite(suiteName) {
    console.log(`🎯 Running test suite: ${suiteName}\n`);
    
    try {
      execSync(`npm test -- --testNamePattern="${suiteName}"`, { 
        stdio: 'inherit', 
        cwd: this.testDir 
      });
      console.log(`\n✅ Test suite "${suiteName}" completed!`);
    } catch (error) {
      console.error(`\n❌ Test suite "${suiteName}" failed:`, error.message);
      process.exit(1);
    }
  }

  // Run tests for specific file
  runTestFile(fileName) {
    console.log(`📄 Running tests for: ${fileName}\n`);
    
    try {
      execSync(`npm test -- ${fileName}`, { 
        stdio: 'inherit', 
        cwd: this.testDir 
      });
      console.log(`\n✅ Tests for "${fileName}" completed!`);
    } catch (error) {
      console.error(`\n❌ Tests for "${fileName}" failed:`, error.message);
      process.exit(1);
    }
  }

  // Run unit tests only
  runUnitTests() {
    console.log('🔧 Running unit tests...\n');
    
    try {
      execSync('npm test -- tests/utils tests/background tests/popup tests/content', { 
        stdio: 'inherit', 
        cwd: this.testDir 
      });
      console.log('\n✅ Unit tests completed!');
    } catch (error) {
      console.error('\n❌ Unit tests failed:', error.message);
      process.exit(1);
    }
  }

  // Run integration tests only
  runIntegrationTests() {
    console.log('🔄 Running integration tests...\n');
    
    try {
      execSync('npm test -- tests/integration', { 
        stdio: 'inherit', 
        cwd: this.testDir 
      });
      console.log('\n✅ Integration tests completed!');
    } catch (error) {
      console.error('\n❌ Integration tests failed:', error.message);
      process.exit(1);
    }
  }

  // Run CI tests (no watch, with coverage)
  runCITests() {
    console.log('🤖 Running CI tests...\n');
    
    try {
      execSync('npm run test:ci', { 
        stdio: 'inherit', 
        cwd: this.testDir 
      });
      
      this.displayCoverageSummary();
      this.generateTestReport();
      console.log('\n✅ CI tests completed!');
    } catch (error) {
      console.error('\n❌ CI tests failed:', error.message);
      process.exit(1);
    }
  }

  // Display coverage summary
  displayCoverageSummary() {
    const coverageFile = path.join(this.coverageDir, 'coverage-summary.json');
    
    if (fs.existsSync(coverageFile)) {
      const coverage = JSON.parse(fs.readFileSync(coverageFile, 'utf8'));
      const total = coverage.total;
      
      console.log('\n📊 Coverage Summary:');
      console.log('────────────────────');
      console.log(`Lines:      ${total.lines.pct}%`);
      console.log(`Functions:  ${total.functions.pct}%`);
      console.log(`Branches:   ${total.branches.pct}%`);
      console.log(`Statements: ${total.statements.pct}%`);
    }
  }

  // Generate test report
  generateTestReport() {
    const timestamp = new Date().toISOString();
    const report = {
      timestamp,
      testSuites: this.getTestSuiteInfo(),
      coverage: this.getCoverageInfo(),
      environment: {
        node: process.version,
        npm: execSync('npm --version', { encoding: 'utf8' }).trim(),
        jest: this.getJestVersion()
      }
    };

    const reportFile = path.join(this.testDir, 'test-report.json');
    fs.writeFileSync(reportFile, JSON.stringify(report, null, 2));
    console.log(`\n📋 Test report generated: ${reportFile}`);
  }

  // Get test suite information
  getTestSuiteInfo() {
    const testFiles = this.findTestFiles();
    
    return testFiles.map(file => ({
      name: path.basename(file, '.test.js'),
      path: file,
      type: this.getTestType(file)
    }));
  }

  // Find all test files
  findTestFiles() {
    const testFiles = [];
    
    const searchDir = (dir) => {
      const items = fs.readdirSync(dir);
      
      items.forEach(item => {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory()) {
          searchDir(fullPath);
        } else if (item.endsWith('.test.js')) {
          testFiles.push(fullPath);
        }
      });
    };

    searchDir(path.join(this.testDir, 'tests'));
    return testFiles;
  }

  // Determine test type based on file path
  getTestType(filePath) {
    if (filePath.includes('integration')) return 'integration';
    if (filePath.includes('utils')) return 'unit';
    if (filePath.includes('background')) return 'unit';
    if (filePath.includes('popup')) return 'unit';
    if (filePath.includes('content')) return 'unit';
    return 'unknown';
  }

  // Get coverage information
  getCoverageInfo() {
    const coverageFile = path.join(this.coverageDir, 'coverage-summary.json');
    
    if (fs.existsSync(coverageFile)) {
      return JSON.parse(fs.readFileSync(coverageFile, 'utf8'));
    }
    
    return null;
  }

  // Get Jest version
  getJestVersion() {
    try {
      const packageJson = JSON.parse(
        fs.readFileSync(path.join(this.testDir, 'package.json'), 'utf8')
      );
      return packageJson.devDependencies.jest || 'unknown';
    } catch (error) {
      return 'unknown';
    }
  }

  // Validate test setup
  validateTestSetup() {
    console.log('🔍 Validating test setup...\n');

    const requiredFiles = [
      'jest.config.js',
      'tests/setup.js',
      '.babelrc'
    ];

    const requiredDirs = [
      'tests',
      'tests/utils',
      'tests/background',
      'tests/popup',
      'tests/content',
      'tests/integration'
    ];

    let isValid = true;

    // Check required files
    requiredFiles.forEach(file => {
      const filePath = path.join(this.testDir, file);
      if (!fs.existsSync(filePath)) {
        console.error(`❌ Missing required file: ${file}`);
        isValid = false;
      } else {
        console.log(`✅ Found: ${file}`);
      }
    });

    // Check required directories
    requiredDirs.forEach(dir => {
      const dirPath = path.join(this.testDir, dir);
      if (!fs.existsSync(dirPath)) {
        console.error(`❌ Missing required directory: ${dir}`);
        isValid = false;
      } else {
        console.log(`✅ Found: ${dir}/`);
      }
    });

    // Check test files
    const testFiles = this.findTestFiles();
    console.log(`\n📊 Found ${testFiles.length} test files:`);
    testFiles.forEach(file => {
      const relativePath = path.relative(this.testDir, file);
      console.log(`   ${relativePath}`);
    });

    if (isValid) {
      console.log('\n✅ Test setup validation passed!');
    } else {
      console.error('\n❌ Test setup validation failed!');
      process.exit(1);
    }
  }

  // Clean test artifacts
  cleanTestArtifacts() {
    console.log('🧹 Cleaning test artifacts...\n');

    const artifactPaths = [
      path.join(this.testDir, 'coverage'),
      path.join(this.testDir, 'test-report.json'),
      path.join(this.testDir, '.nyc_output')
    ];

    artifactPaths.forEach(artifactPath => {
      if (fs.existsSync(artifactPath)) {
        fs.rmSync(artifactPath, { recursive: true, force: true });
        console.log(`🗑️  Removed: ${path.basename(artifactPath)}`);
      }
    });

    console.log('\n✅ Test artifacts cleaned!');
  }

  // Show help
  showHelp() {
    console.log(`
🧪 PrismWeave Test Runner

Available commands:
  all              Run all tests
  coverage         Run tests with coverage report  
  watch            Run tests in watch mode
  unit             Run unit tests only
  integration      Run integration tests only
  ci               Run CI tests (no watch, with coverage)
  validate         Validate test setup
  clean            Clean test artifacts
  suite <name>     Run specific test suite
  file <path>      Run tests for specific file
  help             Show this help message

Examples:
  node test-runner.js all
  node test-runner.js coverage
  node test-runner.js suite "SettingsManager"
  node test-runner.js file "settings-manager.test.js"
`);
  }
}

// CLI interface
if (require.main === module) {
  const runner = new TestRunner();
  const command = process.argv[2];
  const argument = process.argv[3];

  switch (command) {
    case 'all':
      runner.runAllTests();
      break;
    case 'coverage':
      runner.runTestsWithCoverage();
      break;
    case 'watch':
      runner.runTestsInWatchMode();
      break;
    case 'unit':
      runner.runUnitTests();
      break;
    case 'integration':
      runner.runIntegrationTests();
      break;
    case 'ci':
      runner.runCITests();
      break;
    case 'validate':
      runner.validateTestSetup();
      break;
    case 'clean':
      runner.cleanTestArtifacts();
      break;
    case 'suite':
      if (!argument) {
        console.error('❌ Please provide a suite name');
        process.exit(1);
      }
      runner.runTestSuite(argument);
      break;
    case 'file':
      if (!argument) {
        console.error('❌ Please provide a file path');
        process.exit(1);
      }
      runner.runTestFile(argument);
      break;
    case 'help':
    default:
      runner.showHelp();
      break;
  }
}

module.exports = TestRunner;
