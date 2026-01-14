"""Demo for the fixed lottery system.

Shows deterministic behavior when a seed is provided and non-deterministic when not.
"""
from src import create_lottery, User, UserLevel

def demo(seed=None):
    lottery = create_lottery(seed=seed)
    user = User("demo_user", UserLevel.GOLD, total_consumption=8000)
    prize, msg = lottery.draw(user)
    print(f"seed={seed!r} -> prize={prize}, msg={msg}")

if __name__ == "__main__":
    print("Deterministic run (seed=42):")
    demo(seed=42)
    print("Deterministic run repeated (seed=42):")
    demo(seed=42)
    print("Random run (no seed):")
    demo()
