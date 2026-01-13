from src.lottery import LotterySystem, User, UserLevel, PrizeType

lottery = LotterySystem()
counts = {PrizeType.FIRST:0, PrizeType.SECOND:0, PrizeType.THIRD:0, PrizeType.NONE:0}
for i in range(10000):
    user = User(user_id=f"U{i}", level=UserLevel.GOLD, total_consumption=8000)
    prize, _ = lottery.draw(user)
    counts[prize] += 1

print('counts', counts)
print('remaining', lottery.prize_pool.first_remaining, lottery.prize_pool.second_remaining, lottery.prize_pool.third_remaining)
