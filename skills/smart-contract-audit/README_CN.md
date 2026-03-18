# DeFi 智能合约审计 Skill - 核心指南

**版本**: v2.8.0  
**更新日期**: 2026-01

## 📋 目录

- [核心理念](#核心理念)
- [审计流程](#审计流程)
- [预期输出](#预期输出)
- [关键资源](#关键资源)
- [使用指南](#使用指南)
- [调整建议](#调整建议)

---

## 🎯 核心理念

### 1. **理解优先原则**
在发现漏洞之前，必须先深入理解合约的架构、函数目的、数据流和参数语义。**Phase 2 (Contract Understanding) 是强制性的**，不能跳过。

### 2. **双分析方式**
Phase 3 采用两种互补的分析方式：
- **Function-Based（函数级分析）**：逐个函数分析，发现函数级别的漏洞
- **Flow-Based（流程级分析）**：按业务流程分析，发现跨函数的系统性漏洞

### 3. **文件化工作流**
每个阶段必须：
- 完成分析后立即输出完整内容
- 使用 `write` 工具保存到 `.audit/blueprints/` 目录
- 下一阶段开始时，必须先读取上一阶段的文件进行验证

### 4. **参考文件驱动**
Phase 3 必须参考两个关键文件：
- `references/DEFI_CHECKLIST.md`：协议特定的漏洞检查清单
- `references/VULNERABILITY_PATTERNS.md`：23 个漏洞模式（包括现代 DeFi 模式）

### 5. **高效验证策略**
Phase 4 采用分类验证策略，避免不必要的代码重读：
- **Category A**：使用 Phase 3 的证据进行逻辑验证（无需重读代码）
- **Category B**：针对需要验证的发现进行定向代码审查
- **Category C**：对不确定的发现进行深度重新分析

---

## 🔄 审计流程

### 整体流程概览

```
Phase 0 (架构师) → Phase 1 (自动化扫描) [可选] → Phase 2 (合约理解) [强制] 
→ Phase 3 (漏洞发现) → Phase 4 (验证与评估) → Final Report (最终报告)
```

### 详细阶段说明

#### **Phase 0: 架构与协议分类**

**目标**：识别协议类型、映射架构、验证文档

**关键任务**：
- 识别协议类型（DEX/AMM、Lending、Vault、Router、Staking 等）
- 映射合约架构和关键合约
- 验证文档完整性

**输出**：`.audit/blueprints/0_Setup.md`

---

#### **Phase 1: 自动化安全扫描** ⚠️ **可选**

**目标**：使用静态分析工具快速发现常见漏洞

**决策点**：
- **如果工具可用**（Slither、Mythril）：运行 Phase 1
- **如果工具不可用**：**跳过 Phase 1**，直接进入 Phase 2

**注意**：Phase 3 会进行全面的漏洞发现，无论 Phase 1 是否运行。Phase 1 只是时间节省工具，不是必需的。

**输出**：`.audit/blueprints/1_Automated_Security_Scan.md`（如果运行）

---

#### **Phase 2: 合约理解** ⚠️ **强制**

**目标**：深入理解合约架构、函数目的、数据流和参数语义

**关键步骤**：

1. **架构理解**：读取整个合约，识别设计模式、继承关系
2. **函数清单**：为每个函数（public/external/internal/private）创建详细文档
3. **数据流分析**：追踪资金流、状态转换、参数流
4. **函数依赖图**：映射函数调用关系，识别关键路径
5. **参数语义分析**：分析每个参数的语义、验证位置、转换过程
6. **一致性检查**：比较相似函数的一致性
7. **理解摘要**：创建核心功能、关键假设、已知验证缺口的摘要

**这是最全面的代码阅读阶段**，必须读取每个函数、每个修饰符、每个状态变量。

**输出**：`.audit/blueprints/2_Understanding.md`

---

#### **Phase 3: 漏洞发现**

**目标**：发现逻辑错误、状态不一致和 DeFi 特定漏洞

**关键要求**：
- **必须读取**：Phase 0 和 Phase 2 的输出文件
- **必须读取**：`references/DEFI_CHECKLIST.md` 和 `references/VULNERABILITY_PATTERNS.md`（在 Phase 3 开始时读取一次）
- **必须参考**：Phase 2 的函数清单和参数语义
- **必须重读代码**：不能仅依赖 Phase 2 文档

**双分析方式**：

**1. Function-Based Analysis（函数级分析）**
- 基于 Phase 2 的函数文档，逐个函数分析
- 检查参数验证、访问控制、重入、算术问题等
- 发现函数级别的漏洞

**2. Flow-Based Analysis（流程级分析）**
- 基于 Phase 2 的数据流分析，按业务流程分析
- 识别关键流程（Deposit/Withdraw、Swap、Liquidity、Borrow/Repay、Admin、Reward）
- 检查状态一致性、跨函数重入、多步骤操作的滑点保护等
- 发现跨函数的系统性漏洞

**输出格式**：
- 按严重性分类的漏洞（Critical/High/Medium/Low）
- 每个漏洞包含：位置、描述、代码证据、影响、验证状态
- DEFI_CHECKLIST.md 验证结果表格（简洁）
- VULNERABILITY_PATTERNS.md 验证结果表格（简洁）

**输出**：`.audit/blueprints/3_Vulnerability_Scan.md`

---

#### **Phase 4: 验证与影响评估**

**目标**：使用不变量验证过滤误报，评估真实世界影响

**高效验证策略**：

根据 Phase 3 的"验证状态"标记，将发现分为三类：

- **Category A（逻辑验证）**：
  - Phase 3 提供了完整的代码证据
  - **无需重读代码**，使用 Phase 3 的证据进行逻辑验证

- **Category B（定向审查）**：
  - Phase 3 标记为 ⚠️ Needs Verification
  - **重读特定代码段**（仅 Phase 3 提到的部分）

- **Category C（深度重新分析）**：
  - Phase 3 标记为 ❓ Uncertain
  - **重读相关代码段**，检查 Phase 3 可能遗漏的缓解因素

**关键原则**：Phase 4 是关于**验证和影响评估**，不是**重新发现**。信任 Phase 3 的代码阅读，除非有特定原因需要重读。

**输出**：
- 每个发现的验证结果（确认/争议/误报）
- 不变量违反说明
- 影响评估（最大可提取价值）
- 可行性分析
- 验证摘要统计（Category A/B/C 数量和效率）

**输出**：`.audit/blueprints/4_Defense_Verification.md`

---

#### **Phase Final: 最终报告生成**

**目标**：生成专业的第三方审计报告风格的最终报告

**关键要求**：
- 报告应简洁、专业，聚焦于发现的问题
- **不包含**详细的分析过程统计
- **必须包含**：
  - 执行摘要（严重性统计、关键发现摘要）
  - 详细发现（每个漏洞的描述、影响、修复建议）
  - 附录中的验证结果表格：
    - DEFI_CHECKLIST.md 验证结果
    - VULNERABILITY_PATTERNS.md 验证结果

**输出**：`.audit/Audit-Report.md`

---

## 📤 预期输出

### 文件结构

```
.audit/
├── blueprints/
│   ├── 0_Setup.md                    # Phase 0: 架构与协议分类
│   ├── 1_Automated_Security_Scan.md  # Phase 1: 自动化扫描（可选）
│   ├── 2_Understanding.md            # Phase 2: 合约理解（强制）
│   ├── 3_Vulnerability_Scan.md      # Phase 3: 漏洞发现
│   └── 4_Defense_Verification.md     # Phase 4: 验证与评估
└── Audit-Report.md                   # 最终审计报告
```

### Phase 2 输出内容

必须包含以下所有部分：
- 架构分析
- 完整函数清单（每个函数的详细文档）
- 数据流分析
- 函数依赖图
- 参数语义分析
- 跨函数一致性检查
- 理解摘要（核心功能、关键假设、已知验证缺口）

### Phase 3 输出格式

```markdown
# Phase 3: Vulnerability Discovery

## Analysis Summary
- Function-Based Analysis: [N] functions analyzed, [N] vulnerabilities found
- Flow-Based Analysis: [N] flows analyzed, [N] vulnerabilities found

## 🔴 Critical Findings
### [C-01] <Title>
- Location, Analysis Approach, Verification Status
- Description, Vulnerable Code, Impact

## 📋 DEFI_CHECKLIST.md Verification Results
[简洁的表格格式]

## 🔍 VULNERABILITY_PATTERNS.md Verification Results
[简洁的表格格式]
```

### Phase 4 输出格式

```markdown
# Phase 4: Defense & Verification

## Verification Summary
- Category A/B/C 统计
- 效率指标（使用 Phase 3 证据的百分比）

## Verification Results
### [Finding ID] Verification
- Category, Code Re-reading status
- Invariant Violated, Impact, Feasibility
- Final Verdict, Severity
```

### 最终报告格式

专业的第三方审计报告风格：
- 执行摘要（严重性统计、关键发现）
- 协议概览
- 详细发现（每个漏洞的描述、影响、修复建议）
- 修复建议（按优先级分类）
- 附录：
  - 验证结果表格（DEFI_CHECKLIST 和 VULNERABILITY_PATTERNS）
  - 文件清单
  - 方法论说明
  - 漏洞分类标准

---

## 📚 关键资源

### 参考文件

| 资源 | 路径 | 用途 |
|------|------|------|
| **审计报告模板** | `resources/audit_report_template.md` | 最终报告的模板结构 |
| **漏洞模式** | `references/VULNERABILITY_PATTERNS.md` | 23 个漏洞模式（包括现代 DeFi 模式） |
| **DeFi 检查清单** | `references/DEFI_CHECKLIST.md` | 协议特定的漏洞检查清单 |

### 漏洞模式覆盖

**经典模式**（#1-18）：
- Reentrancy、Mapping Default Values、Unprotected Init、Arbitrary Call
- Missing Access Control、Unchecked Returns、Oracle Manipulation
- Precision Loss、First Depositor Attack、Front-Running
- 等等...

**现代 DeFi 模式**（#19-23）：
- #19: Transient Storage Collision (EIP-1153)
- #20: Hook Denial of Service (Uniswap V4)
- #21: Multicall msg.value Reuse
- #22: Permit2 Universal Approval Exploitation
- #23: Deadline Bypass / Hardcoded Deadline

### DeFi 检查清单覆盖

- 📋 Universal Checks（所有协议）
- 🔄 DEX / AMM Specific（包括 V3+ 集中流动性、V4 Hook 安全）
- 💰 Lending Protocol Specific
- 🏦 Vault / Yield Specific
- 🌉 Router / Aggregator Specific（包括滑点保护、闪存会计、调用注入）
- 🔐 Staking Specific

---

## 🚀 使用指南

### 执行顺序

**⚠️ 关键**：必须**按顺序执行**，一个阶段一个阶段完成。

1. **完成 Phase 0** → 输出并保存 → 验证文件存在
2. **决定是否运行 Phase 1** → 如果运行，输出并保存 → 如果跳过，直接进入 Phase 2
3. **完成 Phase 2** → 输出并保存 → 验证文件存在（**这是强制阶段**）
4. **完成 Phase 3** → 输出并保存 → 验证文件存在
5. **完成 Phase 4** → 输出并保存 → 验证文件存在
6. **生成最终报告** → 输出并保存

### 关键原则

**DO（必须做）**：
- ✅ 一个阶段完全完成后再开始下一个
- ✅ 每个阶段完成后立即输出完整内容
- ✅ 使用 `write` 工具立即保存到文件
- ✅ 开始新阶段时，先读取上一阶段的文件进行验证
- ✅ 每个阶段重新读取代码（不同阶段有不同的关注点）
- ✅ Phase 3 开始时，读取 DEFI_CHECKLIST.md 和 VULNERABILITY_PATTERNS.md

**DON'T（不要做）**：
- ❌ 一次性读取所有文件并一起分析
- ❌ 在单个执行中输出所有阶段
- ❌ 在完成前面的阶段之前跳到后面的阶段（例外：Phase 1 可以跳过）
- ❌ 开始新阶段时跳过读取上一阶段的文件（例外：Phase 1 文件是可选的）
- ❌ 跳过为每个阶段重新读取代码文件
- ❌ 将多个阶段合并到一个输出中

---

## 🔧 调整建议

### 如果需要调整 Skill

#### 1. **添加新的漏洞模式**

编辑 `references/VULNERABILITY_PATTERNS.md`：
- 添加新的模式编号和描述
- 更新"快速检测清单"
- Phase 3 会自动使用新模式

#### 2. **添加新的协议类型检查**

编辑 `references/DEFI_CHECKLIST.md`：
- 添加新的协议特定部分
- 添加检查项
- Phase 3 会根据协议类型自动使用

#### 3. **调整 Phase 2 的详细程度**

编辑 `SKILL.md` 的 Phase 2 部分：
- 调整函数文档的必需字段
- 修改步骤描述
- 注意：Phase 3 依赖 Phase 2 的输出，确保不破坏依赖关系

#### 4. **调整 Phase 3 的分析方式**

当前是 Function-Based + Flow-Based 双分析方式。如果需要：
- 可以调整两种方式的执行顺序
- 可以添加新的分析方式
- 注意：两种方式都必须参考 DEFI_CHECKLIST.md 和 VULNERABILITY_PATTERNS.md

#### 5. **调整 Phase 4 的验证策略**

当前使用 Category A/B/C 分类。如果需要：
- 可以调整分类标准
- 可以修改验证工作流
- 注意：保持效率原则，避免不必要的代码重读

#### 6. **调整最终报告格式**

编辑 `resources/audit_report_template.md`：
- 修改报告结构
- 调整详细程度
- 注意：保持专业、简洁的第三方审计报告风格

### 常见调整场景

**场景 1：需要添加新的 DeFi 协议类型**
- 在 `DEFI_CHECKLIST.md` 中添加新的协议部分
- 在 Phase 0 中添加协议识别逻辑

**场景 2：发现新的漏洞模式**
- 在 `VULNERABILITY_PATTERNS.md` 中添加新模式
- 更新检测方法

**场景 3：需要更详细的 Phase 2 输出**
- 在 Phase 2 的步骤中添加更多字段要求
- 注意：这可能会增加 Phase 2 的执行时间

**场景 4：需要更简洁的最终报告**
- 在 `audit_report_template.md` 中进一步简化
- 移除不必要的部分

---

## 💡 核心设计决策

### 为什么 Phase 2 是强制的？

**原因**：
1. **避免上下文过载**：将理解阶段和漏洞发现阶段分离，避免 AI 在单个上下文中处理过多信息
2. **系统性理解**：强制进行完整的函数清单和参数语义分析，确保不遗漏关键信息
3. **为 Phase 3 提供结构**：Phase 3 可以基于 Phase 2 的结构化输出进行高效的漏洞发现

### 为什么 Phase 3 使用双分析方式？

**原因**：
1. **互补覆盖**：Function-Based 发现函数级问题，Flow-Based 发现跨函数问题
2. **避免遗漏**：两种方式结合，确保既发现孤立漏洞，也发现系统性漏洞
3. **效率平衡**：Function-Based 可以快速扫描，Flow-Based 可以深入分析关键流程

### 为什么 Phase 4 使用分类验证？

**原因**：
1. **避免重复工作**：Phase 3 已经读取代码，Phase 4 不应该重复读取
2. **效率优化**：对于有完整证据的发现，只需逻辑验证
3. **聚焦重点**：只对需要验证的发现进行代码重读

### 为什么最终报告要简洁？

**原因**：
1. **专业标准**：第三方审计报告通常简洁、聚焦于发现
2. **可读性**：过多的分析细节会降低报告的可读性
3. **实用性**：用户主要关心漏洞和修复建议，而不是分析过程

---

## 📝 总结

这个 Skill 的核心是：
1. **理解优先**：Phase 2 强制深入理解
2. **双分析方式**：Function-Based + Flow-Based 确保全面覆盖
3. **参考文件驱动**：DEFI_CHECKLIST 和 VULNERABILITY_PATTERNS 确保系统性检查
4. **高效验证**：Phase 4 避免不必要的重复工作
5. **专业输出**：最终报告简洁、专业、聚焦于发现

**关键成功因素**：
- 严格按照顺序执行各阶段
- 每个阶段完成后立即保存文件
- Phase 3 必须参考 Phase 2 的输出
- Phase 3 必须使用参考文件（DEFI_CHECKLIST 和 VULNERABILITY_PATTERNS）
- 保持文件化工作流，确保连续性

---

*本文档基于 DeFi Smart Contract Audit Skill v2.8.0*
