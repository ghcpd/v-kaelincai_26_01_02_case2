from src.lottery import LotterySystem, User, UserLevel
L = LotterySystem()
u = User('U', UserLevel.GOLD, 8000)
for i in range(10):
    rv = L._rng.random()
    adj = L._calculate_adjusted_probabilities(u)
    print(i, rv)
    for k,v in adj.items():
        print('  ', k.name, v)
    print('---')
