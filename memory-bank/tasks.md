# Task: Integrate Sentry Debug-IDs for Source Maps

## Description
Implement Sentry's debug-ids feature for more reliable source map handling in the Angular frontend. Debug-ids provide deterministic, globally unique identifiers that are embedded in minified JavaScript files and their corresponding source maps, making source map resolution more accurate and automatic.

## Complexity
Level: 2
Type: Enhancement

## Technology Stack
- Framework: Angular 20.0.x
- Build System: @angular-devkit/build-angular (esbuild)
- Monitoring: @sentry/angular 9.35.0
- Build Tool: @sentry/webpack-plugin (to be added)

## Requirements
- Embed debug-ids in production JavaScript files
- Include debug-ids in source maps
- Maintain compatibility with existing Sentry configuration
- Preserve current source map generation settings
- Update build and upload processes

## Status
- [x] Initialization complete (VAN phase)
- [x] Current configuration analyzed
- [x] Planning complete
- [x] Technology validation complete
- [x] Implementation complete
- [ ] Testing
- [ ] Reflection
- [ ] Archiving

## Investigation Results
- **Current Setup**: Traditional release-based source map upload
- **Sentry SDK**: v9.35.0 (supports debug-ids)
- **Sentry CLI**: v2.46.0 (supports debug-ids)
- **Build System**: Angular 20 with esbuild
- **Missing**: Sentry webpack plugin for automatic debug-id injection

## Implementation Plan

### Phase 1: Update Build Configuration ✅
1. Ensure source maps are generated
   - [x] Verify angular.json production config has sourceMap enabled
   - [x] Test production build generates .map files
   - [x] Confirm source maps are in correct location

### Phase 2: Update Source Map Upload Script ✅
1. Modify upload-sourcemaps.sh
   - [x] Update script to use `sourcemaps inject` command
   - [x] Update script to use `sourcemaps upload` command
   - [x] Remove old release-based commands
   - [x] Add option to delete source maps after upload

### Phase 3: Environment Configuration ✅
1. Set up environment variables
   - [x] Create .env.example file
   - [x] Document required environment variables in README
   - [ ] Test with actual Sentry credentials

### Phase 4: Update Build Process ✅
1. Modify build scripts
   - [x] Update production build configuration
   - [x] Ensure source maps are generated
   - [x] Update upload-sourcemaps.sh with debug-id approach

### Phase 5: Implementation Results ✅
1. Debug-id injection tested
   - [x] Successfully injected debug-ids into 4 JavaScript files
   - [x] Debug-ids added to corresponding source map files
   - [x] Created build-dev.sh for development builds
   - [x] Updated main README with auth token instructions

### Phase 6: Testing and Validation
1. Test debug-ids integration
   - [x] Build production version
   - [x] Verify debug-ids in JavaScript files
   - [x] Confirm source maps contain debug-ids
   - [ ] Test error tracking in Sentry with actual credentials

## Technology Validation Checkpoints
- [x] Project uses Angular 20 with esbuild
- [x] Sentry SDK supports debug-ids (v9.35.0)
- [x] Sentry CLI v2.46.0 supports debug-ids injection
- [x] Build process generates source maps correctly
- [x] Debug-id injection tested successfully (dry run)
- [x] Test build passes successfully

## Technology Decision
Due to Angular 20's use of the application builder (not compatible with custom-webpack), 
we will use Sentry CLI for debug-id injection instead of the webpack plugin approach.

## Dependencies
- Existing: @sentry/angular v9.35.0
- Existing: @sentry/cli v2.46.0
- No additional dependencies required (using Sentry CLI approach)

## Challenges & Mitigations
- **Challenge 1**: Angular 20 uses esbuild by default, not webpack
  - Mitigation: Use @angular-builders/custom-webpack to extend build process
  
- **Challenge 2**: Maintaining compatibility with existing Sentry configuration
  - Mitigation: Keep existing SDK configuration, only modify build process
  
- **Challenge 3**: Protecting source maps from public exposure
  - Mitigation: Configure server to block .map files or delete after upload

---

# Previous Completed Tasks

## Sentry Independent Traces Implementation - COMPLETED ✅
- **Date**: 2025-01-06
- **Archive**: /docs/archive/tasks/sentry-independent-traces-20250106.md
- **Summary**: Implemented independent transaction traces using startNewTrace()

## Angular 13 → 20 Migration - COMPLETED ✅
- **Date**: 2025-01-05
- **Summary**: Sequential migration through 7 major versions with signals implementation