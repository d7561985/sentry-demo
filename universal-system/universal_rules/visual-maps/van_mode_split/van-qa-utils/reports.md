---
# Universal MDC Format v1.0
rule: reports
type: visual-map
description: This component contains the formats for comprehensive success and failure
  reports generated upon completion of the QA validation process.
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
  token_weight: medium
  priority: medium
  cache_strategy: temporary
  load_timing: on_demand
---

# VAN QA: VALIDATION REPORTS

---
description: Utility for VAN QA validation reports
globs: van-qa-utils/reports.md
alwaysApply: false
---
# VAN QA: VALIDATION REPORTS

> **TL;DR:** This component contains the formats for comprehensive success and failure reports generated upon completion of the QA validation process.

## 📋 COMPREHENSIVE SUCCESS REPORT FORMAT

After all four validation points pass, generate this success report:

```
╔═════════════════════ 🔍 QA VALIDATION REPORT ══════════════════════╗
│ PROJECT: [Project Name] | TIMESTAMP: [Current Date/Time]            │
├─────────────────────────────────────────────────────────────────────┤
│ 1️⃣ DEPENDENCIES: ✓ Compatible                                       │
│ 2️⃣ CONFIGURATION: ✓ Valid & Compatible                             │
│ 3️⃣ ENVIRONMENT: ✓ Ready                                             │
│ 4️⃣ MINIMAL BUILD: ✓ Successful & Passed                            │
├─────────────────────────────────────────────────────────────────────┤
│ 🚨 FINAL VERDICT: PASS                                              │
│ ➡️ Clear to proceed to BUILD mode                                   │
╚═════════════════════════════════════════════════════════════════════╝
```

### Success Report Generation Example:
```powershell
function Generate-SuccessReport {
    param (
        [string]$ProjectName = "Current Project"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    $report = @"
╔═════════════════════ 🔍 QA VALIDATION REPORT ══════════════════════╗
│ PROJECT: $ProjectName | TIMESTAMP: $timestamp            │
├─────────────────────────────────────────────────────────────────────┤
│ 1️⃣ DEPENDENCIES: ✓ Compatible                                       │
│ 2️⃣ CONFIGURATION: ✓ Valid & Compatible                             │
│ 3️⃣ ENVIRONMENT: ✓ Ready                                             │
│ 4️⃣ MINIMAL BUILD: ✓ Successful & Passed                            │
├─────────────────────────────────────────────────────────────────────┤
│ 🚨 FINAL VERDICT: PASS                                              │
│ ➡️ Clear to proceed to BUILD mode                                   │
╚═════════════════════════════════════════════════════════════════════╝
"@
    
    # Save validation status (used by BUILD mode prevention mechanism)
    "PASS" | Set-Content -Path "memory-bank\.qa_validation_status"
    
    return $report
}
```

## ❌ FAILURE REPORT FORMAT

If any validation step fails, generate this detailed failure report:

```
⚠️⚠️⚠️ QA VALIDATION FAILED ⚠️⚠️⚠️

The following issues must be resolved before proceeding to BUILD mode:

1️⃣ DEPENDENCY ISSUES:
- [Detailed description of dependency issues]
- [Recommended fix]

2️⃣ CONFIGURATION ISSUES:
- [Detailed description of configuration issues]
- [Recommended fix]

3️⃣ ENVIRONMENT ISSUES:
- [Detailed description of environment issues]
- [Recommended fix]

4️⃣ BUILD TEST ISSUES:
- [Detailed description of build test issues]
- [Recommended fix]

⚠️ BUILD MODE IS BLOCKED until these issues are resolved.
Type 'VAN QA' after fixing the issues to re-validate.
```

### Failure Report Generation Example:
```powershell
function Generate-FailureReport {
    param (
        [string[]]$DependencyIssues = @(),
        [string[]]$ConfigIssues = @(),
        [string[]]$EnvironmentIssues = @(),
        [string[]]$BuildIssues = @()
    )
    
    $report = @"
⚠️⚠️⚠️ QA VALIDATION FAILED ⚠️⚠️⚠️

The following issues must be resolved before proceeding to BUILD mode:

"@
    
    if ($DependencyIssues.Count -gt 0) {
        $report += @"
1️⃣ DEPENDENCY ISSUES:
$(($DependencyIssues | ForEach-Object { "- $_" }) -join "`n")

"@
    }
    
    if ($ConfigIssues.Count -gt 0) {
        $report += @"
2️⃣ CONFIGURATION ISSUES:
$(($ConfigIssues | ForEach-Object { "- $_" }) -join "`n")

"@
    }
    
    if ($EnvironmentIssues.Count -gt 0) {
        $report += @"
3️⃣ ENVIRONMENT ISSUES:
$(($EnvironmentIssues | ForEach-Object { "- $_" }) -join "`n")

"@
    }
    
    if ($BuildIssues.Count -gt 0) {
        $report += @"
4️⃣ BUILD TEST ISSUES:
$(($BuildIssues | ForEach-Object { "- $_" }) -join "`n")

"@
    }
    
    $report += @"
⚠️ BUILD MODE IS BLOCKED until these issues are resolved.
Type 'VAN QA' after fixing the issues to re-validate.
"@
    
    # Save validation status (used by BUILD mode prevention mechanism)
    "FAIL" | Set-Content -Path "memory-bank\.qa_validation_status"
    
    return $report
}
```

**Next Step (on SUCCESS):** Load `van-qa-utils/mode-transitions.md` to handle BUILD mode transition.
**Next Step (on FAILURE):** Load `van-qa-utils/common-fixes.md` for issue remediation guidance. 