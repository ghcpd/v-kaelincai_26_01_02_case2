# Known Issues

This document describes the intentionally planted flaky behavior bugs in the Marketing Lottery System.

## Issue Type

**Flaky Behavior** - Same input gives inconsistent outputs; non-deterministic test failures.

## Bug #1: Random Number Generation Without Fixed Seed

### Description

The lottery system uses `random.random()` to generate random numbers for prize determination, but never initializes the random seed. This causes non-deterministic behavior where identical inputs produce different outputs across test runs.

### Location

- **File**: [src/lottery.py](src/lottery.py)
- **Class**: `LotterySystem`
- **Method**: `__init__()` (Line ~80-85)
- **Method**: `draw()` (Line ~140-145)

### Root Cause

```python
# Current (buggy) code in __init__:
def __init__(self, prize_pool: Optional[PrizePool] = None):
    self.prize_pool = prize_pool or PrizePool()
    self.ip_win_counts: Dict[str, int] = {}
    
    # BUG: No random seed initialization
    # Should have: random.seed(some_fixed_value)
```

```python
# Current (buggy) code in draw():
def draw(self, user: User) -> tuple[PrizeType, str]:
    # ... eligibility checks ...
    
    # BUG: Using random.random() without seed
    rand_value = random.random()  # Different value each call!
    
    # ... prize determination ...
```

### Trigger Conditions

**Any lottery draw with the same inputs will produce different outputs:**

```python
# Input (identical)
user = User("U001", UserLevel.GOLD, total_consumption=8000)

# Run 1
lottery1 = LotterySystem()
prize1, _ = lottery1.draw(user)  # Result: Third prize

# Run 2 (identical input)
lottery2 = LotterySystem()
prize2, _ = lottery2.draw(user)  # Result: No prize

# Run 3 (identical input)
lottery3 = LotterySystem()
prize3, _ = lottery3.draw(user)  # Result: Second prize
```

### Expected Behavior

For deterministic testing, the system should support seeded random number generation:
- Same seed + same input → same output (reproducible)
- Tests can set seed for consistent results
- Production can use random seed for true randomness

### Actual Behavior

- No seed control mechanism
- Each test run produces different results
- Probabilistic tests fail randomly
- CI/CD pipelines show intermittent failures

### Reproducing the Bug

Run this test multiple times:

```powershell
# Run 5 times and observe different results
for($i=1; $i -le 5; $i++) { 
    Write-Host "`n=== Run $i ===" 
    pytest tests/test_lottery.py::TestFlakyBehavior::test_gold_user_win_rate_FLAKY -v 
}
```

**Typical Output**:
- Run 1: PASSED (win rate: 0.2751)
- Run 2: FAILED (win rate: 0.1923) ❌
- Run 3: PASSED (win rate: 0.2834)
- Run 4: FAILED (win rate: 0.3456) ❌
- Run 5: PASSED (win rate: 0.2612)

### Impact

- **Test Reliability**: Tests fail randomly, not due to code bugs
- **CI/CD**: Builds fail intermittently, causing false alarms
- **Developer Productivity**: Time wasted investigating flaky test failures
- **Confidence**: Cannot trust test results
- **Debugging**: Cannot reproduce failures consistently

---

## Bug #2: Factory Function Ignores Seed Parameter

### Description

The `create_lottery()` factory function accepts a `seed` parameter for controlling randomness, but completely ignores it! This gives users false confidence that they can control random behavior.

### Location

- **File**: [src/lottery.py](src/lottery.py)
- **Function**: `create_lottery()` (Line ~240-250)

### Root Cause

```python
def create_lottery(seed: Optional[int] = None) -> LotterySystem:
    """
    Factory function to create a lottery system.
    
    Args:
        seed: Random seed for deterministic behavior (optional)
              BUG: This parameter is accepted but NOT used!
    
    Returns:
        LotterySystem instance
    """
    # BUG: Seed parameter is ignored!
    # Should call: if seed is not None: random.seed(seed)
    return LotterySystem()
```

### Trigger Conditions

**Using seed parameter has no effect:**

```python
# User expects deterministic behavior
lottery1 = create_lottery(seed=42)
user1 = User("U001", UserLevel.GOLD, 5000)
prize1, _ = lottery1.draw(user1)  # Random result A

# Same seed should give same result
lottery2 = create_lottery(seed=42)
user2 = User("U001", UserLevel.GOLD, 5000)
prize2, _ = lottery2.draw(user2)  # Random result B (different!)

