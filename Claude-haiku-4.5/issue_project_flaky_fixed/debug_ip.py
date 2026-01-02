from src.lottery import LotterySystem, User, UserLevel, PrizeType

lottery = LotterySystem(seed=77)
wins = 0

for i in range(100):
    user = User(
        user_id=f"U{i}",
        level=UserLevel.GOLD,
        total_consumption=8000,
        ip_address=f"10.{(i // 65536) % 256}.{(i // 256) % 256}.{i % 256}"
    )
    prize, msg = lottery.draw(user)
    if prize != PrizeType.NONE:
        wins += 1
        if wins <= 10:  # Show first 10 wins
            print(f"Win {wins}: Draw {i}, {prize.value}, IP={user.ip_address}")

print(f"\nWins: {wins} out of 100")

# Check pool
print(f"Pool remaining: first={lottery.prize_pool.first_remaining}, second={lottery.prize_pool.second_remaining}, third={lottery.prize_pool.third_remaining}")

# Check IPs used
ip_counts = {}
for i in range(100):
    ip = f"10.{(i // 65536) % 256}.{(i // 256) % 256}.{i % 256}"
    ip_counts[ip] = ip_counts.get(ip, 0) + 1

print(f"\nUnique IPs: {len(ip_counts)}")
print(f"IP win counts: {lottery.ip_win_counts}")
