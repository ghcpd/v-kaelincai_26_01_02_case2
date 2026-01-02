"""Demo script for stable lottery behavior

Shows deterministic behavior with seed and non-deterministic behavior without seed.
"""
from src.lottery import create_lottery, LotterySystem, User, UserLevel


def run_demo_with_seed():
    lottery = create_lottery(seed=12345)
    wins = 0
    for i in range(1000):
        user = User(user_id=f"U{i}", level=UserLevel.GOLD, total_consumption=8000)
        prize, _ = lottery.draw(user)
        if prize != None and prize.name != "NONE":
            wins += 1
    print("Deterministic run (seed=12345) wins:", wins)


def run_demo_no_seed():
    lottery = LotterySystem()  # no seed -> random behavior
    wins = 0
    for i in range(1000):
        user = User(user_id=f"U{i}", level=UserLevel.GOLD, total_consumption=8000)
        prize, _ = lottery.draw(user)
        if prize != None and prize.name != "NONE":
            wins += 1
    print("Random run (no seed) wins:", wins)


if __name__ == "__main__":
    run_demo_with_seed()
    run_demo_no_seed()