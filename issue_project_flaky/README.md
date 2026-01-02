# Marketing Lottery System

A Python-based marketing lottery system for e-commerce platforms. This project demonstrates **Flaky Behavior** where the same inputs produce inconsistent outputs due to non-deterministic random number generation.

## Project Overview

This is a minimal reproducible project that demonstrates a **Flaky Behavior** bug where:
- Same input produces different outputs across test runs
- Tests pass and fail randomly
- Non-deterministic failures make CI/CD unreliable
- Race conditions in random number generation

## Project Structure

```
issue_project_flaky/
├── src/
│   ├── __init__.py
│   └── lottery.py                # Core lottery logic (WITH FLAKY BUGS)
├── tests/
│   ├── __init__.py
│   └── test_lottery.py           # Test suite with flaky tests
├── demo_flaky.py                 # Interactive demonstration
├── README.md                     # This file
├── KNOWN_ISSUE.md                # Bug documentation
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

Execute all tests including the flaky ones:

```powershell
pytest tests/ -v
```

### Expected Test Results

**Deterministic Tests**: 8 tests should consistently pass (basic functionality)

**Flaky Tests**: 4 tests will FAIL RANDOMLY and inconsistently:
- `test_gold_user_win_rate_FLAKY` - Sometimes passes, sometimes fails
- `test_batch_draw_distribution_FLAKY` - Different failures each run
- `test_multiple_runs_consistency_FLAKY` - Highly unpredictable
- `test_seed_parameter_ignored_FLAKY` - Fails ~50% of the time

### Demonstrating Flakiness

Run the same test multiple times to see different results:

```powershell
# Run 1
pytest tests/test_lottery.py::TestFlakyBehavior::test_gold_user_win_rate_FLAKY -v

# Run 2 (may produce different result!)
pytest tests/test_lottery.py::TestFlakyBehavior::test_gold_user_win_rate_FLAKY -v

# Run 3 (yet another different result!)
pytest tests/test_lottery.py::TestFlakyBehavior::test_gold_user_win_rate_FLAKY -v
```

## Example Usage

```python
from src.lottery import LotterySystem, User, UserLevel

# Create lottery system
lottery = LotterySystem()

# Create user
user = User(
    user_id="U001",
    level=UserLevel.GOLD,
    total_consumption=8000
)

# Draw lottery - FLAKY: result varies each time!
prize, message = lottery.draw(user)
print(f"Result: {prize.value} - {message}")

# Run again with SAME user data - DIFFERENT result!
user2 = User(
    user_id="U001",
    level=UserLevel.GOLD,
    total_consumption=8000
)
prize2, message2 = lottery.draw(user2)
print(f"Result: {prize2.value} - {message2}")
# BUG: prize != prize2 (most of the time)
```

## Known Issues

This project intentionally contains flaky behavior bugs. See [KNOWN_ISSUE.md](KNOWN_ISSUE.md) for details.

**Summary**:
1. Random number generation without fixed seed
2. Factory function ignores seed parameter
3. Non-deterministic test results
4. CI/CD pipeline unreliability

## Test Coverage

Run tests with coverage report:

```powershell
pytest tests/ --cov=src --cov-report=term-missing -v
```

## Flaky Behavior Demonstration

The flaky behavior manifests in several ways:

1. **Probabilistic Test Failures**:
   - Expected win rate: 27% ± 5%
   - Actual results: Varies from 15% to 40%
   - Causes random test failures

2. **Inconsistent Batch Results**:
   - Same 1000 users processed
   - Run 1: 145 winners
   - Run 2: 167 winners
   - Run 3: 132 winners
   - Run 4: 189 winners

3. **Non-Reproducible Failures**:
   - Test fails in CI
   - Cannot reproduce locally
   - Re-running passes
   - Wastes developer time

## Technology Stack

- Python 3.8+
- pytest (testing framework)
- dataclasses (data structures)
- enum (type safety)

## Success Metrics

To verify the flaky behavior:

1. Run tests 10 times: `for($i=1; $i -le 10; $i++) { pytest tests/test_lottery.py::TestFlakyBehavior -v }`
2. Observe varying pass/fail results
3. Note different failure messages
4. Confirm non-deterministic behavior

## License

MIT License - For educational and demonstration purposes.
