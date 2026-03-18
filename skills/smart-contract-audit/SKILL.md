---
name: DeFi Smart Contract Audit
description: A rigorous, adversarial DeFi smart contract audit process with specialized checks for DEX, AMM, Lending, and token interactions.
version: "2.8.0"
updated: "2026-01"
---

# DeFi Smart Contract Audit Skill (Advanced)

This skill executes a high-precision security audit using a "Team of Rivals" approach, **specialized for DeFi protocols**.

## 📂 Skill Resources

| Resource | Path | Description |
|----------|------|-------------|
| **Audit Report Template** | `resources/audit_report_template.md` | Template for final comprehensive audit report (`.audit/Audit-Report.md`) |
| **Vulnerability Patterns** | `references/VULNERABILITY_PATTERNS.md` | Solidity vulnerability code examples - Use in Phase 3 (Vulnerability Discovery) |
| **DeFi Checklist** | `references/DEFI_CHECKLIST.md` | Protocol-specific audit checklists - Use in Phase 3 (both Function-Based and Flow-Based analysis) |

## 🚀 Workflow Overview

1.  **Phase 0 (Architect)**: Map architecture, identify DeFi protocol type, and verify documentation.
2.  **Phase 1 (Automated Scan)** ⚠️ **OPTIONAL**: Run static analysis tools (Slither, Mythril) to catch low-hanging fruit. **Skip if tools unavailable**.
3.  **Phase 2 (Contract Understanding)** ⚠️ **MANDATORY**: Deep understanding of contract architecture, function purposes, data flows, and parameter semantics.
4.  **Phase 3 (Senior Auditor)**:
    *   **Function-Based Analysis**: Analyze each function individually using Phase 2 documentation
    *   **Flow-Based Analysis**: Analyze contract flows/capabilities using Phase 2 data flow analysis
    *   Both approaches reference `references/DEFI_CHECKLIST.md` and `references/VULNERABILITY_PATTERNS.md`
5.  **Phase 4 (Defense)**: Verify findings using **Invariants** and assess real-world impact.

---

## 🛠️ Instructions

> ⚠️ **CRITICAL EXECUTION ORDER**: You MUST execute phases **SEQUENTIALLY**, one at a time. Each phase must be completed, output in conversation, and **SAVED BY AI using `write` tool** to a separate file before starting the next phase.
>
> **⚠️ MANDATORY FILE-BASED WORKFLOW:**
>
> **⚠️ FILE STRUCTURE**: All audit files must be saved in the `.audit/` directory with the following structure:
> ```
> .audit/
> ├── blueprints/
> │   ├── 0_Setup.md
> │   ├── 1_Automated_Security_Scan.md (OPTIONAL - only if Phase 1 is run)
> │   ├── 2_Understanding.md
> │   ├── 3_Vulnerability_Scan.md
> │   └── 4_Defense_Verification.md
> └── Audit-Report.md (final report)
> ```
>
> **Phase 0:**
> 1. Read necessary files (README, main contracts) for architecture understanding
> 2. Complete Phase 0 analysis
> 3. **MANDATORY**: Output complete Phase 0 content in conversation (formatted as markdown)
> 4. **MANDATORY**: **SAVE** this content to `.audit/blueprints/0_Setup.md` using `write` tool immediately after outputting
> 5. **VERIFICATION**: When starting Phase 1, **MUST** use `read_file` to read `.audit/blueprints/0_Setup.md` - verify it exists and contains Phase 0 results. If file doesn't exist or is empty, STOP and re-run Phase 0.
> 6. **DO NOT** proceed to Phase 1 until Phase 0 file is verified to exist and contains content
>
> **Phase 1 (OPTIONAL):**
> 1. **DECISION**: Check if automated tools (Slither, Mythril) are available
>    - **If tools available**: Proceed with Phase 1
>    - **If tools NOT available**: **SKIP Phase 1** and proceed directly to Phase 2
> 2. **If running Phase 1**:
>    - **FIRST STEP** - Use `read_file` tool to read `.audit/blueprints/0_Setup.md` - verify it exists and contains Phase 0 results
>    - Re-read relevant code files with Phase 1 focus (automated scan patterns, security patterns)
>    - Run automated tools or perform manual pattern-based analysis
>    - Output complete Phase 1 content in conversation (formatted as markdown)
>    - **SAVE** this content to `.audit/blueprints/1_Automated_Security_Scan.md` using `write` tool immediately after outputting
> 3. **If skipping Phase 1**: Proceed directly to Phase 2 (no file creation needed)
>
> **Phase 2:**
> 1. Read `.audit/blueprints/0_Setup.md` (required). Optionally read Phase 1 file if available.
> 2. Re-read ALL contract files (most comprehensive code reading).
> 3. Complete analysis: architecture, function inventory, data flows, parameter semantics, consistency check.
> 4. Output and **SAVE** to `.audit/blueprints/2_Understanding.md`.
>
> **Phase 3:**
> 1. **MANDATORY**: **FIRST STEP** - Use `read_file` tool to read `.audit/blueprints/0_Setup.md` and `.audit/blueprints/2_Understanding.md` - verify both exist and contain results. If files don't exist or are empty, STOP and re-run previous phases.
> 2. **OPTIONAL**: If Phase 1 was run, read `.audit/blueprints/1_Automated_Security_Scan.md` for context (this file may not exist if Phase 1 was skipped)
> 2. **MANDATORY**: Reference Phase 2 function inventory and parameter semantics when analyzing vulnerabilities - explicitly cite Phase 2 findings in your analysis
> 3. **MANDATORY**: Re-read relevant code sections with Phase 3 focus (vulnerability discovery based on Phase 2 understanding)
> 4. Complete Phase 3 analysis (check ALL items in DeFi-specific vulnerability checklist)
> 5. **MANDATORY**: Output complete Phase 3 content in conversation (formatted as markdown with all vulnerability findings)
> 6. **MANDATORY**: **SAVE** this content to `.audit/blueprints/3_Vulnerability_Scan.md` using `write` tool immediately after outputting
> 7. **VERIFICATION**: When starting Phase 4, **MUST** use `read_file` to read all previous blueprint files (`.audit/blueprints/0_Setup.md` through `.audit/blueprints/3_Vulnerability_Scan.md`) - verify all exist and contain vulnerability findings
> 8. **DO NOT** proceed to Phase 4 until Phase 3 file is verified to exist and contains findings
>
> **Phase 4:**
> 1. **MANDATORY**: Use `read_file` tool to read required blueprint files:
>    - `.audit/blueprints/0_Setup.md` (required)
>    - `.audit/blueprints/2_Understanding.md` (required)
>    - `.audit/blueprints/3_Vulnerability_Scan.md` (required)
>    - `.audit/blueprints/1_Automated_Security_Scan.md` (optional - only if Phase 1 was run)
>    - Verify required files exist and contain results. If required files don't exist or are empty, STOP and ask user to complete previous phases first.
> 2. **MANDATORY**: For EACH finding from Phase 3, re-read relevant code sections and perform verification
> 3. Complete Phase 4 analysis (verification and impact assessment for each Phase 3 finding)
> 4. **MANDATORY**: Output complete Phase 4 content in conversation (formatted as markdown with verification results for each finding)
> 5. **MANDATORY**: Instruct user to save this content to `.audit/blueprints/4_Defense_Verification.md`
> 6. **VERIFICATION**: When generating final report, use `read_file` to verify Phase 4 file exists and contains verification results
>
> **Final Report:**
> 1. **MANDATORY**: Use `read_file` tool to read `.audit/blueprints/3_Vulnerability_Scan.md` and `.audit/blueprints/4_Defense_Verification.md` (primary sources)
> 2. **OPTIONAL**: Reference `.audit/blueprints/0_Setup.md`, `.audit/blueprints/2_Understanding.md`, and `.audit/blueprints/1_Automated_Security_Scan.md` (if exists) for context
> 3. **FOCUS**: The final report should center around Phase 3 (Vulnerability Scan) and Phase 4 (Defense & Verification) comprehensive results
> 4. **Structure**: Include executive summary, findings from Phase 3 with Phase 4 verification, severity classification, and recommendations
> 5. **Output**: Output final report in conversation (formatted as markdown)
> 6. **Instruct User**: "Please save this content to `.audit/Audit-Report.md`. This is the final comprehensive audit report focusing on vulnerabilities and their verification."
>
> **DO NOT:**
> - ❌ Read all files at once and analyze everything together
> - ❌ Output all phases in a single execution
> - ❌ Skip ahead to later phases before completing earlier ones (Exception: Phase 1 can be skipped if tools unavailable)
> - ❌ Skip reading previous phase files when starting a new phase (Exception: Phase 1 file is optional)
> - ❌ Skip re-reading code files for each phase (each phase has different focus)
> - ❌ Combine multiple phases into one output
>
> **DO:**
> - ✅ Complete one phase fully before starting the next
> - ✅ Output each phase's complete content in conversation after completing it
> - ✅ **SAVE each phase to a separate file using `write` tool immediately after outputting**
> - ✅ **ALWAYS read previous phase files using `read_file` tool as the FIRST STEP when starting a new phase**
> - ✅ Re-read relevant code files for each phase (each phase has different focus)
> - ✅ Reference previous phase findings explicitly in your analysis
> - ✅ Use findings from earlier phases to inform later phases

