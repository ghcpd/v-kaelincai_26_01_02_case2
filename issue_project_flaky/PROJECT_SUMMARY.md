# Project Summary - Marketing Lottery System (Flaky)

## Overview
Complete Python project demonstrating **FLAKY BEHAVIOR** where same inputs produce inconsistent outputs.

## Directory Structure
```
issue_project_flaky/
├── src/
│   ├── __init__.py                  # Package initialization
│   └── lottery.py                   # Core lottery logic (300+ lines, FLAKY BUGS)
├── tests/
│   ├── __init__.py                  # Test package initialization
│   └── test_lottery.py              # Test suite (13 tests, 3-4 flaky)
├── demo_flaky.py                    # Interactive flaky demonstration
├── README.md                        # Setup and usage guide
├── KNOWN_ISSUE.md                   # Detailed bug analysis
└── requirements.txt                 # Python dependencies (pytest)
```

## Quick Start Command

```powershell
# One command to setup and run:
pip install -r requirements.txt; pytest tests/ -v
```

## Test Results Summary

**Total Tests**: 13
- ✅ **Stable Tests**: 8-10 tests consistently pass (basic functionality)
- ❌ **Flaky Tests**: 3-4 tests fail RANDOMLY and inconsistently

### Flaky Test Behavior

Run the same tests multiple times and observe DIFFERENT results:

**Run 1**:
```
FAILED test_gold_user_win_rate_FLAKY (win rate: 0.0005)
FAILED test_batch_draw_distribution_FLAKY (0 second prizes)
FAILED test_seed_parameter_ignored_FLAKY (prizes differ)
PASSED test_multiple_runs_consistency_FLAKY
Result: 3 failed, 10 passed
```

**Run 2** (immediately after, no code changes):
```
FAILED test_gold_user_win_rate_FLAKY (win rate: 0.0005)
FAILED test_batch_draw_distribution_FLAKY (0 second prizes)  
PASSED test_seed_parameter_ignored_FLAKY (prizes same by chance)
PASSED test_multiple_runs_consistency_FLAKY
Result: 2 failed, 11 passed  ← Different result!
```

**Run 3** (again, same code):
```
PASSED test_gold_user_win_rate_FLAKY (lucky! win rate: 0.2751)
FAILED test_batch_draw_distribution_FLAKY (too many third prizes)
FAILED test_seed_parameter_ignored_FLAKY (prizes differ)
FAILED test_multiple_runs_consistency_FLAKY (high variance)
Result: 3 failed, 10 passed  ← Yet another result!
```

## Bugs Planted

### Bug #1: Random Number Generation Without Seed
- **Location**: [src/lottery.py](src/lottery.py) (Line ~83, ~143)
- **Issue**: `random.random()` called without `random.seed()`
- **Impact**: Every draw produces different random sequence

### Bug #2: Factory Function Ignores Seed Parameter
- **Location**: [src/lottery.py](src/lottery.py) (Line ~246)
- **Issue**: `create_lottery(seed=42)` accepts but ignores seed parameter
- **Impact**: Users cannot control randomness even when they try

### Bug #3: Set Iteration (Minor)
- **Location**: [src/lottery.py](src/lottery.py) (Line ~150)
- **Issue**: Using `set` for prize type iteration
- **Impact**: Contributes to non-determinism

## Reproduction Steps

### Option 1: Run Tests Multiple Times
```powershell
# Run same test 5 times
for($i=1; $i -le 5; $i++) { 
    Write-Host "`n=== Run $i ==="
    pytest tests/test_lottery.py::TestFlakyBehavior::test_seed_parameter_ignored_FLAKY -v
}
```

**Expected**: Different pass/fail results across runs

### Option 2: Interactive Demo
```powershell
python demo_flaky.py
```

### Option 3: Manual Code Execution
```python
from src.lottery import LotterySystem, User, UserLevel

# Same input
user = User("U001", UserLevel.GOLD, 8000)

# Run 1
lottery1 = LotterySystem()
print(lottery1.draw(user))  # Different result each time!

# Run 2 (identical input)
lottery2 = LotterySystem()
print(lottery2.draw(user))  # Different result!
```

## Fix Verification

After applying fixes from KNOWN_ISSUE.md, tests should be stable:

```powershell
# Run tests 10 times - all should pass consistently
for($i=1; $i -le 10; $i++) { 
    pytest tests/ -v 
}
# Expected: 13/13 tests passing every time ✅
```

## Technical Details

- **Language**: Python 3.8+
- **Testing**: pytest 7.4.0+
- **Dependencies**: Minimal (only pytest for testing)
- **Code Quality**: Type hints, docstrings, enums
- **Complexity**: Complex business logic, simple bug

## Real-World Impact Simulation

This project simulates real CI/CD problems:

1. **Developer Experience**:
   - Local tests pass ✓
   - Push to CI → fails ✗
   - Re-run → passes ✓
   - Confusion and time waste

2. **Team Productivity Loss**:
   - Investigating false failures
   - Debugging non-reproducible issues
   - Meeting discussions about "flaky tests"
   - Reduced confidence in test suite

3. **Business Impact**:
   - Delayed releases
   - False alarms in production monitoring
   - Inconsistent analytics/reporting

## Educational Value

This project demonstrates:
- ✅ Flaky behavior from uncontrolled randomness
- ✅ Non-deterministic test failures
- ✅ Importance of seeded random generation
- ✅ API design pitfalls (ignored parameters)
- ✅ Testing best practices for probabilistic systems

## Comparison with First Project

| Aspect | issue_project (Functional Bug) | issue_project_flaky (Flaky Behavior) |
|--------|-------------------------------|--------------------------------------|
| Bug Type | Wrong output (deterministic) | Inconsistent output (non-deterministic) |
| Test Results | Always same failures | Different failures each run |
| Reproducibility | 100% reproducible | Varies randomly |
| Debugging | Straightforward | Very frustrating |
| Fix Complexity | Simple | Simple (but often overlooked) |
