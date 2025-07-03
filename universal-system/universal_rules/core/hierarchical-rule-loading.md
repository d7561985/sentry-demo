---
# Universal MDC Format v1.0
rule: hierarchical-rule-loading
type: core
description: This rule implements an optimized loading system that only loads necessary
  rules based on context, complexity level, and current phase to maximize token efficiency.
version: '1.0'
created: '2025-06-28'
modified: '2025-06-28'
dependencies:
  required:
  - core/main
  optional:
  - rules/creative_phase_uiux
  - rules/verification_advanced
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
  - read_files
  - memory_bank_operations
  - execute_commands
  - create_plans
  disabled:
  - delete_system_files
  - modify_critical_configs
metadata:
  token_weight: heavy
  priority: critical
  cache_strategy: persistent
  load_timing: immediate
---

# HIERARCHICAL RULE LOADING SYSTEM

---
description: Hierarchical rule loading system for optimized token usage
globs: "**/rule-loading*/**", "**/optimization*/**"
alwaysApply: false
---

# HIERARCHICAL RULE LOADING SYSTEM

> **TL;DR:** This rule implements an optimized loading system that only loads necessary rules based on context, complexity level, and current phase to maximize token efficiency.

## 🧠 HIERARCHICAL RULE STRUCTURE

```mermaid
graph TD
    Root["Root Rules"] --> Core["Core Rules<br>(Always Loaded)"]
    Root --> Common["Common Rules<br>(Mode Independent)"]
    Root --> Mode["Mode-Specific<br>Rules"]
    Root --> Level["Complexity Level<br>Rules"]
    
    Core --> Platform["Platform<br>Detection"]
    Core --> File["File<br>Operations"]
    Core --> Transition["Mode<br>Transitions"]
    
    Mode --> VAN["VAN Mode<br>Rules"]
    Mode --> PLAN["PLAN Mode<br>Rules"]
    Mode --> CREATIVE["CREATIVE Mode<br>Rules"]
    Mode --> IMPLEMENT["IMPLEMENT Mode<br>Rules"]
    Mode --> REFLECT["REFLECT Mode<br>Rules"]
    
    Level --> Level1["Level 1<br>Rules"]
    Level --> Level2["Level 2<br>Rules"]
    Level --> Level3["Level 3<br>Rules"]
    Level --> Level4["Level 4<br>Rules"]
    
    style Root fill:#4da6ff,stroke:#0066cc,color:white
    style Core fill:#ffa64d,stroke:#cc7a30,color:white
    style Common fill:#4dbb5f,stroke:#36873f,color:white
    style Mode fill:#d94dbb,stroke:#a3378a,color:white
    style Level fill:#4dbbbb,stroke:#368787,color:white
```

## 📊 RULE LOADING PROTOCOL

```mermaid
sequenceDiagram
    participant User
    participant LoadManager
    participant RuleCache
    participant FileSystem
    
    User->>LoadManager: Request mode activation
    LoadManager->>RuleCache: Check cached core rules
    RuleCache-->>LoadManager: Return cached rules if available
    
    LoadManager->>FileSystem: Load essential mode rules
    FileSystem-->>LoadManager: Return essential rules
    
    LoadManager->>LoadManager: Register lazy loaders for specialized rules
    LoadManager->>User: Return initialized mode
    
    User->>LoadManager: Request specialized functionality
    LoadManager->>RuleCache: Check specialized rule cache
    RuleCache-->>LoadManager: Return cached rule if available
    
    alt Rule not in cache
        LoadManager->>FileSystem: Load specialized rule
        FileSystem-->>LoadManager: Return specialized rule
        LoadManager->>RuleCache: Cache specialized rule
    end
    
    LoadManager->>User: Execute specialized functionality
```

## 🔄 RULE LOADING IMPLEMENTATION

```javascript
// Pseudocode for hierarchical rule loading
class RuleLoadManager {
  constructor() {
    this.cache = {
      core: {},
      common: {},
      mode: {},
      level: {}
    };
    this.lazyLoaders = {};
  }
  
  // Initialize a mode with only essential rules
  initializeMode(modeName, complexityLevel) {
    // Always load core rules
    this.loadCoreRules();
    
    // Load common rules
    this.loadCommonRules();
    
    // Load essential mode-specific rules
    this.loadEssentialModeRules(modeName);
    
    // Load complexity level rules
    this.loadComplexityRules(complexityLevel);
    
    // Register lazy loaders for specialized functionality
    this.registerLazyLoaders(modeName, complexityLevel);
    
    return {
      modeName,
      complexityLevel,
      status: "initialized"
    };
  }
  
  // Load only when specialized functionality is needed
  loadSpecializedRule(ruleType) {
    if (this.lazyLoaders[ruleType]) {
      if (!this.cache.specialized[ruleType]) {
        const rule = this.lazyLoaders[ruleType]();
        this.cache.specialized[ruleType] = rule;
      }
      return this.cache.specialized[ruleType];
    }
    return null;
  }
  
  // Register specialized rule loaders based on mode and complexity
  registerLazyLoaders(modeName, complexityLevel) {
    // Clear existing lazy loaders
    this.lazyLoaders = {};
    
    // Register mode-specific lazy loaders
    if (modeName === "CREATIVE") {
      this.lazyLoaders["architecture"] = () => this.loadRule("creative-phase-architecture.md");
      this.lazyLoaders["algorithm"] = () => this.loadRule("creative-phase-algorithm.md");
      this.lazyLoaders["uiux"] = () => this.loadRule("creative-phase-uiux.md");
    } else if (modeName === "IMPLEMENT") {
      this.lazyLoaders["testing"] = () => this.loadRule("implementation-testing.md");
      this.lazyLoaders["deployment"] = () => this.loadRule("implementation-deployment.md");
    }
    
    // Register complexity-specific lazy loaders
    if (complexityLevel >= 3) {
      this.lazyLoaders["comprehensive-planning"] = () => this.loadRule("planning-comprehensive.md");
      this.lazyLoaders["advanced-verification"] = () => this.loadRule("verification-advanced.md");
    }
  }
}
```