---

### Phase 0: Architecture & Protocol Classification

> ⚠️ **MANDATORY FILE OPERATIONS**:
> - At the START: Read `README.md` (if exists) and main contract files to understand the project
> - At the END: Output complete Phase 0 content in conversation (following the Phase 0 Output Format below), then **SAVE** to `.audit/blueprints/0_Setup.md` using `write` tool
> - **VERIFICATION**: When starting Phase 1, **MUST** read Phase 0 file using `read_file` tool as the FIRST STEP
> - **DO NOT** proceed to Phase 1 until Phase 0 file is verified to exist and contains content

1.  **Initialize**: Read project structure and main contract files.
2.  **Identify Protocol Type**: Classify the DeFi protocol:
    *   `DEX/AMM` - Token swaps, liquidity pools (Uniswap, Curve, etc.)
    *   `Lending` - Borrow/Lend protocols (Aave, Compound, etc.)
    *   `Yield/Vault` - Yield aggregators, vaults (Yearn, etc.)
    *   `Stablecoin/PSM` - Stablecoin mechanisms, PSM modules
    *   `Bridge/Router` - Cross-chain or multi-protocol routers
    *   `Staking` - Token staking, reward distribution
3.  **Doc Check**: Read `README.md` or specs (if exists). Compare against the code outline.
    *   **If README is empty or generic**: Mark "Documentation vs Code Discrepancies" as `N/A - No meaningful spec provided` and proceed.
4.  **Action**: Document all Phase 0 findings, specifically noting:
    - Protocol type classification
    - Architecture overview
    - Key contracts and their purposes
    - Money flow diagram
    - Roles & access control
    - External integrations
    - Documentation mismatches

**Phase 0 Output Format**:
```markdown
# Phase 0: Architecture & Protocol Classification

## Protocol Classification
- **Type:** [DEX/AMM | Lending | Yield/Vault | Stablecoin/PSM | Bridge/Router | Staking]
- **Blockchain:** [Ethereum | TRON | BSC | etc.]
- **Solidity Version:** [version range]

## Key Contracts
| Contract | LOC | Purpose |
|----------|-----|---------|
| [Contract Name] | [lines] | [Purpose] |

## Money Flow Architecture
[Diagram or narrative description]

## Roles & Access Control
| Role | Storage | Permissions | Transfer Method |
|------|---------|-------------|-----------------|
| [Role] | [var] | [permissions] | [method] |

## External Integrations
| Integration | Interface | Risk Level | Notes |
|-------------|-----------|------------|-------|
| [Integration] | [Interface] | [Level] | [Notes] |

## Documentation vs Code Discrepancies
[Findings or N/A]
```

5.  **MANDATORY OUTPUT**: Output complete Phase 0 content in conversation (formatted as markdown following the format above). Then **IMMEDIATELY SAVE** this content to `.audit/blueprints/0_Setup.md` using `write` tool. After saving, proceed to Phase 1 (or skip to Phase 2 if automated tools are unavailable).

---

### Phase 1: Automated Security Scan (OPTIONAL)
**Goal**: Use static analysis tools to find common vulnerabilities before manual review.

