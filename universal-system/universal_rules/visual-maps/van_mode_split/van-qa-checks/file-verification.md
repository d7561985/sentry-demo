---
# Universal MDC Format v1.0
rule: file-verification
type: visual-map
description: Rule for file-verification
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
  enabled: []
  disabled:
  - delete_system_files
  - modify_critical_configs
metadata:
  token_weight: light
  priority: medium
  cache_strategy: temporary
  load_timing: on_demand
---

 