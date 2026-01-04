from src.lottery import LotterySystem, User, UserLevel, PrizeType

lottery = LotterySystem(seed=12345)

# Manually check first 30 draws
print("Draw details:")
print("i, rand_value, cumulative, prize")

for i in range(30):
    user = User(f'U{i}', UserLevel.GOLD, 8000)
    
    # Manually replicate draw logic
    can_win, _ = lottery._can_user_win(user)
    if not can_win:
        print(f"{i}, N/A, N/A, ineligible")
        continue
    
    rand_value = lottery._rng.random()
    adj_probs = lottery._calculate_adjusted_probabilities(user)
    
    cumulative = 0.0
    result_prize = None
    hit_at_cumulative = None
    
    for prize_type in [PrizeType.FIRST, PrizeType.SECOND, PrizeType.THIRD, PrizeType.NONE]:
        cumulative += adj_probs.get(prize_type, 0)
        if rand_value < cumulative:
            result_prize = prize_type
            hit_at_cumulative = cumulative
            break
    
    print(f"{i}, {rand_value:.6f}, {hit_at_cumulative:.6f}, {result_prize.value if result_prize else 'none'}")

print(f"\nPrize pool at end: first={lottery.prize_pool.first_remaining}, second={lottery.prize_pool.second_remaining}, third={lottery.prize_pool.third_remaining}")