> ⚠️ **OPTIONAL PHASE**: This phase is **OPTIONAL**. If automated tools (Slither, Mythril) are not available or cannot be run, you can **SKIP Phase 1** and proceed directly to Phase 2.

> ⚠️ **FILE OPERATIONS** (only if running Phase 1):
> - At the START: **FIRST STEP** - **MUST** use `read_file` tool to read `.audit/blueprints/0_Setup.md` - verify it exists and contains Phase 0 results. If file doesn't exist or is empty, STOP and re-run Phase 0.
> - During analysis: Re-read relevant code files with Phase 1 focus (security patterns, compilation issues)
> - At the END: Output complete Phase 1 content in conversation (following the Phase 1 Output Format below), then **SAVE** to `.audit/blueprints/1_Automated_Security_Scan.md` using `write` tool

> **Reference**: This phase uses methodology from the `smart-contract-security` skill.

#### Step 1: Static Analysis Tools

> 🔴 **DECISION POINT**: 
> - **If tools are available**: Run automated scans (Slither, Mythril, Semgrep)
> - **If tools are NOT available**: **SKIP Phase 1** and proceed directly to Phase 2
> 
> **Note**: Phase 3 will perform comprehensive vulnerability discovery regardless of whether Phase 1 was run. Phase 1 is a time-saver but not required.

**Option A: If tools are available** (user can run them):
- **Slither** (Fast vulnerability detection):
  ```bash
  # Basic scan
  slither . --exclude-dependencies
  
  # JSON output for parsing
  slither . --json slither-report.json --exclude-dependencies
  
  # Focus on high-impact detectors only
  slither . --detect reentrancy-eth,reentrancy-no-eth,arbitrary-send,controlled-delegatecall,suicidal,unprotected-upgrade
  ```
- **Mythril** (Symbolic execution - deeper analysis):
  ```bash
  # Single contract analysis
  myth analyze contracts/Contract.sol --solc-json mythril.config.json
  
  # Full project
  myth analyze . --solc-json mythril.config.json
  ```
- **Semgrep** (Custom rules for smart contracts):
  ```bash
  semgrep --config "p/smart-contracts" .
  ```

**Option B: Skip Phase 1** (if tools unavailable):
- **SKIP Phase 1** and proceed directly to Phase 2
- Phase 3 will perform comprehensive vulnerability discovery regardless
- No manual pattern-based analysis needed in Phase 1

> **Note**: The following steps (Step 2, Step 3) are only executed if you chose to run Phase 1.

#### Step 2: Pre-Audit Checklist
(Only if running Phase 1) Before proceeding to manual review, verify:

- [ ] Code compiles without warnings (`forge build` or `npx hardhat compile`)
- [ ] Tests pass with good coverage (`forge test` or `npx hardhat test`)
- [ ] No critical Slither findings unaddressed
- [ ] Dependencies reviewed (check for known vulnerabilities)

#### Step 3: Triage Automated Findings
(Only if running Phase 1) If automated tools were run, triage the findings:

| Slither Detector | Severity | Action |
|-----------------|----------|--------|
| `reentrancy-eth` | Critical | Manual review required |
| `arbitrary-send` | Critical | Manual review required |
| `suicidal` | Critical | Manual review required |
| `unprotected-upgrade` | High | Check if intentional |
| `controlled-delegatecall` | High | Manual review required |
| `unchecked-transfer` | Medium | Verify SafeERC20 usage |
| `reentrancy-benign` | Low | Usually false positive |
| `naming-convention` | Info | Ignore unless egregious |

**Action** (only if running Phase 1): Document all Phase 1 findings, including:
- Pre-audit checklist results (with checkboxes: [x] or [ ])
- Automated scan status (whether tools were run)
- Key security patterns identified (ReentrancyGuard, SafeMath, access control, etc.)
- Any automated tool findings (with `[AUTO]` tag)

**If skipping Phase 1**: No action needed. Proceed directly to Phase 2.

**Phase 1 Output Format** (only if running Phase 1):
```markdown
# Phase 1: Automated Security Scan

## Pre-Audit Checklist
- [x] Code compiles without warnings
- [ ] Tests pass with good coverage
- [x] No critical findings unaddressed
- [x] Dependencies reviewed

## Automated Scan Status
[Status: Tools run / Manual analysis / Not available]

## Key Security Patterns Identified
[Table or list of patterns found]

## Automated/Manual Findings
[Any findings from tools or manual pattern matching]
```

**If skipping Phase 1**: No output needed. Proceed directly to Phase 2.

**OUTPUT** (only if running Phase 1):
- Output complete Phase 1 content in conversation (formatted as markdown following the format above)
- **SAVE** this content to `.audit/blueprints/1_Automated_Security_Scan.md` using `write` tool immediately after outputting
- After saving, proceed to Phase 2

**If skipping Phase 1**: Proceed directly to Phase 2 without creating Phase 1 file.

---

### Phase 2: Contract Understanding (MANDATORY)

**Goal**: Achieve deep understanding of contract architecture, function purposes, data flows, and parameter semantics before vulnerability discovery.

> ⚠️ **FILE OPERATIONS**:
> - **START**: Read `.audit/blueprints/0_Setup.md` (required). Optionally read `.audit/blueprints/1_Automated_Security_Scan.md` if Phase 1 was run.
> - **ANALYSIS**: Re-read ALL contract files from top to bottom (most comprehensive code reading phase).
> - **END**: Output complete Phase 2 content, then **SAVE** to `.audit/blueprints/2_Understanding.md`.

#### Step 2.1: Contract Architecture Understanding

1. **Read entire contract** from top to bottom (every function, modifier, state variable).
2. **Identify**: Primary purpose, core functionality, contract hierarchy (inheritance, libraries, interfaces).
3. **Identify design patterns**: Proxy/Upgradeable, Factory, Router/Aggregator, etc.

#### Step 2.2: Complete Function Inventory & Documentation

**For EVERY function** (public, external, internal, private), document:

