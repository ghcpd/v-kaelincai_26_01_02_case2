from src.lottery import LotterySystem, User, UserLevel, PrizeType

# Create lottery with seed 77
lottery = LotterySystem(seed=77)

# First draw
user = User('U0', UserLevel.GOLD, 8000)

# Get rand value (which will be consumed by draw)
rand_value = lottery._rng.random()

# Get probabilities
probs = lottery._calculate_adjusted_probabilities(user)

# Calculate cumulative
cumulative = 0.0
print(f'Random value: {rand_value:.6f}')
print()

for ptype in [PrizeType.FIRST, PrizeType.SECOND, PrizeType.THIRD, PrizeType.NONE]:
    cumulative += probs.get(ptype, 0)
    hits = rand_value < cumulative
    print(f'{ptype.value}: prob={probs[ptype]:.6f}, cumulative={cumulative:.6f}, hits={hits}')
    if hits:
        print(f'  -> This prize type would be selected')
        break

# Now actually do the draw
lottery2 = LotterySystem(seed=77)
user2 = User('U0', UserLevel.GOLD, 8000)
prize, msg = lottery2.draw(user2)
print(f'\nActual draw result: {prize.value} ({msg})')
