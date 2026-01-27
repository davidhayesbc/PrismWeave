# Build and Run Scripts Review - Aspire-Focused Simplification

**Date:** January 26, 2026  
**Focus:** Simplify scripts now that Aspire is the primary orchestration tool

## Current State Analysis

### ✅ What You're Using (Keep)

#### 1. **Aspire Orchestration** (`apphost.cs`)
- **Status**: PRIMARY orchestration tool - well-configured
- **Manages**:
  - Ollama (port 11434)
  - AI Processing (port 4001) + MCP Server (port 4005)
  - MCP Inspector (ports 4009, 4010)
  - Visualization (port 4002)
  - Website (port 4003)
- **Benefits**: Integrated dashboard, health checks, OpenTelemetry, automatic service discovery
- **Conclusion**: ✅ **KEEP** - This is excellent and should be your primary workflow

#### 2. **npm Workspace Structure** (package.json)
- **Status**: Just implemented, working well
- **Benefits**: Centralized dependencies, consistent tooling
- **Conclusion**: ✅ **KEEP** - Core to modern development workflow

#### 3. **Component-Specific Scripts**
```bash
npm run build:browser-extension  # Browser extension build
npm run build:cli                # CLI TypeScript compilation
npm run test:cli                 # CLI tests (120/120 passing)
npm run test:browser-extension   # Browser extension tests
```
- **Conclusion**: ✅ **KEEP** - These are simple and component-focused

### ⚠️ Redundant/Complex (Simplify or Remove)

#### 1. **Docker Compose** (docker-compose.yml, docker-compose.prod.yml)
- **Status**: Duplicates Aspire functionality
- **Issues**:
  - Different port mappings than Aspire
  - Maintenance burden (two orchestration systems)
  - No integration with Aspire dashboard
- **Use Case**: Only needed for containerized production deployments
- **Recommendation**: 
  - ⚠️ **SIMPLIFY**: Keep docker-compose.prod.yml for production deployments
  - ❌ **REMOVE**: docker-compose.yml (dev mode - use Aspire instead)
  - ❌ **REMOVE**: All `docker:dev:*` scripts from package.json

#### 2. **build.js** (660 lines)
- **Status**: Overly complex custom build orchestration
- **Issues**:
  - Duplicates npm workspace functionality
  - Incremental copy logic could be simpler
  - Hard to maintain
- **Recommendation**: ✅ **SIMPLIFY** to use workspace commands:
  ```javascript
  // Current: Complex custom logic
  await this.buildBrowserExtension();  // ~100 lines
  
  // Better: Delegate to workspace
  execSync('npm run build --workspace=browser-extension');
  ```

#### 3. **serve-web.js** (400+ lines)
- **Status**: Custom HTTP server with directory listing, watch mode, etc.
- **Issues**:
  - Aspire's website component handles this better
  - Reinvents the wheel (static file serving)
- **Recommendation**: ⚠️ **REPLACE** with simpler alternatives:
  - For development: Use Aspire
  - For quick static serving: `npx serve dist/web`
  - Or keep minimal version (50 lines) if needed

#### 4. **Excessive Package.json Scripts** (50+ scripts)
- **Docker scripts**: 20+ docker-compose wrappers
- **Build variants**: Multiple build:web variations
- **Recommendation**: ❌ **REMOVE** 70% of scripts, keep essentials

#### 5. **VS Code Tasks** (50+ tasks in tasks.json)
- **Docker debug tasks**: 20+ manual curl/docker exec tasks
- **Status**: Debugging artifacts that should be removed
- **Recommendation**: ❌ **REMOVE** debugging tasks, keep core build/test tasks

## Recommended Script Structure

### Root package.json (Simplified)

```json
{
  "scripts": {
    "//": "=== Development (Primary) ===",
    "dev": "aspire run",
    "dev:dashboard": "open http://localhost:4000",
    
    "//": "=== Build ===",
    "build": "npm run build:all",
    "build:all": "npm run build:browser-extension && npm run build:cli && npm run build:web",
    "build:browser-extension": "npm run build --workspace=browser-extension",
    "build:cli": "npm run build --workspace=cli",
    "build:web": "node scripts/build-web.js",
    "clean": "rm -rf dist/ && npm run clean --workspaces",
    
    "//": "=== Testing ===",
    "test": "npm run test:all",
    "test:all": "npm test --workspaces --if-present",
    "test:cli": "npm test --workspace=cli",
    "test:browser-extension": "npm test --workspace=browser-extension",
    "test:ai": "cd ai-processing && .venv/bin/pytest tests/ -v",
    
    "//": "=== Code Quality ===",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "typecheck": "tsc --build",
    
    "//": "=== Production Deployment (Docker) ===",
    "docker:prod": "docker-compose -f docker-compose.prod.yml up -d",
    "docker:prod:build": "docker-compose -f docker-compose.prod.yml up --build -d",
    "docker:prod:down": "docker-compose -f docker-compose.prod.yml down"
  }
}
```