- **Visibility & Modifiers**: `public`/`external`/`internal`/`private`, modifiers used
- **Purpose**: Role in the contract/protocol
- **Input Parameters**: For each parameter - semantics, valid values/ranges, edge cases, where validated
- **Output Parameters**: Return value semantics
- **State Changes**: Modified state variables, balance/allowance changes
- **External Calls**: External contracts called and why
- **Events Emitted**: Events and information conveyed
- **Error Conditions**: When function reverts, error messages
- **Call Flow**: Who can call, what functions call this
- **Dependencies**: Other functions/libraries used
- **Critical Assumptions**: Assumptions made and whether validated

#### Step 2.3: Data Flow Analysis

1. **Money flows**: Entry points → internal processing → exit points. Identify stuck funds risks.
2. **State transitions**: Key state variables, how they change, valid/invalid states.
3. **Parameter flows**: How user inputs flow through, validation at each step, semantic consistency.

#### Step 2.4: Function Dependency Graph

1. **Map call relationships**: Which functions call which, call depth, circular dependencies, unreachable functions.
2. **Identify function groups**: Entry points, internal routing, helpers, admin functions.
3. **Identify critical paths**: Common execution paths, edge cases, native token handling, multi-step operations.

#### Step 2.5: Parameter Semantics & Validation Analysis

**For each function, analyze**:

1. **Input Parameter Semantics**: Business logic meaning, implicit assumptions, edge cases (e.g., `address(0)` for native token, percentage bounds).
2. **Parameter Validation**: Where validated (entry vs internal), consistency across code paths, unvalidated parameters.
3. **Parameter Transformation**: How parameters transform, semantic preservation, validation on transformed values.
4. **Output Parameter Semantics**: Return value meaning, when values are meaningful.

#### Step 2.6: Cross-Function Consistency Check

1. **Compare similar functions**: Consistent validation, edge case handling (e.g., swapExactInput vs swapExactOutput, depositETH vs depositToken).
2. **Check inconsistencies**: Validation rules, error messages, parameter assumptions across similar functions.

#### Step 2.7: Create Understanding Summary

**Create summary with**:
- **Core Functionality**: What the contract does
- **Key Design Decisions**: Important design choices and rationale
- **Critical Assumptions**: Protocol-specific assumptions (e.g., "Native token must be wrapped", "All addresses must exist in registry")
- **Known Validation Gaps**: Identified validation gaps (e.g., "Deadline not validated at entry point")
- **Areas Requiring Deep Audit**: Focus areas for Phase 3

**MANDATORY OUTPUT**: Output complete Phase 2 content including all sections from Steps 2.1-2.7 (architecture, function inventory, data flows, dependency graph, parameter semantics, consistency check, understanding summary). Then **SAVE** to `.audit/blueprints/2_Understanding.md` using `write` tool. After saving, proceed to Phase 3.

---

### Phase 3: Vulnerability Discovery (Senior Auditor)
**Goal**: Find logic errors, state inconsistencies, and DeFi-specific vulnerabilities.

> ⚠️ **MANDATORY FILE OPERATIONS**:
> - At the START: **FIRST STEP** - **MUST** use `read_file` tool to read `.audit/blueprints/0_Setup.md` and `.audit/blueprints/2_Understanding.md` - verify both exist and contain results. If files don't exist or are empty, STOP and re-run previous phases.
> - **OPTIONAL**: If Phase 1 was run, read `.audit/blueprints/1_Automated_Security_Scan.md` for context (this file may not exist if Phase 1 was skipped)
> - **🔴 CRITICAL REFERENCE FILES - READ ONCE AT START**:
>   - **MUST** read `references/DEFI_CHECKLIST.md` ONCE at Phase 3 start - understand the full checklist structure
>   - **MUST** read `references/VULNERABILITY_PATTERNS.md` ONCE at Phase 3 start - understand all 23 patterns
>   - **Reference as needed**: During analysis, refer back to specific sections/patterns as needed (no need to re-read entire files)
> - **CRITICAL**: Reference Phase 2's function inventory, parameter semantics, and data flows when analyzing vulnerabilities - explicitly cite Phase 2 findings in your analysis
> - During analysis: Re-read relevant code sections with Phase 3 focus (vulnerability patterns based on Phase 2 understanding)
> - At the END: Output complete Phase 3 content in conversation (formatted as specified below), then **SAVE** to `.audit/blueprints/3_Vulnerability_Scan.md` using `write` tool
> - **VERIFICATION**: When starting Phase 4, **MUST** read Phase 3 file using `read_file` tool as the FIRST STEP - verify it exists and contains vulnerability findings
> - **DO NOT** proceed to Phase 4 until Phase 3 file is verified to exist and contains findings

> ⚠️ **CRITICAL**: You MUST reference your Phase 2 understanding (function inventory, parameter semantics, data flows) when performing vulnerability discovery. **MUST read Phase 2 results using `read_file` tool as the FIRST STEP**. Do NOT start vulnerability discovery without reading Phase 2 results.

> 🔴 **PHASE 3 SIMPLIFIED WORKFLOW**:
> 
> Phase 3 uses **TWO complementary analysis approaches**:
> 
> 1. **Function-Based Analysis**: Analyze each function individually using Phase 2's function documentation
> 2. **Flow-Based Analysis**: Analyze contract flows/capabilities using Phase 2's data flow and dependency analysis
> 
> **Both approaches MUST**:
> - Reference Phase 2 documentation (function inventory, parameter semantics, known gaps)
> - Reference `references/DEFI_CHECKLIST.md` (protocol-specific checks)
> - Reference `references/VULNERABILITY_PATTERNS.md` (23 vulnerability patterns)
> - Re-read code (do NOT rely solely on Phase 2 documentation)
> - Use existing contract security knowledge to discover unknown issues
> 
> **Why two approaches?**
> - Function-based catches function-level issues (parameter validation, access control, etc.)
> - Flow-based catches cross-function issues (state transitions, multi-step attacks, etc.)
> - Together: Comprehensive coverage of both isolated and systemic vulnerabilities

---

#### Analysis Approach 1: Function-Based Analysis

**Goal**: Analyze each function individually using Phase 2's function documentation to discover vulnerabilities.

**Workflow**:

1. **Reference Phase 2 Function Inventory**: Use Phase 2's complete function inventory (from `.audit/blueprints/2_Understanding.md`) to know which functions exist and their documented semantics.

