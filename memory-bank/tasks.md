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
- [ ] Planning
- [ ] Implementation
- [ ] Testing
- [ ] Reflection
- [ ] Archiving

## Investigation Results
- **Current Setup**: Traditional release-based source map upload
- **Sentry SDK**: v9.35.0 (supports debug-ids)
- **Sentry CLI**: v2.46.0 (supports debug-ids)
- **Build System**: Angular 20 with esbuild
- **Missing**: Sentry webpack plugin for automatic debug-id injection

---

# Previous Completed Tasks

## Sentry Independent Traces Implementation - COMPLETED ✅
- **Date**: 2025-01-06
- **Archive**: /docs/archive/tasks/sentry-independent-traces-20250106.md
- **Summary**: Implemented independent transaction traces using startNewTrace()

## Angular 13 → 20 Migration - COMPLETED ✅
- **Date**: 2025-01-05
- **Summary**: Sequential migration through 7 major versions with signals implementation