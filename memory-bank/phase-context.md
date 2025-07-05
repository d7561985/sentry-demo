# Phase Context

## Current Phase: VAN
- Task: Update Angular frontend to latest version
- Current Angular Version: 13.3.0
- Target: Latest Angular (20.x)

## Migration Path Analysis
The migration from Angular 13 to Angular 20 requires multiple major version updates:
- Angular 13 → 14: Control flow syntax changes
- Angular 14 → 15: Standalone components introduction
- Angular 15 → 16: Signal inputs/outputs
- Angular 16 → 17: New control flow syntax (@if, @for)
- Angular 17 → 18: Improved signals
- Angular 18 → 19: Enhanced performance
- Angular 19 → 20: Latest features

## Key Breaking Changes to Address
1. **Standalone Components** - Migration from NgModules
2. **New Control Flow Syntax** - Replace *ngIf/*ngFor with @if/@for
3. **Signal-based APIs** - Update inputs/outputs/queries
4. **Build System** - Migrate from webpack to esbuild
5. **Inject Function** - Replace constructor injection
6. **Node/TypeScript Requirements** - Update to Node 20+ and TypeScript 5.8+