---
# Universal MDC Format v1.0
rule: van-platform-detection
type: visual-map
description: Detects the OS, determines path separators, and notes command adaptations
  required.
version: '1.0'
created: '2025-06-28'
modified: '2025-06-28'
dependencies:
  required:
  - core/main
  optional: []
triggers:
  phases:
  - van
  complexity:
  - 1
  - 2
  - 3
  - 4
  conditions: []
capabilities:
  enabled:
  - read_files
  - execute_commands
  disabled:
  - delete_system_files
  - modify_critical_configs
metadata:
  token_weight: light
  priority: medium
  cache_strategy: temporary
  load_timing: on_demand
---

# VAN MODE: PLATFORM DETECTION

---
description: Visual process map for VAN mode platform detection
globs: van-platform-detection.md
alwaysApply: false
---
# VAN MODE: PLATFORM DETECTION

> **TL;DR:** Detects the OS, determines path separators, and notes command adaptations required.

## 🌐 PLATFORM DETECTION PROCESS

```mermaid
graph TD
    PD["Platform Detection"] --> CheckOS["Detect Operating System"]
    CheckOS --> Win["Windows"]
    CheckOS --> Mac["macOS"]
    CheckOS --> Lin["Linux"]
    
    Win & Mac & Lin --> Adapt["Adapt Commands<br>for Platform"]
    
    Win --> WinPath["Path: Backslash (\\)"]
    Mac --> MacPath["Path: Forward Slash (/)"]
    Lin --> LinPath["Path: Forward Slash (/)"]
    
    Win --> WinCmd["Command Adaptations:<br>dir, icacls, etc."]
    Mac --> MacCmd["Command Adaptations:<br>ls, chmod, etc."]
    Lin --> LinCmd["Command Adaptations:<br>ls, chmod, etc."]
    
    WinPath & MacPath & LinPath --> PathCP["Path Separator<br>Checkpoint"]
    WinCmd & MacCmd & LinCmd --> CmdCP["Command<br>Checkpoint"]
    
    PathCP & CmdCP --> PlatformComplete["Platform Detection<br>Complete"]
    
    style PD fill:#4da6ff,stroke:#0066cc,color:white
    style PlatformComplete fill:#10b981,stroke:#059669,color:white
```

## 📋 CHECKPOINT VERIFICATION TEMPLATE (Example)

```
✓ SECTION CHECKPOINT: PLATFORM DETECTION
- Operating System Detected? [YES/NO]
- Path Separator Confirmed? [YES/NO]
- Command Adaptations Noted? [YES/NO]

→ If all YES: Platform Detection Complete.
→ If any NO: Resolve before proceeding.
```

**Next Step:** Load and process `van-file-verification.md`. 