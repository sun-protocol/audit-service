# DeFi Protocol Audit Checklist

> Comprehensive checklist organized by protocol type.
> **Primary Use:** Phase 3 (Vulnerability Discovery) - Step 3.3 DeFi-Specific Vulnerability Scan.
> **Secondary Use:** Phase 1 (Automated Security Scan) - Manual pattern-based analysis if automated tools unavailable.
> **Reference:** Use Phase 2 (Contract Understanding) function inventory and parameter semantics when checking these items.

---

## 📋 Universal Checks (All Protocols)

### Access Control
- [ ] All admin functions have proper access modifiers (`onlyOwner`, `onlyAdmin`)
- [ ] Ownership transfer is 2-step (propose → accept)
- [ ] Critical parameter changes have timelock
- [ ] No unprotected `initialize()` function
- [ ] `selfdestruct` / `delegatecall` properly protected

### Reentrancy
- [ ] CEI pattern followed (Checks-Effects-Interactions)
- [ ] `nonReentrant` modifier on state-changing external functions
- [ ] Cross-function reentrancy considered (multiple functions share state)

### Token Handling
- [ ] Use `SafeERC20` for all token operations
- [ ] Handle fee-on-transfer tokens (use `balanceAfter - balanceBefore`)
- [ ] Handle rebasing tokens if applicable
- [ ] No assumption about token decimals (query dynamically)
- [ ] `address(0)` handled explicitly for native currency

### Arithmetic
- [ ] No precision loss (multiply before divide)
- [ ] Rounding direction favors protocol (rounds down for withdrawals)
- [ ] Safe math for Solidity < 0.8.0
- [ ] No overflow in unchecked blocks

### Input Validation
- [ ] All external inputs validated
- [ ] Array length checks to prevent DoS
- [ ] Zero address checks where applicable
- [ ] Reasonable bounds on numeric inputs

---

## 🔄 DEX / AMM Specific

### Token Registry
- [ ] **Token existence validated before swap** (mapping default value check!)
- [ ] Token IDs/indices verified against registry
- [ ] Pool address validated from factory/registry
- [ ] Path tokens validated at each hop

### Swap Mechanics
- [ ] Slippage protection enforced (`amountOutMin`)
- [ ] **`amountOutMin` cannot be set to 0** (or has explicit warning)
- [ ] **`amountInMax` enforced for exactOutput swaps**
- [ ] Deadline parameter actually checked
- [ ] Recipient address validated
- [ ] Fee calculation correct and no overflow

### Slippage Parameters
- [ ] **Slippage controlled by user**, not hardcoded in contract
- [ ] **Internal swap calls calculate slippage properly** (e.g., vault strategies calling DEX)
- [ ] **Slippage calculation uses TWAP/oracle**, not manipulable spot price
- [ ] Reasonable slippage bounds (not too tight causing DoS, not too loose allowing MEV)

### Price / Oracle
- [ ] TWAP used instead of spot price (flash loan resistant)
- [ ] Oracle staleness check (timestamp validation)
- [ ] Price manipulation resistance during swaps
- [ ] Reserve ratios cannot be manipulated in single tx

### Liquidity
- [ ] LP token minting/burning calculations correct
- [ ] No inflation attack on first deposit
- [ ] Imbalanced liquidity adds handled properly
- [ ] Remove liquidity doesn't leave dust

### 💧 Concentration & Range Logic (Uniswap V3+ Pattern)
- [ ] **Tick Initialization DoS**: Check if `mint` or `swap` can cause gas exhaustion by iterating through too many uninitialized ticks
- [ ] **Liquidity Gross Overflow**: Ensure single tick's `liquidityGross` cannot exceed `uint128` max, preventing permanent pool lock
- [ ] **In-range vs Out-of-range State**: Verify state updates (`feeGrowthGlobal`) and swap remaining amount calculations are correct when price crosses ticks
- [ ] **Position boundary validation**: Ensure `tickLower < tickUpper` and both are multiples of `tickSpacing`
- [ ] **Fee growth accounting**: Verify `feeGrowthInside` calculation handles tick crossing correctly

### 🧩 Hook & Callback Security (V4 / Singleton Pattern)
- [ ] **Hook Return Value Validation**: For V4-style hooks, strictly verify returned selector; incorrect returns may bypass pool logic
- [ ] **Callback Origin Verification**: All `uniswapV3SwapCallback` or `lockAcquired` must verify `msg.sender` is expected Pool/Vault address
- [ ] **No-Op Hook Detection**: Check if hooks can return 0 or no-op under certain conditions, allowing transactions to execute without intended restrictions
- [ ] **Hook permission flags**: Verify hook address encodes correct permission bits (beforeSwap, afterSwap, etc.)
- [ ] **Reentrancy through hooks**: Hooks may call back into pool; ensure state is consistent

---

## 💰 Lending Protocol Specific

### Collateral
- [ ] Collateral factor bounds checked (not > 100%)
- [ ] Collateral valuation uses secure oracle
- [ ] Collateral cannot be withdrawn while borrowed
- [ ] Cross-collateral calculated correctly

### Borrowing
- [ ] Borrow limit enforced before and after borrow
- [ ] Interest accrues before any state change
- [ ] Borrow cannot exceed available liquidity
- [ ] Health factor calculated correctly

### Liquidation
- [ ] Liquidation threshold < collateral factor
- [ ] Self-liquidation prevented or handled
- [ ] Liquidation bonus reasonable (no drain)
- [ ] Partial liquidation calculated correctly
- [ ] Underwater positions can always be liquidated

### Interest
- [ ] Interest rate model bounded
- [ ] Accrual frequency reasonable
- [ ] Utilization rate calculated correctly
- [ ] No overflow in long-term interest calculation