**Removed**: 35+ scripts (docker:dev:*, serve:*, watch:*, docker:shell:*, etc.)

### VS Code tasks.json (Simplified)

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Aspire: Run All Services",
      "type": "shell",
      "command": "aspire run",
      "isBackground": true,
      "problemMatcher": [],
      "group": {
        "kind": "build",
        "isDefault": true
      }
    },
    {
      "label": "Test: All Components",
      "type": "shell",
      "command": "npm",
      "args": ["test"],
      "group": {
        "kind": "test",
        "isDefault": true
      }
    },
    {
      "label": "Test: CLI",
      "type": "shell",
      "command": "npm",
      "args": ["run", "test:cli"]
    },
    {
      "label": "Test: Browser Extension",
      "type": "shell",
      "command": "npm",
      "args": ["run", "test:browser-extension"]
    },
    {
      "label": "Test: AI Processing",
      "type": "shell",
      "command": "npm",
      "args": ["run", "test:ai"]
    },
    {
      "label": "Build: All Components",
      "type": "shell",
      "command": "npm",
      "args": ["run", "build:all"],
      "group": "build"
    },
    {
      "label": "TypeScript: Check All",
      "type": "shell",
      "command": "tsc",
      "args": ["--build"],
      "group": "build",
      "problemMatcher": "$tsc"
    }
  ]
}
```

**Removed**: 40+ debugging tasks (all the docker exec curl commands, etc.)

### Simplified build.js

Replace 660-line build.js with ~150 lines that delegates to workspaces:

```javascript
#!/usr/bin/env node
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

class SimplifiedBuild {
  constructor() {
    this.root = __dirname;
  }

  exec(command, cwd = this.root) {
    execSync(command, { cwd, stdio: 'inherit' });
  }

  async build(target = 'all') {
    console.log(`🔨 Building: ${target}`);
    
    try {
      switch (target) {
        case 'all':
          this.buildAll();
          break;
        case 'browser-extension':
          this.exec('npm run build --workspace=browser-extension');
          break;
        case 'cli':
          this.exec('npm run build --workspace=cli');
          break;
        case 'web':
          await this.buildWeb();
          break;
        case 'clean':
          this.clean();
          break;
        default:
          throw new Error(`Unknown target: ${target}`);
      }
      console.log('✅ Build completed!');
    } catch (error) {
      console.error('❌ Build failed:', error.message);
      process.exit(1);
    }
  }

  buildAll() {
    this.exec('npm run build --workspace=browser-extension');
    this.exec('npm run build --workspace=cli');
    this.buildWeb();
  }

  async buildWeb() {
    const dist = path.join(this.root, 'dist', 'web');
    
    // Simple copy operations
    this.ensureDir(dist);
    this.copyDir('website/assets', path.join(dist, 'assets'));
    this.copyDir('dist/browser-extension', path.join(dist, 'extension'));
    this.copyDir('website/dist/bookmarklet', path.join(dist, 'bookmarklet'));
    
    // Generate index.html
    this.createWebIndex(dist);
  }

  ensureDir(dir) {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  }

  copyDir(src, dest) {
    if (!fs.existsSync(src)) return;
    
    this.ensureDir(dest);
    fs.cpSync(src, dest, { recursive: true });
  }

  createWebIndex(dist) {
    const html = `<!DOCTYPE html>
<html>
<head>
  <title>PrismWeave</title>
  <link rel="icon" href="./favicon.ico">
</head>
<body>
  <h1>PrismWeave Web Deployment</h1>
  <nav>
    <a href="./bookmarklet/generator.html">Bookmarklet Generator</a>
    <a href="./extension/">Browser Extension</a>
  </nav>
</body>
</html>`;
    
    fs.writeFileSync(path.join(dist, 'index.html'), html);
  }

  clean() {
    const targets = ['dist', 'cli/dist', 'ai-processing/__pycache__'];
    targets.forEach(t => {
      const p = path.join(this.root, t);
      if (fs.existsSync(p)) {
        fs.rmSync(p, { recursive: true, force: true });
        console.log(`🗑️ Removed ${t}`);
      }
    });
  }
}

