from src.lottery import LotterySystem, User, UserLevel, PrizeType

lottery = LotterySystem(seed=77)

# Find first win
for i in range(100):
    user = User(f'U{i}', UserLevel.GOLD, 8000)
    prize, msg = lottery.draw(user)
    if prize != PrizeType.NONE:
        print(f'First win at draw {i}: {prize.value} ({msg})')
        break

# Count wins in first 1000
lottery2 = LotterySystem(seed=77)
wins = 0
for i in range(1000):
    user = User(f'U{i}', UserLevel.GOLD, 8000)
    prize, msg = lottery2.draw(user)
    if prize != PrizeType.NONE:
        wins += 1

print(f'\nWins in first 1000 draws: {wins}')
print(f'Win rate: {wins/1000:.4f}')

# Count total in 10000
lottery3 = LotterySystem(seed=77)
wins = 0
for i in range(10000):
    user = User(f'U{i}', UserLevel.GOLD, 8000)
    prize, msg = lottery3.draw(user)
    if prize != PrizeType.NONE:
        wins += 1

print(f'\nTotal wins in 10000 draws: {wins}')
print(f'Win rate: {wins/10000:.4f}')
