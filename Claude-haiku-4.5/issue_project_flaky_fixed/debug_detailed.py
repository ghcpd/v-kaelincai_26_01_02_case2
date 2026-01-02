from src.lottery import LotterySystem, User, UserLevel, PrizeType

# Use pure random module to know what values to expect
from random import Random
expected_rng = Random(77)

lottery = LotterySystem(seed=77)

for i in range(25):
    user = User(f'U{i}', UserLevel.GOLD, 8000)
    
    # Check eligibility
    can_win, reason = lottery._can_user_win(user)
    if not can_win:
        print(f"Draw {i}: NOT ELIGIBLE - {reason}")
        expected_rng.random()  # Keep in sync
        continue
    
    # Get expected random value
    expected_rand = expected_rng.random()
    
    # Do actual draw
    prize, msg = lottery.draw(user)
    
    # Determine if should have won
    should_win = expected_rand < 0.2306
    actually_won = prize != PrizeType.NONE
    
    # Print result
    match = "✓" if (should_win == actually_won) else "✗"
    print(f"Draw {i}: rand={expected_rand:.6f}, should_win={should_win}, actual_win={actually_won} {match}")

