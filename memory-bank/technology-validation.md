# Technology Validation Checklist

## Angular 20 Migration Technology Stack

### Core Technologies
- **Framework**: Angular 20.0.x
- **Runtime**: Node.js 20.19.0+ or 22.12.0+ or 24.0.0+
- **Language**: TypeScript 5.8.0 - 5.9.0
- **Build System**: @angular-devkit/build-angular with esbuild
- **Package Manager**: npm 10.x+

### Validation Steps

#### 1. Environment Setup Validation
- [ ] Node.js version check: `node --version` (must be 20.19.0+)
- [ ] npm version check: `npm --version` (must be 10.x+)
- [ ] Angular CLI installation: `npm install -g @angular/cli@latest`
- [ ] CLI version verification: `ng version`

#### 2. Migration Tools Validation
- [ ] Verify ng update availability: `ng update`
- [ ] Check migration schematics:
  - [ ] @angular/core:standalone
  - [ ] @angular/core:control-flow
  - [ ] @angular/core:signals
  - [ ] @angular/core:inject-migration

#### 3. Dependency Compatibility
- [ ] Sentry Angular SDK compatibility with Angular 20
- [ ] RxJS 7.x compatibility verification
- [ ] TypeScript strict mode compatibility

#### 4. Build System Validation
- [ ] Create minimal Angular 20 project: `ng new test-angular20`
- [ ] Verify esbuild integration in angular.json
- [ ] Test build process: `ng build`
- [ ] Verify development server: `ng serve`

#### 5. Feature Compatibility Testing
- [ ] Standalone components creation and usage
- [ ] New control flow syntax (@if, @for)
- [ ] Signal inputs/outputs functionality
- [ ] Inject function usage

### Proof of Concept Requirements

Create a minimal Angular 20 application with:
```bash
# Create new Angular 20 project
ng new angular20-poc --routing --style=css

# Navigate to project
cd angular20-poc

# Add Sentry
ng add @sentry/angular

# Create standalone component
ng generate component test-standalone --standalone

# Run development server
ng serve
```

### Build Configuration Validation

Verify angular.json uses the new builder:
```json
"build": {
  "builder": "@angular-devkit/build-angular:application",
  "options": {
    "outputPath": "dist/angular20-poc",
    "index": "src/index.html",
    "browser": "src/main.ts",
    "polyfills": ["zone.js"],
    "tsConfig": "tsconfig.app.json"
  }
}
```

### Success Criteria
- [ ] Node.js and npm versions meet requirements
- [ ] Angular CLI successfully installed and working
- [ ] Test project builds without errors
- [ ] Development server runs successfully
- [ ] Sentry integration confirmed working
- [ ] All migration schematics available

### Known Issues & Solutions
1. **Node.js Version**: Must use Node 20.19.0+ (not just 20.0.0)
2. **TypeScript Version**: Strictly between 5.8.0 and 5.9.0
3. **Zone.js**: Still required, configured in polyfills
4. **Sentry Compatibility**: Verify latest @sentry/angular supports Angular 20