## 📋 RULE DEPENDENCY MAP

```mermaid
graph TD
    Main["main.md"] --> Core1["platform-awareness.md"]
    Main --> Core2["file-verification.md"]
    Main --> Core3["command-execution.md"]
    
    subgraph "VAN Mode"
        VanMap["van-mode-map.md"] --> Van1["van-complexity-determination.md"]
        VanMap --> Van2["van-file-verification.md"]
        VanMap --> Van3["van-platform-detection.md"]
    end
    
    subgraph "PLAN Mode"
        PlanMap["plan-mode-map.md"] --> Plan1["task-tracking-basic.md"]
        PlanMap --> Plan2["planning-comprehensive.md"]
    end
    
    subgraph "CREATIVE Mode"
        CreativeMap["creative-mode-map.md"] --> Creative1["creative-phase-enforcement.md"]
        CreativeMap --> Creative2["creative-phase-metrics.md"]
        Creative1 & Creative2 -.-> CreativeSpecialized["Specialized Creative Rules"]
        CreativeSpecialized --> CArch["creative-phase-architecture.md"]
        CreativeSpecialized --> CAlgo["creative-phase-algorithm.md"]
        CreativeSpecialized --> CUIUX["creative-phase-uiux.md"]
    end
    
    subgraph "IMPLEMENT Mode"
        ImplementMap["implement-mode-map.md"] --> Impl1["implementation-guide.md"]
        ImplementMap --> Impl2["testing-strategy.md"]
    end
```

## 🔍 MODE-SPECIFIC RULE LOADING

### VAN Mode Essential Rules
```markdown
- main.md (Core)
- platform-awareness.md (Core)
- file-verification.md (Core)
- van-mode-map.md (Mode)
```

### PLAN Mode Essential Rules
```markdown
- main.md (Core)
- plan-mode-map.md (Mode)
- task-tracking-[complexity].md (Level)
```

### CREATIVE Mode Essential Rules
```markdown
- main.md (Core)
- creative-mode-map.md (Mode)
- creative-phase-enforcement.md (Mode)
```

### CREATIVE Mode Specialized Rules (Lazy Loaded)
```markdown
- creative-phase-architecture.md (Specialized)
- creative-phase-algorithm.md (Specialized)
- creative-phase-uiux.md (Specialized)
```

### IMPLEMENT Mode Essential Rules
```markdown
- main.md (Core)
- command-execution.md (Core)
- implement-mode-map.md (Mode)
```

## 🚀 IMPLEMENTATION BENEFITS

The hierarchical loading system provides:

1. **Reduced Initial Loading**: Only essential rules loaded at start (~70% token reduction)
2. **Cached Core Rules**: Rules shared between modes are cached
3. **Specialized Rule Loading**: Specialized rules loaded only when needed
4. **Complexity-Based Loading**: Only load rules appropriate for task complexity

## 📈 TOKEN USAGE COMPARISON

| Approach | Initial Tokens | Specialized Tokens | Total Tokens |
|----------|---------------|-------------------|--------------|
| Original System | ~70,000 | Included in initial | ~70,000 |
| Hierarchical System | ~15,000 | ~10,000 (on demand) | ~25,000 |
| **Token Reduction** | **~55,000 (78%)** | **N/A** | **~45,000 (64%)** |

## 🔄 USAGE EXAMPLE

### Example: Creative Phase with Architecture Rule

```javascript
// Initialize the CREATIVE mode with only essential rules
const mode = ruleManager.initializeMode("CREATIVE", 3);

// Core and essential mode rules are loaded 
// Architecture rules are NOT loaded yet

// Later, when architecture design is needed:
const architectureRule = ruleManager.loadSpecializedRule("architecture");

// Now the architecture rule is loaded and cached
```

## 🧪 RULE LOADING VERIFICATION

To ensure the rule loading system is working optimally:

```markdown
## Rule Loading Verification

- Core Rules: [Loaded]
- Mode-Essential Rules: [Loaded]
- Complexity-Level Rules: [Loaded]
- Specialized Rules: [Not Loaded]

Current Token Usage: [X] tokens
Potential Token Savings: [Y] tokens
```

This hierarchical approach ensures optimal token usage while maintaining all functionality.