2. **For EACH function** (public, external, internal, private) from Phase 2 inventory:
   
   a. **Re-read code** for this specific function (do NOT rely solely on Phase 2 documentation)
   
   b. **Reference Phase 2 documentation**:
      - Function purpose and role
      - Parameter semantics (what each parameter means, valid values, edge cases)
      - Known Validation Gaps (from Phase 2)
      - Dependencies and call flow
   
   c. **Apply vulnerability checks** while reading code:
      - **Reference `references/DEFI_CHECKLIST.md`**: Check protocol-specific items relevant to this function
      - **Reference `references/VULNERABILITY_PATTERNS.md`**: Check patterns relevant to this function's operations
      - **Use security knowledge**: Apply general contract security principles to discover unknown issues
   
   d. **Check for**:
      - Parameter validation gaps (compare with Phase 2's parameter semantics)
      - Access control issues
      - Reentrancy vulnerabilities
      - Arithmetic issues (precision loss, overflow)
      - State variable manipulation
      - External call safety
      - Return value handling
      - Edge cases (zero values, max values, empty arrays, address(0))
   
   e. **Document findings**: For each vulnerability found:
      - Function name and line numbers
      - Complete code evidence
      - Severity (Critical/High/Medium/Low)
      - Reference to Phase 2 understanding
      - **Verification Status**: ✅ Complete Evidence / ⚠️ Needs Verification / ❓ Uncertain

3. **Cross-function consistency check**:
   - Compare similar functions (from Phase 2's consistency analysis)
   - Check if validation rules are consistent
   - Document inconsistencies as potential vulnerabilities

---

#### Analysis Approach 2: Flow-Based Analysis

**Goal**: Analyze contract flows/capabilities using Phase 2's data flow and dependency analysis to discover cross-function vulnerabilities.

**Workflow**:

1. **Reference Phase 2 Flow Documentation**: Use Phase 2's data flow analysis and function dependency graph to identify contract capabilities/flows.

2. **Identify Contract Flows** (based on Phase 2 analysis):
   - *Deposit/Withdraw Flow*: `deposit` → `_deposit` → `_mint` → state updates
   - *Swap/Exchange Flow*: `swap` → `_swap` → pool interactions → `_transfer`
   - *Liquidity Flow*: `addLiquidity` → pool interactions → LP token minting
   - *Borrow/Repay Flow*: `borrow` → interest accrual → collateral checks → state updates
   - *Admin Flow*: `setParams` → access control → state changes
   - *Reward Flow*: `claim` → reward calculation → distribution
   - *Multi-step Operations*: Any operations spanning multiple functions

3. **For EACH identified flow**:
   
   a. **Re-read code** for all functions in this flow (trace the complete execution path)
   
   b. **Reference Phase 2 documentation**:
      - Data flow analysis for this capability
      - Function dependency relationships
      - State transitions
      - Known validation gaps across the flow
   
   c. **Apply vulnerability checks** while tracing the flow:
      - **Reference `references/DEFI_CHECKLIST.md`**: Check protocol-specific items relevant to this flow
      - **Reference `references/VULNERABILITY_PATTERNS.md`**: Check patterns relevant to multi-step operations
      - **Use security knowledge**: Apply flow-based security principles (state consistency, atomicity, etc.)
   
   d. **Check for**:
      - State consistency across the flow
      - Reentrancy through multiple functions
      - Slippage protection across multi-step operations
      - Final output validation (unified check after all steps)
      - Fee-on-transfer handling in multi-step flows
      - Native token wrapping/unwrapping consistency
      - Cross-function parameter validation gaps
      - Timing issues (deadline enforcement, interest accrual timing)
      - Flash loan amplification possibilities
      - Multi-path final output validation (all branches checked consistently)
   
   e. **Document findings**: For each vulnerability found:
      - Flow name and affected functions
      - Complete code evidence with execution path
      - Severity (Critical/High/Medium/Low)
      - Reference to Phase 2 flow analysis
      - **Verification Status**: ✅ Complete Evidence / ⚠️ Needs Verification / ❓ Uncertain

4. **Multi-path analysis**:
   - For flows with multiple execution branches (e.g., different pool types, different token types)
   - Check if all branches have consistent security guarantees
   - Document branch inconsistencies as vulnerabilities

---

---

#### Analysis Guidance

**For Function-Based Analysis**:
- Use Phase 2's function inventory to identify all functions to analyze
- For each function, re-read code while referencing Phase 2's parameter semantics
- Apply `references/DEFI_CHECKLIST.md` items relevant to the function
- Apply `references/VULNERABILITY_PATTERNS.md` patterns relevant to the function's operations
- Use security knowledge to discover issues not covered by checklists/patterns

**For Flow-Based Analysis**:
- Use Phase 2's data flow analysis and function dependency graph to identify flows
- For each flow, trace execution path by re-reading code for all functions in the flow
- Apply `references/DEFI_CHECKLIST.md` items relevant to multi-step operations
- Apply `references/VULNERABILITY_PATTERNS.md` patterns relevant to cross-function vulnerabilities
- Use security knowledge to discover flow-level issues (state consistency, atomicity, etc.)

**Both approaches should**:
- Re-read code (do NOT rely solely on Phase 2 documentation)
- Reference Phase 2 understanding (function inventory, parameter semantics, known gaps)
- Reference vulnerability files (DEFI_CHECKLIST.md and VULNERABILITY_PATTERNS.md)
- Document findings with complete code evidence, severity, and verification status

**MANDATORY OUTPUT**: Output complete Phase 3 content in conversation following the format below. Then **IMMEDIATELY SAVE** this content to `.audit/blueprints/3_Vulnerability_Scan.md` using `write` tool. After saving, proceed to Phase 4.

**Phase 3 Output Format**:

```markdown
# Phase 3: Vulnerability Discovery

## Analysis Summary

**Function-Based Analysis**: [Number] functions analyzed, [Number] vulnerabilities found
**Flow-Based Analysis**: [Number] flows analyzed, [Number] vulnerabilities found
**Total Findings**: [Number] vulnerabilities

## 🔴 Critical Findings

### [C-01] <Title>
**Location**: `Contract.sol` : `functionName()` : Lines X-Y
**Analysis Approach**: Function-Based / Flow-Based
**Verification Status**: ✅ Complete Evidence / ⚠️ Needs Verification / ❓ Uncertain

**Description**: [Detailed description of the vulnerability]

**Vulnerable Code**:
```solidity
[Code snippet with line numbers]
```

**Exploit Scenario**: [How an attacker could exploit this]

**Impact**: [Maximum loss, affected users, protocol impact]

**Reference to Phase 2**: [Cite Phase 2 understanding, e.g., "Based on Phase 2 function inventory..."]

[Repeat for all Critical findings]

## 🟠 High Findings

[Same format as Critical]

## 🟡 Medium Findings

[Same format as Critical]

## 🟢 Low Findings

[Same format as Critical]

## 📋 DEFI_CHECKLIST.md Verification Results

**Protocol Type**: [DEX/AMM | Lending | Vault | Router | Staking]

| Section | Items Checked | Pass | Fail | Notes |
|---------|---------------|------|------|-------|
| Universal Checks | [N] | [N] | [N] | [Brief notes] |
| DEX/AMM Specific | [N] | [N] | [N] | [Brief notes] |
| [Other sections] | [N] | [N] | [N] | [Brief notes] |

**Summary**: [Brief summary of checklist verification - keep concise]

## 🔍 VULNERABILITY_PATTERNS.md Verification Results

| Pattern Category | Patterns Checked | Violations Found | Notes |
|-----------------|------------------|------------------|-------|
| Critical (#1-4) | 4 | [N] | [Brief notes] |
| High (#5-7) | 3 | [N] | [Brief notes] |
| Medium (#8-12) | 5 | [N] | [Brief notes] |
| Modern DeFi (#19-23) | 5 | [N] | [Brief notes] |
| [Other categories] | [N] | [N] | [Brief notes] |

**Summary**: [Brief summary of pattern verification - keep concise]

## Analysis Approach Notes

**Function-Based Analysis**:
- Functions analyzed: [List key functions]
- Key findings: [Brief summary]

**Flow-Based Analysis**:
- Flows analyzed: [List key flows]
- Key findings: [Brief summary]
```

**Key Requirements**:
- All findings must be categorized by severity (Critical/High/Medium/Low)
- Each finding must specify which analysis approach found it (Function-Based or Flow-Based)
- DEFI_CHECKLIST.md results should be concise (table format, brief notes)
- VULNERABILITY_PATTERNS.md results should be concise (table format, brief notes)
- Both analysis approaches should reference Phase 2 understanding

---

### Phase 4: Defense & Verification (Lead Dev)
**Goal**: Filter False Positives with Logic/Math and assess real-world impact.

> ⚠️ **MANDATORY FILE OPERATIONS**:
> - At the START: **FIRST STEP** - **MUST** use `read_file` tool to read all previous blueprint files (`.audit/blueprints/0_Setup.md` through `.audit/blueprints/3_Vulnerability_Scan.md`) - verify all exist and contain results. If files don't exist or are empty, STOP and re-run previous phases.
> - During analysis: **Use efficient verification strategy** (see "Efficient Verification Strategy" below) - **NOT all findings require re-reading code**
> - **Key Principle**: Phase 4 is about **verification and impact assessment**, not **re-discovery**. Trust Phase 3's code reading unless there's a specific reason to re-read.
> - At the END: Output complete Phase 4 content in conversation (with verification results for each Phase 3 finding), then **SAVE** to `.audit/blueprints/4_Defense_Verification.md` using `write` tool
> - **VERIFICATION**: When generating final report, **MUST** read Phase 4 file using `read_file` tool as the FIRST STEP - verify it exists and contains verification results
> - **DO NOT** proceed to final report until Phase 4 file is verified to exist

> ⚠️ **PREREQUISITE**: All previous phase files must exist before starting Phase 4. **MUST read all previous phase files using `read_file` tool as the FIRST STEP**. Phase 4 verifies each finding from Phase 3.

> 🔴 **PHASE 4 EXECUTION STEPS**:
> 
> 1. **Read Phase 3 findings**: Load all findings from `.audit/blueprints/3_Vulnerability_Scan.md`
> 2. **Categorize each finding**: Check Phase 3's "Verification Status" marker:
>    - ✅ Complete Evidence → Category A (Logic Verification) - **No code re-reading needed**
>    - ⚠️ Needs Verification → Category B (Targeted Code Review) - **Re-read specific sections only**
>    - ❓ Uncertain → Category C (Deep Re-analysis) - **Re-read relevant sections**
> 3. **Efficiency check**: Count findings by category. Most findings should be Category A (no re-reading).
> 4. **Execute verification** based on category (see "Efficient Verification Strategy" below)
> 5. **Document results**: For each finding, provide verification result with final verdict
> 
> **Expected Efficiency**: 
> - Category A (majority): Logic verification using Phase 3 evidence - fast
> - Category B (some): Targeted code review - moderate time
> - Category C (few): Deep re-analysis - more time, but only for uncertain findings

> 🔴 **EFFICIENT VERIFICATION STRATEGY**:
> 
> Phase 4 should **NOT** re-read code for every finding. Use this triage approach:
> 
> **Category A: Logic Verification (No Code Re-reading Needed)**
> - Phase 3 provided complete code evidence with line numbers
> - Phase 3 analysis is clear and well-documented
> - **Action**: Verify the logic, assess impact, check feasibility - use Phase 3's code evidence
> 
> **Category B: Targeted Code Review (Minimal Re-reading)**
> - Phase 3 marked as ⚠️ **Needs Verification**
> - Phase 3 code evidence is incomplete or unclear
> - **Action**: Re-read ONLY the specific code sections mentioned in Phase 3 (not entire functions)
> - **Focus**: Verify Phase 3's code evidence and check if additional context changes the finding
> 
> **Category C: Deep Re-analysis (Full Code Re-reading)**
> - Phase 3 marked as ❓ **Uncertain**
> - Phase 3 finding seems like potential false positive
> - Need to verify exploit path or check for mitigating factors
> - **Action**: Re-read relevant code sections with verification focus (may need broader context)
> - **Focus**: Check for mitigating factors, verify exploit feasibility, look for protections Phase 3 missed
> 
> **Key Principle**: Phase 4 is about **verification and impact assessment**, not **re-discovery**. Trust Phase 3's code reading unless there's a specific reason to re-read.

**Operational Rules**:
1.  For each finding, define the **Safety Invariant** it violates.
2.  Assess real-world impact: "What's the maximum extractable value?"
3.  Consider: Can this be combined with flash loans for bigger impact?
4.  Check if exploit relies on impossible conditions (e.g., minting infinite USDT).
5.  **Efficiency**: Use Phase 3's code evidence when sufficient; only re-read code when necessary.

**Verification Workflow per Finding**:

**Step 1: Categorize Finding**
> Check Phase 3's finding documentation for "Verification Status" marker:
> - ✅ **Complete Evidence** → **Category A** (Logic Verification) - Use Phase 3's code evidence, no re-reading needed
> - ⚠️ **Needs Verification** → **Category B** (Targeted Code Review) - Re-read specific code sections mentioned in Phase 3
> - ❓ **Uncertain** → **Category C** (Deep Re-analysis) - Re-read relevant code sections with verification focus
> 
> **If Phase 3 didn't mark verification status**: Check code evidence quality:
> - Complete code evidence with line numbers → Category A
> - Incomplete or unclear evidence → Category B
> - Finding seems questionable → Category C

**Step 2: Execute Verification Based on Category**

> **For Category A (Logic Verification)**:
> - **Use Phase 3's code evidence** - do NOT re-read code
> - Define the **Safety Invariant** violated
> - Assess real-world impact using Phase 3's code analysis
> - Check feasibility (gas costs, flash loan amplification)
> - Verify exploit path logic based on Phase 3's description
> - **Output**: Confirm/Dispute with severity justification

> **For Category B (Targeted Code Review)**:
> - **Re-read ONLY the specific code sections** mentioned in Phase 3
> - Verify the code evidence Phase 3 provided
> - Check if additional context changes the finding
> - Define the **Safety Invariant** violated
> - Assess impact and feasibility
> - **Output**: Confirm/Dispute with updated analysis

> **For Category C (Deep Re-analysis)**:
> - **Re-read relevant code sections** with verification focus
> - Check for mitigating factors Phase 3 might have missed
> - Verify exploit path is actually feasible
> - Check if there are code protections not mentioned in Phase 3
> - Define the **Safety Invariant** (if violated)
> - **Output**: Confirm/Dispute/False Positive with detailed justification

**Step 3: Final Verdict**
> For each finding, provide:
> 1. **Verification Category**: A (Logic) / B (Targeted Review) / C (Deep Re-analysis)
> 2. **Code Re-reading Performed**: Yes (Category B/C) / No (Category A - used Phase 3 evidence)
> 3. **Invariant Violated**: Clear statement of what security property is broken
> 4. **Impact Assessment**: Maximum extractable value, affected users, protocol impact
> 5. **Feasibility**: Economic viability, required conditions, complexity
> 6. **Final Verdict**: ✅ Confirmed / ❌ Disputed / ⚠️ False Positive / 🔄 Needs More Info
> 7. **Severity Justification**: Final severity rating with reasoning (may differ from Phase 3 if disputed)
> 
> **Output Format**:
> ```markdown
> ### [Finding ID] Verification
> 
> **Category**: A (Logic Verification) / B (Targeted Review) / C (Deep Re-analysis)
> **Code Re-reading**: No / Yes (specific sections: [list])
> 
> **Invariant Violated**: [statement]
> **Impact**: [assessment]
> **Feasibility**: [analysis]
> 
> **Final Verdict**: ✅ Confirmed / ❌ Disputed / ⚠️ False Positive
> **Severity**: [Critical/High/Medium/Low] (justification: [reasoning])
> ```

#### Severity Classification

| Severity | Impact | Likelihood | Examples |
|----------|--------|------------|----------|
| **Critical** | Direct fund loss, protocol insolvency | High (easy to exploit) | Reentrancy drains, unprotected init, token ID spoofing, Permit2 arbitrary call, multicall msg.value reuse, transient storage leak |
| **High** | Significant damage, partial fund loss | Medium-High | Access control bypass, oracle manipulation, unchecked transfers, Hook DoS, deadline bypass, slippage bypass |
| **Medium** | Conditional impact, requires setup | Medium | Precision loss, front-running, timing issues, callback origin not verified, sweep/dust residue |
| **Low** | Minor issues, unlikely exploitation | Low | Missing events, naming conventions, gas optimizations, hardcoded slippage |
| **Informational** | Best practices, no security impact | N/A | Code quality, documentation gaps |

**MANDATORY OUTPUT**: Output complete Phase 4 content in conversation (formatted as markdown with all verification results). 

**Output Format**:
```markdown
# Phase 4: Defense & Verification

## Verification Summary

| Category | Count | Code Re-reading | Description |
|----------|-------|-----------------|-------------|
| Category A (Logic) | [N] | No | Used Phase 3 evidence |
| Category B (Targeted) | [N] | Yes (specific sections) | Re-read specific code sections |
| Category C (Deep) | [N] | Yes (broader context) | Full re-analysis |

**Total Findings Verified**: [N]
**Efficiency**: [X]% of findings verified using Phase 3 evidence (no code re-reading)

## Verification Results

### [Finding ID] Verification
[Follow format from Step 3 above]

[Repeat for all findings]
```

Then **IMMEDIATELY SAVE** this content to `.audit/blueprints/4_Defense_Verification.md` using `write` tool. After saving, proceed to generate the final merged report.

---

## 🧠 Core Principles
1.  **Sequential Execution**: ⚠️ **CRITICAL** Execute phases one at a time. Complete Phase N fully (including outputting content and **SAVING to file using `write` tool**) before starting Phase N+1. Do NOT combine multiple phases in a single execution.
2.  **File-Based Workflow**: ⚠️ **CRITICAL** Each phase must be **SAVED by AI using `write` tool** to a separate file. **ALWAYS read previous phase files using `read_file` tool as the FIRST STEP** when starting a new phase. **ALWAYS verify files exist and contain content** before proceeding. This ensures continuity and forces careful review of previous findings.
3.  **Code Re-Reading**: ⚠️ **CRITICAL** Re-read relevant code files for each phase. Each phase has different focus (architecture, security patterns, deep understanding, vulnerability discovery, verification), so code must be re-read with that focus in mind.
4.  **Understand Before Auditing**: ⚠️ **NEW** Complete Phase 2 (Contract Understanding) before vulnerability discovery. You cannot effectively audit what you don't understand.
5.  **Context Groups**: Audit capabilities, not lines of code. Use your Phase 2 function inventory to group related functions.
6.  **Parameter Semantics First**: ⚠️ **NEW** Understand what each parameter means before checking validation. Use your Phase 2 parameter semantics analysis.
7.  **DeFi-Specific Thinking**: Always ask "What if this is part of a flash loan? What if the price is manipulated?"
8.  **Stateful & Append-Only**: Never delete Phase 3 findings. Only refine or dispute them in Phase 4.
9.  **Invariant-Based Verification**: Every critical function should have a clear invariant it must maintain. Use your Phase 2 understanding to identify invariants.
10. **Internal Function Parity**: ⚠️ **NEW** Internal functions deserve the same scrutiny as public functions. Use your Phase 2 function inventory to ensure all functions are audited.
11. **Error Handling**: ⚠️ **NEW** If a required blueprint file doesn't exist or is empty when starting a new phase, STOP immediately and re-run the previous phase. Do NOT proceed without verification.
12. **Tool Availability**: ⚠️ **NEW** If automated tools (Slither, Mythril) are unavailable, perform manual pattern-based analysis instead. Document findings with `[MANUAL]` tag instead of `[AUTO]`.

---

## 📤 Final Deliverable (Mandatory)

After completing Phase 4, you **MUST** finalize and output the Audit Report.

### Phase Final: Report Generation

> ⚠️ **MANDATORY FILE OPERATIONS**:
> - **MUST** use `read_file` tool to read `.audit/blueprints/3_Vulnerability_Scan.md` and `.audit/blueprints/4_Defense_Verification.md` (primary sources)
> - **OPTIONAL**: Reference `.audit/blueprints/0_Setup.md`, `.audit/blueprints/1_Automated_Security_Scan.md`, and `.audit/blueprints/2_Understanding.md` for context
> - Verify all required files exist before generating final report

1.  **MANDATORY**: Use `read_file` tool to read `.audit/blueprints/3_Vulnerability_Scan.md` and `.audit/blueprints/4_Defense_Verification.md` (primary sources)
2.  **OPTIONAL**: Reference `.audit/blueprints/0_Setup.md`, `.audit/blueprints/1_Automated_Security_Scan.md`, and `.audit/blueprints/2_Understanding.md` for context (protocol type, architecture, understanding summary)
3.  **FOCUS**: The final report should be concise and professional, similar to third-party audit reports. Focus on findings and verification results, not detailed analysis processes.
4.  **Structure**: Follow the structure defined in `resources/audit_report_template.md`. Key requirements:
    - **Executive Summary**: Keep it concise - only severity counts and key findings summary. Do NOT include detailed Phase 3/4 analysis statistics.
    - **Detailed Findings**: Each finding should include:
      - Clear description, vulnerable code, impact, exploit scenario, and recommendation
      - Do NOT include detailed analysis context, verification categories, or code re-reading status
      - Keep findings concise and focused on the vulnerability itself
    - **Appendix**: MUST include Phase 3 verification results:
      - DEFI_CHECKLIST.md verification table (from Phase 3 output)
      - VULNERABILITY_PATTERNS.md verification table (from Phase 3 output)
    
    > **Note**: The report should be professional and concise, focusing on findings rather than analysis methodology details.
5.  **Extract Data**: From Phase 3 and Phase 4 outputs, extract:
    *   **Findings**: All confirmed vulnerabilities with their descriptions, impacts, and recommendations
    *   **Verification Results**: DEFI_CHECKLIST.md and VULNERABILITY_PATTERNS.md verification tables from Phase 3 output
    *   **Do NOT include**: Detailed analysis statistics, verification categories, or code re-reading details in the main report
6.  **Finalize**: Review and clean up the report to ensure:
    *   All confirmed findings from Phase 3/4 are included (exclude disputed/false positives unless relevant)
    *   Each finding is concise and professional
    *   The severity count table is accurate
    *   Phase 3 verification results (DEFI_CHECKLIST and VULNERABILITY_PATTERNS tables) are included in Appendix
    *   Report format matches third-party audit report style (concise, professional, focused on findings)
7.  **Output**: Output complete final report in conversation (formatted as markdown following the structure above)
8.  **SAVE**: **IMMEDIATELY SAVE** this content to `.audit/Audit-Report.md` using `write` tool. This is the final comprehensive audit report focusing on vulnerabilities (Phase 3) and their verification (Phase 4).

---

## 📚 Reference: Common DeFi Attack Patterns

For quick reference during audit:

| Attack | Typical Target | Key Indicators |
|--------|---------------|----------------|
| Flash Loan Attack | Price oracles, yield farming | Spot price used, single-block manipulation possible |
| Sandwich Attack | DEX swaps | No slippage protection, predictable transactions |
| Reentrancy | Any external call before state update | `call()`, `transfer()`, callbacks before state change |
| **Read-Only Reentrancy** | Curve/Balancer integrations | View function reads state during callback |
| **ERC Token Callback** | ERC777/721/1155 receivers | `tokensReceived`, `onERC721Received` without reentrancy guard |
| First Depositor | Vaults, share-based pools | `shares = deposit * totalShares / totalAssets` with 0 initial |
| **Donation Attack** | ERC4626 Vaults | Direct token transfer inflates share price |
| Oracle Manipulation | Lending, leveraged positions | `getReserves()`, TWAP window too short |
| Token Approval Front-run | Any `approve()` | Changing approval from non-zero to non-zero |
| Governance Attack | DAOs, parameter changes | Low quorum, flash loan votes |
| Token ID Spoofing | DEX with token registries | Mapping returns 0 for unregistered, colliding with token ID 0 |
| **Unsafe Downcast** | Any type conversion | `uint256` -> `uint128` without bounds check |
| **Force-feeding ETH** | Contracts using `balance` | `selfdestruct` can force ETH, breaking `address(this).balance` checks |
| **Signature Replay** | Permit, meta-tx, multi-chain | Missing `chainId`, `nonce`, or contract address in signed data |
