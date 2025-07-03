---
# Universal MDC Format v1.0
rule: rule-calling-help
type: visual-map
description: This file provides examples and reminders on how to properly call VAN
  QA rules using the fetch_rules tool.
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
  disabled:
  - delete_system_files
  - modify_critical_configs
metadata:
  token_weight: light
  priority: medium
  cache_strategy: temporary
  load_timing: on_demand
---

# VAN QA: HOW TO CALL RULES

---
description: Utility for remembering how to call VAN QA rules
globs: van-qa-utils/rule-calling-help.md
alwaysApply: false
---
# VAN QA: HOW TO CALL RULES

> **TL;DR:** This file provides examples and reminders on how to properly call VAN QA rules using the fetch_rules tool.

## 🚨 RULE CALLING SYNTAX

Always use the `fetch_rules` tool with the correct syntax:

```
<function_calls>
<invoke name="fetch_rules">
<parameter name="rule_names">["isolation_rules/visual-maps/rule-name"]
</invoke>
</function_calls> 