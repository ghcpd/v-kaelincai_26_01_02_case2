# FIX REPORT

## Summary
- Fixed sources of non-determinism in `src/lottery.py`.
- Main fixes: honor `seed` in factory, use instance RNG when seeded, use deterministic prize iteration order, preserve production randomness when no seed provided.

## Bugs Fixed

1. File: `src/lottery.py` - create_lottery / LotterySystem
   - Issue: `create_lottery(seed=...)` accepted a seed but ignored it; `LotterySystem` used module-level `random.random()` exclusively.
   - Impact: Same-seed runs produced different results; tests were flaky.
   - Fix: `create_lottery(seed)` now creates a `random.Random(seed)` and passes it into `LotterySystem`. `LotterySystem` uses the provided RNG for all draws. When no RNG/seed is provided, the system falls back to module-level `random` (preserves existing behavior where `random.seed(...)` is used externally).

2. File: `src/lottery.py` - Prize iteration order
   - Issue: `draw()` iterated over a `set` of prize types (undefined order), causing non-deterministic prize selection in some scenarios.
   - Impact: Iteration order affected cumulative probability checks and made outcomes non-deterministic between runs.
   - Fix: Replaced `set` with a deterministic `PRIZE_ITERATION_ORDER` list: [FIRST, SECOND, THIRD, NONE].

3. File: `src/lottery.py` - Random usage in code paths
   - Issue: Direct calls to `random.random()` made deterministic testing via instance-level seeding impossible.
   - Fix: Added `_rand()` helper that uses the instance RNG when provided; otherwise falls back to `random.random()`.

## Test Results
All tests in `tests/` now pass consistently.

Example: 5 consecutive runs (each run output: "13 passed")

Run 1: 13 passed
Run 2: 13 passed
Run 3: 13 passed
Run 4: 13 passed
Run 5: 13 passed

(Verified by running the test suite repeatedly.)

## Verification
- Deterministic example:
  - `l1 = create_lottery(seed=42)` and `l2 = create_lottery(seed=42)` produce identical results for the same sequence of draws.
- Production example:
  - `create_lottery()` (no seed) uses system randomness; results may vary as expected.

## Notes
- API is backward compatible: existing callers using `LotterySystem()` or `random.seed(...)` continue to work.
- Tests were not modified.
