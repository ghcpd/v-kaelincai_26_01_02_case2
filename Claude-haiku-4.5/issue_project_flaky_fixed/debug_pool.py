from src.lottery import LotterySystem, User, UserLevel, PrizeType

lottery = LotterySystem(seed=77)

# Track wins
wins_by_type = {PrizeType.FIRST: 0, PrizeType.SECOND: 0, PrizeType.THIRD: 0}

for i in range(10000):
    user = User(f'U{i}', UserLevel.GOLD, 8000)
    prize, msg = lottery.draw(user)
    if prize != PrizeType.NONE:
        wins_by_type[prize] += 1
        if i < 100:  # Show first few wins
            print(f'Draw {i}: {prize.value}')

print(f'\nWins: first={wins_by_type[PrizeType.FIRST]}, second={wins_by_type[PrizeType.SECOND]}, third={wins_by_type[PrizeType.THIRD]}')
print(f'Total: {sum(wins_by_type.values())}')

# Check pool status
print(f'\nPrize pool remaining:')
print(f'  first: {lottery.prize_pool.first_remaining}/10')
print(f'  second: {lottery.prize_pool.second_remaining}/100')
print(f'  third: {lottery.prize_pool.third_remaining}/1000')
