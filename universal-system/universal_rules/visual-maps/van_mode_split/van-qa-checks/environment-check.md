---
# Universal MDC Format v1.0
rule: environment-check
type: visual-map
description: This component verifies that the build environment is properly set up
  with required tools and permissions.
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
  - write_files
  disabled:
  - delete_system_files
  - modify_critical_configs
metadata:
  token_weight: medium
  priority: medium
  cache_strategy: temporary
  load_timing: on_demand
---

# VAN QA: ENVIRONMENT VALIDATION

---
description: Process map for VAN QA environment validation
globs: van-qa-checks/environment-check.md
alwaysApply: false
---
# VAN QA: ENVIRONMENT VALIDATION

> **TL;DR:** This component verifies that the build environment is properly set up with required tools and permissions.

## 3️⃣ ENVIRONMENT VALIDATION PROCESS

```mermaid
graph TD
    Start["Environment Validation"] --> CheckEnv["Check Build Environment"]
    CheckEnv --> VerifyBuildTools["Verify Build Tools"]
    VerifyBuildTools --> ToolsStatus{"Build Tools<br>Available?"}
    
    ToolsStatus -->|"Yes"| CheckPerms["Check Permissions<br>and Access"]
    ToolsStatus -->|"No"| InstallTools["Install Required<br>Build Tools"]
    InstallTools --> RetryTools["Retry Verification"]
    RetryTools --> ToolsStatus
    
    CheckPerms --> PermsStatus{"Permissions<br>Sufficient?"}
    PermsStatus -->|"Yes"| EnvSuccess["Environment Validated<br>✅ PASS"]
    PermsStatus -->|"No"| FixPerms["Fix Permission<br>Issues"]
    FixPerms --> RetryPerms["Retry Permission<br>Check"]
    RetryPerms --> PermsStatus
    
    style Start fill:#4da6ff,stroke:#0066cc,color:white
    style EnvSuccess fill:#10b981,stroke:#059669,color:white
    style ToolsStatus fill:#f6546a,stroke:#c30052,color:white
    style PermsStatus fill:#f6546a,stroke:#c30052,color:white
```

### Environment Validation Implementation:
```powershell
# Example: Validate environment for a web project
function Validate-Environment {
    $requiredTools = @(
        @{Name = "git"; Command = "git --version"},
        @{Name = "node"; Command = "node --version"},
        @{Name = "npm"; Command = "npm --version"}
    )
    
    $missingTools = @()
    $permissionIssues = @()
    
    # Check build tools
    foreach ($tool in $requiredTools) {
        try {
            Invoke-Expression $tool.Command | Out-Null
        } catch {
            $missingTools += $tool.Name
        }
    }
    
    # Check write permissions in project directory
    try {
        $testFile = ".__permission_test"
        New-Item -Path $testFile -ItemType File -Force | Out-Null
        Remove-Item -Path $testFile -Force
    } catch {
        $permissionIssues += "Current directory (write permission denied)"
    }
    
    # Check if port 3000 is available (commonly used for dev servers)
    try {
        $listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, 3000)
        $listener.Start()
        $listener.Stop()
    } catch {
        $permissionIssues += "Port 3000 (already in use or access denied)"
    }
    
    # Display results
    if ($missingTools.Count -eq 0 -and $permissionIssues.Count -eq 0) {
        Write-Output "✅ Environment validated successfully"
        return $true
    } else {
        if ($missingTools.Count -gt 0) {
            Write-Output "❌ Missing tools: $($missingTools -join ', ')"
        }
        if ($permissionIssues.Count -gt 0) {
            Write-Output "❌ Permission issues: $($permissionIssues -join ', ')"
        }
        return $false
    }
}
```

## 📋 ENVIRONMENT VALIDATION CHECKPOINT

```
✓ CHECKPOINT: ENVIRONMENT VALIDATION
- All required build tools installed? [YES/NO]
- Project directory permissions sufficient? [YES/NO]
- Required ports available? [YES/NO]

→ If all YES: Continue to Minimal Build Test.
→ If any NO: Fix environment issues before continuing.
```

**Next Step (on PASS):** Load `van-qa-checks/build-test.md`.
**Next Step (on FAIL):** Check `van-qa-utils/common-fixes.md` for environment fixes. 