// CLI
const target = process.argv[2] || 'all';
new SimplifiedBuild().build(target);
```

**Reduction**: 660 lines → 150 lines (77% smaller)

## Migration Plan

### Phase 1: Remove Docker Dev Scripts (Immediate)

1. **Update package.json**:
   ```bash
   # Remove these scripts:
   - docker:dev
   - docker:dev:build
   - docker:dev:ollama
   - docker:dev:ollama:build
   - docker:dev:detached
   - docker:logs
   - docker:logs:ai
   - docker:logs:web
   - docker:logs:viz
   - docker:logs:ollama
   - docker:shell:ai
   - docker:shell:web
   - docker:shell:viz
   - docker:pull-models
   - docker:health
   - docker:test
   ```

2. **Delete docker-compose.yml** (keep only docker-compose.prod.yml)

3. **Update .vscode/tasks.json**:
   - Remove all "Docker Compose:" and "Docker:" debugging tasks
   - Keep only production deployment tasks

**Impact**: Eliminates confusion, forces Aspire usage (which is better)

### Phase 2: Simplify build.js (Next)

1. **Create scripts/build-web.js** - Simplified web build only
2. **Replace build.js** with simplified version
3. **Update package.json** to use new scripts
4. **Test**: `npm run build:all`

**Impact**: Easier to maintain, clearer delegation to workspaces

### Phase 3: Simplify serve-web.js (Optional)

Options:
1. **Remove entirely** - Use Aspire for development
2. **Replace with**: `npx serve dist/web --port 8080`
3. **Minimal version** - Just static file serving (50 lines)

**Recommendation**: Option 1 (remove) or Option 2 (npx serve)

## Recommended Developer Workflow

### Development (Daily Use)

```bash
# Start everything with Aspire
npm run dev

# Open Aspire dashboard
open http://localhost:4000

# All services available:
# - AI Processing: http://localhost:4001
# - MCP Server: http://localhost:4005
# - Visualization: http://localhost:4002
# - Website: http://localhost:4003
# - Ollama: http://localhost:11434
# - MCP Inspector: http://localhost:4009
```

### Building

```bash
# Build all components
npm run build:all

# Build specific component
npm run build:browser-extension
npm run build:cli

# Clean build
npm run clean && npm run build:all
```

### Testing

```bash
# Run all tests
npm test

# Test specific component
npm run test:cli
npm run test:browser-extension
npm run test:ai
```

### Production Deployment

```bash
# Build production Docker images
npm run docker:prod:build

# Deploy
npm run docker:prod

# Stop
npm run docker:prod:down
```

## Files to Remove

- ❌ `docker-compose.yml` (replaced by Aspire)
- ❌ `serve-web.js` (replaced by Aspire or npx serve)
- ⚠️ Simplify `build.js` (660 lines → 150 lines)

## Files to Update

- ✅ `package.json` - Remove 35+ docker dev scripts
- ✅ `.vscode/tasks.json` - Remove 40+ debugging tasks
- ✅ `README.md` - Update with Aspire-first workflow
- ✅ `docs/DOCKER.md` - Update to reflect Aspire primary, Docker for prod only

## Benefits of Simplification

### Developer Experience
- ✅ **Single command development**: `npm run dev`
- ✅ **Unified dashboard**: All services visible in Aspire
- ✅ **Better debugging**: Aspire dashboard shows logs, metrics, traces
- ✅ **Health checks**: Automatic service health monitoring

### Maintenance
- ✅ **Less code**: ~1,000 lines of build scripts → ~200 lines
- ✅ **No duplication**: One orchestration system (Aspire), not two (Aspire + Docker)
- ✅ **Clear separation**: Aspire for dev, Docker Compose for production

### Reliability
- ✅ **Fewer ports to manage**: Aspire handles port allocation
- ✅ **Dependency management**: Aspire ensures services start in correct order
- ✅ **Consistent environment**: Same setup for all developers

## Summary

### Keep (Core Tools)
- ✅ Aspire (primary orchestration)
- ✅ npm workspaces (dependency management)
- ✅ Component-specific build scripts
- ✅ docker-compose.prod.yml (production deployments)

### Simplify
- ⚠️ build.js (660 → 150 lines)
- ⚠️ package.json scripts (50 → 15)
- ⚠️ .vscode/tasks.json (50 → 8 tasks)

### Remove
- ❌ docker-compose.yml (dev mode)
- ❌ serve-web.js (optional)
- ❌ 35+ docker dev scripts
- ❌ 40+ VS Code debugging tasks

### Result
- **Lines of code removed**: ~1,500
- **Scripts removed**: ~45
- **Tasks removed**: ~42
- **Complexity reduction**: ~70%
- **Developer workflow**: Simple, unified, Aspire-focused
