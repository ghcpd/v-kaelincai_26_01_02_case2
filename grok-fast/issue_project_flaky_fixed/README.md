# Marketing Lottery System (Fixed Version)

A Python-based marketing lottery system for e-commerce platforms. This project demonstrates **Stable Behavior** where the same inputs produce consistent outputs due to deterministic random number generation with seed control.

## Project Overview

This is the **FIXED VERSION** of the marketing lottery system that resolves all flaky behavior bugs:
- Same input produces identical outputs when seeded
- Tests pass consistently across multiple runs
- Deterministic behavior for testing, random for production
- Reliable CI/CD pipelines

## Project Structure

```
issue_project_flaky_fixed/
├── src/
│   ├── __init__.py
│   └── lottery.py                # Core lottery logic (FIXED - deterministic)
├── tests/
│   ├── __init__.py
│   └── test_lottery.py           # Test suite with stable tests
├── demo_stable.py                # Interactive demonstration of stability
├── README.md                     # This file
├── FIX_REPORT.md                 # Documentation of fixes applied
└── requirements.txt              # Python dependencies
```

## Business Rules

The lottery system calculates win probability based on:

1. **User Level Multipliers**:
   - Regular: 1.0x
   - Silver: 1.2x
   - Gold: 1.5x
   - Diamond: 2.0x

2. **Consumption Bonuses**:
   - < 1000: No bonus
   - 1000-4999: +5%
   - 5000-9999: +10%
   - ≥10000: +20%

3. **Prize Pool** (Daily limits):
   - First Prize (1000 CNY): 0.1% probability, 10 per day
   - Second Prize (100 CNY): 1% probability, 100 per day
   - Third Prize (10 CNY): 10% probability, 1000 per day
   - No Prize: 88.9% probability

4. **Anti-Fraud Rules**:
   - Max 3 wins per user per day
   - Minimum 10-minute interval between wins
   - Max 5 wins per IP per day

## Quick Start

### Installation

Install dependencies (Python 3.8+ required):

```powershell
pip install -r requirements.txt
```

### Run Tests

Execute all tests - they should pass consistently:

```powershell
pytest tests/ -v
```

### Expected Test Results

**All tests should pass consistently across multiple runs:**
- 13/13 tests passing every time ✅
- No flaky failures
- Deterministic results when seeded

### Demonstrating Stability

Run the same test multiple times to verify consistency:

```powershell
# Run 1
pytest tests/test_lottery.py::TestFlakyBehavior::test_gold_user_win_rate_FLAKY -v

# Run 2 (should produce identical result!)
pytest tests/test_lottery.py::TestFlakyBehavior::test_gold_user_win_rate_FLAKY -v

# Run 3 (yet another identical result!)
pytest tests/test_lottery.py::TestFlakyBehavior::test_gold_user_win_rate_FLAKY -v
```

## Example Usage

```python
from src.lottery import LotterySystem, User, UserLevel, create_lottery

# For testing: Use seeded lottery for deterministic results
lottery = create_lottery(seed=42)

# Create user
user = User(
    user_id="U001",
    level=UserLevel.GOLD,
    total_consumption=8000
)

# Draw lottery - STABLE: result is consistent with seed
prize, message = lottery.draw(user)
print(f"Result: {prize.value} - {message}")

# Run again with SAME seed - IDENTICAL result!
lottery2 = create_lottery(seed=42)
user2 = User(
    user_id="U001",
    level=UserLevel.GOLD,
    total_consumption=8000
)
prize2, message2 = lottery2.draw(user2)
print(f"Result: {prize2.value} - {message2}")
# FIXED: prize == prize2 (always!)

# For production: No seed for true randomness
production_lottery = LotterySystem()  # No seed
prize_prod, _ = production_lottery.draw(user)
# Result varies randomly as intended
```

## Key Improvements

### ✅ Deterministic Testing
- `create_lottery(seed=X)` now works correctly
- Same seed + same input → same output
- Tests are reproducible and reliable

### ✅ Production Randomness
- `LotterySystem()` without seed maintains randomness
- Real lottery behavior preserved for users
- No degradation of user experience

### ✅ Instance-Level Random Control
- Each `LotterySystem` has its own random generator
- No interference between different lottery instances
- Thread-safe random number generation

### ✅ Consistent Iteration Order
- Prize types processed in deterministic order
- No flaky behavior from set/dict iteration
- Predictable prize selection logic

## Test Coverage

Run tests with coverage report:

```powershell
pytest tests/ --cov=src --cov-report=term-missing -v
```

## Stability Demonstration

The `demo_stable.py` script shows:

1. **Consistent Results**: Same inputs give same outputs with seeds
2. **Statistical Stability**: Win rates are identical across runs
3. **Seed Functionality**: `create_lottery(seed=X)` works correctly
4. **Batch Consistency**: Batch processing is deterministic
5. **Production Randomness**: No seed still provides randomness

## Technology Stack

- Python 3.8+
- pytest (testing framework)
- dataclasses (data structures)
- enum (type safety)

## Success Metrics

To verify the fixes work:

1. Run tests 10 times: `for($i=1; $i -le 10; $i++) { pytest tests/ -v }`
2. Observe "13 passed" every single time ✅
3. No test failures due to randomness
4. All probabilistic tests pass consistently

## Comparison with Flaky Version

| Aspect | Flaky Version | Fixed Version |
|--------|---------------|---------------|
| Test Reliability | Random failures | Always passes |
| Seed Parameter | Ignored | Works correctly |
| Same Input | Different outputs | Identical outputs (seeded) |
| CI/CD | Unreliable | Reliable |
| Debugging | Impossible | Easy reproduction |
| Production | Random | Still random |

## License

MIT License - For educational and demonstration purposes.