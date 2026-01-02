from src.lottery import LotterySystem, User, UserLevel

u = User('U1', UserLevel.GOLD, total_consumption=8000)
lot = LotterySystem()
print('rng first values:', [lot.rng.random() for _ in range(3)])
print('adjusted:', {k.name: float(v) for k, v in lot._calculate_adjusted_probabilities(u).items()})
from collections import Counter
c = Counter()
for i in range(1000):
    prize, _ = lot.draw(User(f'U{i}', UserLevel.GOLD, total_consumption=8000))
    c[prize.name] += 1
print('draw counts (1000):', dict(c))
