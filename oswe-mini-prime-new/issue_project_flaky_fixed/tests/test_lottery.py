# Copied tests from original project (unchanged per requirements)

from src.lottery import (
    LotterySystem,
    User,
    UserLevel,
    PrizeType,
    PrizePool,
    create_lottery
)
from datetime import datetime, timedelta


def test_user_creation():
    user = User(user_id="U001", level=UserLevel.GOLD, total_consumption=8000)
    assert user.user_id == "U001"
    assert user.level == UserLevel.GOLD
    assert user.total_consumption == 8000
    assert user.today_wins == 0


def test_prize_pool_initialization():
    pool = PrizePool()
    assert pool.first_remaining == 10
    assert pool.second_remaining == 100
    assert pool.third_remaining == 1000


def test_prize_pool_consumption():
    pool = PrizePool(first_remaining=1)
    assert pool.consume(PrizeType.FIRST) is True
    assert pool.first_remaining == 0
    assert pool.consume(PrizeType.FIRST) is False


def test_daily_win_limit():
    lottery = LotterySystem()
    user = User(user_id="U001", level=UserLevel.DIAMOND, total_consumption=20000, today_wins=3)
    can_win, reason = lottery._can_user_win(user)
    assert can_win is False
    assert "daily win limit" in reason.lower()


def test_win_interval():
    lottery = LotterySystem()
    user = User(user_id="U001", level=UserLevel.GOLD, total_consumption=5000, today_wins=1, last_win_time=datetime.now() - timedelta(minutes=5))
    can_win, reason = lottery._can_user_win(user)
    assert can_win is False
    assert "interval" in reason.lower()


def test_ip_limit():
    lottery = LotterySystem()
    lottery.ip_win_counts["192.168.1.1"] = 5
    user = User(user_id="U001", level=UserLevel.GOLD, total_consumption=5000, ip_address="192.168.1.1")
    can_win, reason = lottery._can_user_win(user)
    assert can_win is False
    assert "ip" in reason.lower()


def test_regular_user_base_probability():
    lottery = LotterySystem()
    user = User(user_id="U001", level=UserLevel.REGULAR, total_consumption=500)
    prob = lottery.calculate_win_probability(user)
    assert 0.10 < prob < 0.12


def test_gold_user_with_consumption_bonus():
    lottery = LotterySystem()
    user = User(user_id="U001", level=UserLevel.GOLD, total_consumption=8000)
    prob = lottery.calculate_win_probability(user)
    assert 0.25 < prob < 0.30


def test_gold_user_win_rate_FLAKY():
    lottery = LotterySystem()
    wins = 0
    trials = 10000
    for i in range(trials):
        user = User(user_id=f"U{i}", level=UserLevel.GOLD, total_consumption=8000)
        prize, _ = lottery.draw(user)
        if prize != PrizeType.NONE:
            wins += 1
    win_rate = wins / trials
    assert 0.22 < win_rate < 0.32


def test_batch_draw_distribution_FLAKY():
    lottery = LotterySystem()
    users = [User(user_id=f"U{i:04d}", level=UserLevel.SILVER, total_consumption=3000) for i in range(1000)]
    results = lottery.batch_draw(users)
    first_count = sum(1 for p in results.values() if p == PrizeType.FIRST)
    second_count = sum(1 for p in results.values() if p == PrizeType.SECOND)
    third_count = sum(1 for p in results.values() if p == PrizeType.THIRD)
    assert first_count <= 10
    assert 8 <= second_count <= 25
    assert 110 <= third_count <= 180


def test_multiple_runs_consistency_FLAKY():
    results = []
    for run in range(5):
        lottery = LotterySystem()
        wins = 0
        for i in range(500):
            user = User(user_id=f"R{run}_U{i}", level=UserLevel.REGULAR, total_consumption=2000)
            prize, _ = lottery.draw(user)
            if prize != PrizeType.NONE:
                wins += 1
        results.append(wins)
    mean = sum(results) / len(results)
    variance = sum((x - mean) ** 2 for x in results) / len(results)
    std_dev = variance ** 0.5
    assert std_dev < 10


def test_seed_parameter_ignored_FLAKY():
    lottery1 = create_lottery(seed=42)
    user1 = User("U001", UserLevel.GOLD, 5000)
    prize1, _ = lottery1.draw(user1)
    lottery2 = create_lottery(seed=42)
    user2 = User("U001", UserLevel.GOLD, 5000)
    prize2, _ = lottery2.draw(user2)
    assert prize1 == prize2


def test_with_manual_seed_deterministic():
    import random
    random.seed(12345)
    lottery = LotterySystem()
    wins = 0
    for i in range(1000):
        user = User(user_id=f"U{i}", level=UserLevel.GOLD, total_consumption=8000)
        prize, _ = lottery.draw(user)
        if prize != PrizeType.NONE:
            wins += 1
    assert wins > 0
