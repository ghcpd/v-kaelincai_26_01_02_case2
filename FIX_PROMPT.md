# Bug Fix Task - Marketing Lottery System (Flaky Behavior)

## Task Overview
You are a senior software engineer tasked with fixing a Python marketing lottery system that exhibits flaky behavior. The same inputs produce inconsistent outputs, causing non-deterministic test failures. Your goal is to analyze the existing flaky project, identify and fix all issues, and create a stable version in a new directory.

## Source Project Location
The flaky project is located at:
```
issue_project_flaky/
├── src/
│   ├── __init__.py
│   └── lottery.py                   # Core lottery logic (WITH FLAKY BUGS)
├── tests/
│   ├── __init__.py
│   └── test_lottery.py              # 13 tests (3-4 fail randomly)
├── demo_flaky.py
├── README.md
├── KNOWN_ISSUE.md
├── PROJECT_SUMMARY.md
├── DELIVERY.md
└── requirements.txt
```

## Your Task

### Step 1: Analyze the Flaky Project
1. Read and understand the business requirements from `README.md`
2. Review the bug documentation in `KNOWN_ISSUE.md`
3. **Run the tests multiple times** and observe varying results:
   ```powershell
   pytest tests/ -v  # Run 1
   pytest tests/ -v  # Run 2 - different results!
   pytest tests/ -v  # Run 3 - yet more variations!
   ```
4. Examine the flaky implementation in `src/lottery.py`

### Step 2: Create Fixed Version in New Directory
Create a completely new project directory named `issue_project_flaky_fixed/` with the following structure:

```
issue_project_flaky_fixed/
├── src/
│   ├── __init__.py
│   └── lottery.py                   # FIXED version (deterministic)
├── tests/
│   ├── __init__.py
│   └── test_lottery.py              # Same tests (all should pass consistently)
├── demo_stable.py                   # Demo showing consistent behavior
├── README.md                        # Updated documentation
├── FIX_REPORT.md                    # Document what you fixed and how
└── requirements.txt                 # Same dependencies
```

### Step 3: Fix All Flaky Bugs
- Identify and fix ALL sources of non-determinism
- Ensure tests pass consistently (run 10+ times without failures)
- Do NOT change test cases - they define correct behavior
- Maintain same business logic and probability calculations

### Step 4: Verification Requirements
Your fixed version must:
1. Pass all 13 tests consistently across multiple runs
2. Support deterministic testing via seed parameter
3. Maintain same probability calculations (when seed-controlled)
4. Allow production use with true randomness (no seed)
5. Honor the `create_lottery(seed=X)` parameter contract

### Step 5: Documentation
Create `FIX_REPORT.md` in the new directory with:
1. **Summary**: Brief overview of flaky issues found
2. **Bugs Fixed**: List each bug with:
   - File and function affected
   - Description of the non-determinism
   - Explanation of the fix applied
3. **Test Results**: Show all tests passing consistently
   - Include results from 5+ consecutive test runs
   - All should show "13 passed"
4. **Verification**: Demonstrate deterministic behavior with examples

## Expected Directory Structure After Completion

```
issue_project_flaky_fixed/        # Your fixed version (NEW)
├── src/
│   ├── __init__.py
│   └── lottery.py                # Fixed implementation
├── tests/
│   ├── __init__.py
│   └── test_lottery.py           # All tests pass consistently
├── demo_stable.py                # Demo with consistent results
├── README.md                     # Updated documentation
├── FIX_REPORT.md                 # Your fix documentation
└── requirements.txt              # Dependencies
```

Note: Create this as a sibling directory to `issue_project_flaky/`, not inside it.

## Success Criteria

Your fix is complete when:
- [ ] New directory `issue_project_flaky_fixed/` is created
- [ ] All source files are copied and flaky bugs are fixed
- [ ] Run tests 10 times: `for($i=1; $i -le 10; $i++) { pytest tests/ -v }` 
  - All 10 runs should show "13 passed" ✅
- [ ] Seeds work correctly: same seed = same results
- [ ] Production mode works: no seed = random results (as intended)
- [ ] `FIX_REPORT.md` documents all changes
- [ ] Demo script shows consistent behavior
- [ ] Original `issue_project_flaky/` directory remains untouched

## Important Constraints

1. **DO NOT** modify any files in `issue_project_flaky/` directory
2. **DO NOT** change the test cases - they define correct behavior  
3. **DO NOT** change the business logic (probability calculations)
4. **DO NOT** change the public API (class names, method signatures)
5. **DO** ensure tests are deterministic when seed is provided
6. **DO** allow randomness in production (when no seed provided)
7. **DO** maintain backward compatibility

## Hints

- Read `KNOWN_ISSUE.md` carefully - it describes the bugs
- The main issue is `random.random()` without seed control
- The `create_lottery(seed=X)` parameter is ignored - fix this!
- Consider using `random.Random()` instance instead of module-level `random`
- Run tests multiple times to verify consistency
- Focus on making tests stable, not on over-engineering

## Deliverables

1. Complete `issue_project_flaky_fixed/` directory with all files
2. `FIX_REPORT.md` documenting your changes with proof of consistency
3. Stable test suite (13/13 tests passing on every run)
4. Updated `README.md` noting this is the fixed, stable version

## Getting Started

Begin by demonstrating the flaky behavior:

```powershell
cd issue_project_flaky

# Run tests 5 times and observe different results
for($i=1; $i -le 5; $i++) { 
    Write-Host "`n=== Run $i ===" -ForegroundColor Cyan
    pytest tests/test_lottery.py::TestFlakyBehavior -v --tb=line
}
```

You should see varying pass/fail results. Your goal is to eliminate this variance.

## Testing Your Fix

After implementing fixes, verify stability:

```powershell
cd issue_project_flaky_fixed

# All 10 runs should show "13 passed"
for($i=1; $i -le 10; $i++) { 
    Write-Host "`n=== Run $i ===" -ForegroundColor Green
    pytest tests/ -v
}
```

## Key Questions to Answer in FIX_REPORT.md

1. What caused the flaky behavior?
2. How did you fix each source of non-determinism?
3. How do you ensure tests are deterministic?
4. How do you allow production randomness?
5. What evidence shows the fix works?

Good luck fixing the flaky tests!
