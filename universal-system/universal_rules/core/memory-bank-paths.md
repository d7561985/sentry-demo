---
# Universal MDC Format v1.0
rule: memory-bank-paths
type: core
description: Rule for CORE MEMORY BANK FILE LOCATIONS
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
  - plan
  - creative
  - implement
  - reflect
  - archive
  complexity:
  - 1
  - 2
  - 3
  - 4
  conditions:
  - always_loaded: Core rules are always available
capabilities:
  enabled:
  - rule_loading
  - memory_bank_operations
  - read_files
  - write_files
  disabled:
  - delete_system_files
  - modify_critical_configs
metadata:
  token_weight: light
  priority: critical
  cache_strategy: persistent
  load_timing: immediate
---

# CORE MEMORY BANK FILE LOCATIONS

---
description: Defines canonical paths for core Memory Bank files.
globs: memory-bank-paths.md
alwaysApply: true
---

# CORE MEMORY BANK FILE LOCATIONS

**CRITICAL:** All core Memory Bank files reside within the `memory-bank/` directory at the project root. Do NOT create or modify these files outside this directory unless explicitly instructed for archiving purposes.

* **Tasks File:** `memory-bank/tasks.md` - This file is used for active, in-progress task tracking, detailing steps, checklists, and component lists. Its content, particularly the detailed checklists, is merged into the main archive document for the task upon completion. After archival, `tasks.md` is cleared to be ready for the next task. It is an ephemeral working document during a task's lifecycle, with its persistent record captured in the task's archive file.
* **Active Context File:** `memory-bank/activeContext.md`
* **Progress File:** `memory-bank/progress.md`
* **Project Brief File:** `memory-bank/projectbrief.md`
* **Product Context File:** `memory-bank/productContext.md`
* **System Patterns File:** `memory-bank/systemPatterns.md`
* **Tech Context File:** `memory-bank/techContext.md`
* **Style Guide File:** `memory-bank/style-guide.md`
* **Creative Phase Docs:** `memory-bank/creative/creative-[feature_name].md`
* **Reflection Docs:** `memory-bank/reflection/reflection-[task_id].md`
* **Archive Directory:** `memory-bank/archive/archive-[task_id].md`

**Verification Mandate:** Before any `create_file` or `edit_file` operation on these core files, verify the path starts with `memory-bank/`. If attempting to create a new core file (e.g., `tasks.md` at the start of a project), ensure it is created at `memory-bank/tasks.md`.
