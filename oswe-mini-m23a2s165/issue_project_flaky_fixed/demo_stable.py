"""Demo for the fixed, stable LotterySystem.

Shows deterministic behavior when a seed is provided and true randomness when no seed.
"""
from src.lottery import create_lottery, User, UserLevel


def demo_seeded():
    lottery = create_lottery(seed=12345)
    user = User(user_id="demo", level=UserLevel.GOLD, total_consumption=8000)
    prize, msg = lottery.draw(user)
    print(f"Seeded draw -> prize={prize}, msg='{msg}'")


def demo_unseeded():
    lottery = create_lottery()
    user = User(user_id="demo", level=UserLevel.GOLD, total_consumption=8000)
    prize, msg = lottery.draw(user)
    print(f"Unseeded draw -> prize={prize}, msg='{msg}'")


if __name__ == "__main__":
    demo_seeded()
    demo_seeded()  # repeat to show determinism
    demo_unseeded()  # may vary between runs