# BUG: prize1 != prize2 (most likely)
```

### Expected Behavior

- `create_lottery(seed=42)` should produce deterministic results
- Same seed should always produce same sequence
- Enables reproducible testing

### Actual Behavior

- Seed parameter is silently ignored
- Results vary even with same seed
- Misleading API contract

### Reproducing the Bug

```powershell
pytest tests/test_lottery.py::TestFlakyBehavior::test_seed_parameter_ignored_FLAKY -v
```

This test will fail approximately 50% of the time (when the two random draws happen to differ).

### Impact

- **API Confusion**: Function signature promises functionality it doesn't deliver
- **User Frustration**: Developers waste time trying to fix their code
- **Hidden Bug**: Problem is not obvious from API alone

---

## Bug #3: Set Iteration Order (Minor Contributing Factor)

### Description

The code uses a `set` to iterate over prize types, which has undefined iteration order (even in Python 3.7+, sets are unordered). While this is a minor issue compared to the random seed problem, it contributes to non-determinism.

### Location

- **File**: [src/lottery.py](src/lottery.py)
- **Method**: `draw()` (Line ~150)

### Root Cause

```python
# BUG: Using set which has undefined iteration order
prize_types_set = {PrizeType.FIRST, PrizeType.SECOND, PrizeType.THIRD, PrizeType.NONE}

for prize_type in prize_types_set:  # Order not guaranteed
    cumulative += adjusted_probs.get(prize_type, 0)
    if rand_value < cumulative:
        # Prize selection logic
```

### Impact

Minor contribution to non-determinism, though the main issue is the random seed.

---

## Combined Impact Example

### Scenario: CI/CD Pipeline Failure

**Day 1** - Developer commits code:
```
✓ All tests pass locally (lucky random sequence)
✓ Push to repository
✗ CI fails: test_gold_user_win_rate_FLAKY failed (unlucky random sequence)
Developer re-runs CI → ✓ Passes (lucky again)
Code merged
```

**Day 2** - Another developer:
```
✓ Pull latest code
✗ Tests fail locally (unlucky)
Investigates for 2 hours
✓ Runs again → passes (lucky)
Confused, blames environment
```

**Day 3** - QA team:
```
✗ Nightly build fails
Bug report filed
✓ Developer cannot reproduce
✗ QA runs again → fails again
✓ Developer runs → passes
Team wastes 4 hours in meetings
```

---

## Fix Strategy

### Fix #1: Initialize Random Seed in LotterySystem

**Modify `__init__()` to accept optional seed:**

```python
def __init__(self, prize_pool: Optional[PrizePool] = None, random_seed: Optional[int] = None):
    self.prize_pool = prize_pool or PrizePool()
    self.ip_win_counts: Dict[str, int] = {}
    
    # FIX: Initialize random seed if provided
    if random_seed is not None:
        random.seed(random_seed)
```

### Fix #2: Use Seed Parameter in Factory Function

**Modify `create_lottery()` to actually use the seed:**

```python
def create_lottery(seed: Optional[int] = None) -> LotterySystem:
    # FIX: Pass seed to LotterySystem constructor
    return LotterySystem(random_seed=seed)
```

### Fix #3: Use Ordered Collection for Prize Types

**Replace set with list:**

```python
# FIX: Use list for deterministic iteration order
prize_types_list = [PrizeType.FIRST, PrizeType.SECOND, PrizeType.THIRD, PrizeType.NONE]

for prize_type in prize_types_list:  # Order guaranteed
    # Prize selection logic
```

### Alternative Fix: Use Random Instance Instead of Module

**Better design - use Random instance:**

```python
class LotterySystem:
    def __init__(self, prize_pool: Optional[PrizePool] = None, random_seed: Optional[int] = None):
        self.prize_pool = prize_pool or PrizePool()
        self.ip_win_counts: Dict[str, int] = {}
        
        # FIX: Use instance-level random generator
        self.rng = random.Random(random_seed)
    
    def draw(self, user: User) -> tuple[PrizeType, str]:
        # Use instance RNG instead of module-level
        rand_value = self.rng.random()
        # ...
```

---

## Verification After Fix

After applying fixes, all tests should pass consistently:

```powershell
# Run tests 10 times - all should pass
for($i=1; $i -le 10; $i++) { 
    pytest tests/ -v 
}
# Expected: 12/12 tests passing every time ✅
```

---

## Testing Best Practices

### For Future Tests

1. **Always control randomness in tests**:
   ```python
   def test_something():
       lottery = create_lottery(seed=12345)  # Fixed seed
       # ... deterministic test ...
   ```

2. **Use parametrized tests for probabilistic behavior**:
   ```python
   @pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
   def test_various_seeds(seed):
       lottery = create_lottery(seed=seed)
       # ... test with known seed ...
   ```

3. **Separate unit tests from statistical tests**:
   - Unit tests: Deterministic, fast, always pass/fail consistently
   - Statistical tests: Marked separately, run less frequently, allowed higher variance

4. **Document expected randomness**:
   - Clearly mark probabilistic tests
   - Set appropriate tolerances
   - Use confidence intervals

---

## Notes

- These bugs are intentionally planted for demonstration
- The flaky behavior is realistic and commonly seen in production code
- Fixes are straightforward but often overlooked
- Proper random seed management is critical for testable code
