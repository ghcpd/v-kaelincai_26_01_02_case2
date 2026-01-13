# Fixed Marketing Lottery System (Stable)

This repository contains a fixed, stable version of the Marketing Lottery System.

Key points:
- Deterministic behavior supported via `create_lottery(seed=...)` or `LotterySystem(random_seed=...)`
- Production randomness preserved when no seed provided
- Fixed prize selection order to avoid iteration-order non-determinism
- Tests from original project copied unchanged and now pass consistently

Run demo:

python demo_stable.py

Run tests:

pytest tests/ -v