---

## 🏦 Vault / Yield Specific

### Share Calculation
- [ ] **First depositor attack mitigated** (virtual shares or minimum)
- [ ] Share price cannot be manipulated by donation
- [ ] Rounding favors vault (down on deposit, up on withdraw)
- [ ] Total assets includes pending rewards

### Strategy
- [ ] Strategy changes have timelock
- [ ] Emergency withdrawal path available
- [ ] Harvest does not favor specific users
- [ ] Slippage on strategy actions

### Rewards
- [ ] Reward calculation overflow-safe
- [ ] No double-claiming rewards
- [ ] Reward distribution gas-bounded
- [ ] Staking snapshot timing correct

---

## 🌉 Router / Aggregator Specific

### Path Validation
- [ ] **All tokens in path validated against pools**
- [ ] Each hop uses correct pool
- [ ] No arbitrary pool/token injection
- [ ] Path length bounded

### Multi-Protocol
- [ ] Each external call validated
- [ ] Return values from external protocols checked
- [ ] Deadline enforced through entire route

### Slippage Protection
- [ ] **Slippage across entire path enforced** (`amountOutMin` at final hop)
- [ ] **⚠️ UNIFIED FINAL CHECK**: After ALL execution paths complete (after routing loop), router MUST verify final output `amountsOut[last] >= amountOutMin` regardless of last pool type (V1/V2/V3/Stable). Do NOT rely solely on external protocol checks.
- [ ] **Intermediate hop outputs validated** (not just final result)
- [ ] **Cumulative slippage across n-hops considered**
- [ ] **Quote vs execution deviation handled** (price may change between quote and swap)
- [ ] **`amountOutMin` cannot be 0** for user-facing functions
- [ ] Per-hop slippage or aggregated slippage strategy documented

### Funds Handling
- [ ] Leftover tokens returned to user
- [ ] Native currency (ETH/TRX) wrapped/unwrapped correctly
- [ ] No stuck funds in router
- [ ] Recipient address from caller, not parameter

### 🌊 Liquidity Fragmentation & Dust
- [ ] **Partial Fill Residue**: When aggregator splits across multiple paths, if one path fails (e.g., slippage), are remaining funds correctly refunded or rerouted?
- [ ] **Sweep Enforcement**: Does router enforce `sweepToken`? Ensure no user assets remain in contract to be "picked up" by next caller
- [ ] **Minimum output threshold**: Dust amounts below gas cost should be handled explicitly

### ⚡ Flash Accounting & Transient Storage
- [ ] **Transient Storage (EIP-1153) Reset**: If using `TSTORE`, ensure state is cleared at transaction end; uncleared state may cause next Permit2/Swap to misuse previous authorization
- [ ] **Native Wrapping Consistency**: Ensure `WETH.deposit{value: amount}()` amount matches actual `msg.value`, preventing double-charge in Permit2 batch transactions
- [ ] **Flash loan callback accounting**: Verify borrowed amounts are correctly tracked and repaid within same transaction

### 🛡️ Call Injection & Permissions
- [ ] **Arbitrary Call in Dispatcher**: Does aggregator's `execute` logic restrict `target` address? Prohibit user-supplied arbitrary contract calls to prevent draining router-approved tokens
- [ ] **Permit2 Nonce Replay**: Verify router correctly handles nonce and deadline when calling Permit2
- [ ] **Signature malleability**: Ensure permit signatures cannot be replayed or modified
- [ ] **Approved token scope**: Router should only interact with explicitly approved tokens per transaction

---

## 🔐 Staking Specific

### Reward Distribution
- [ ] Reward per token calculation precision
- [ ] Rewards accrue before any stake/unstake
- [ ] No reward dilution through flash stake
- [ ] Reward update on all entry/exit points

### Lock Periods
- [ ] Lock period enforced on withdraw
- [ ] Early withdrawal penalty calculated correctly
- [ ] Lock cannot be extended maliciously
- [ ] Penalty distribution fair

### Governance
- [ ] Voting power snapshot at correct time
- [ ] No flash loan voting
- [ ] Delegation tracked correctly
- [ ] Quorum reasonable

---

## ⚠️ Common Gotchas Quick Reference

| Issue | How to Miss It | How to Find It |
|-------|---------------|----------------|
| Mapping default 0 | Assume key exists | "What if key never set?" |
| address(0) dual use | Native currency vs not-found | Check all address(0) paths |
| ID = 0 valid | First item has ID 0 | Check if 0 is valid state |
| Stale oracle | Works in tests | Check timestamp validation |
| First depositor | Works with 1+ depositors | Test with empty vault |
| Reentrancy | No obvious callback | Check ERC777, receive(), external calls |
| `amountOutMin = 0` | User/contract sets 0 | Check if 0 slippage allowed → sandwich attack |
| Hardcoded slippage | Works in stable market | Volatile market → DoS or excessive loss |
| Spot price slippage | Works without flashloan | Flash loan manipulates spot → wrong slippage calc |
| Multi-hop slippage | Final output looks ok | Intermediate hops manipulated, final passes |
| Multi-protocol final check | Only last pool checks | Router must verify final output after ALL paths, regardless of pool type |

---

## ✅ Phase 3 Completion Checklist

Before completing Phase 3 (Vulnerability Discovery):

- [ ] All items above checked for applicable protocol type
- [ ] Phase 2 function inventory referenced when analyzing vulnerabilities
- [ ] Phase 2 parameter semantics used to identify validation gaps
- [ ] Each finding explicitly references Phase 2 understanding
- [ ] All findings documented in `.audit/blueprints/3_Vulnerability_Scan.md`
- [ ] Findings ready for Phase 4 verification

---

*Checklist for DeFi Smart Contract Audit Skill*
