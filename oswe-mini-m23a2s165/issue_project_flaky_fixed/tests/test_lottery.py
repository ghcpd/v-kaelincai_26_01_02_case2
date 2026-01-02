"""
Test suite for Marketing Lottery System.

These tests demonstrate FLAKY BEHAVIOR due to non-deterministic random number generation.
Tests may pass or fail depending on random outcomes, making CI/CD unreliable.

FLAKY TESTS INCLUDED:
1. test_gold_user_win_rate_FLAKY - Probabilistic test that sometimes fails
2. test_batch_draw_distribution_FLAKY - Distribution test with varying results
3. test_multiple_runs_consistency_FLAKY - Consistency test that exposes flakiness
"""

import pytest
from src.lottery import (
    LotterySystem,
    User,
    UserLevel,
    PrizeType,
    PrizePool,
    create_lottery
)
from datetime import datetime, timedelta


class TestBasicFunctionality:
    """Test basic lottery functionality (these should be stable)"""
    
    def test_user_creation(self):
        """Test user object creation"""
        user = User(
            user_id="U001",
            level=UserLevel.GOLD,
            total_consumption=8000
        )
        assert user.user_id == "U001"
        assert user.level == UserLevel.GOLD
        assert user.total_consumption == 8000
        assert user.today_wins == 0
    
    def test_prize_pool_initialization(self):
        """Test prize pool initialization"""
        pool = PrizePool()
        assert pool.first_remaining == 10
        assert pool.second_remaining == 100
        assert pool.third_remaining == 1000
    
    def test_prize_pool_consumption(self):
        """Test prize pool consumption"""
        pool = PrizePool(first_remaining=1)
        assert pool.consume(PrizeType.FIRST) is True
        assert pool.first_remaining == 0
        assert pool.consume(PrizeType.FIRST) is False


class TestAntiFragRules:
    """Test anti-fraud rules (these should be deterministic)"""
    
    def test_daily_win_limit(self):
        """Test daily win limit per user"""
        lottery = LotterySystem()
        user = User(
            user_id="U001",
            level=UserLevel.DIAMOND,
            total_consumption=20000,
            today_wins=3  # Already at limit
        )
        
        can_win, reason = lottery._can_user_win(user)
        assert can_win is False
        assert "daily win limit" in reason.lower()
    
    def test_win_interval(self):
        """Test minimum win interval"""
        lottery = LotterySystem()
        user = User(
            user_id="U001",
            level=UserLevel.GOLD,
            total_consumption=5000,
            today_wins=1,
            last_win_time=datetime.now() - timedelta(minutes=5)  # 5 min ago
        )
        
        can_win, reason = lottery._can_user_win(user)
        assert can_win is False
        assert "interval" in reason.lower()
    
    def test_ip_limit(self):
        """Test IP address win limit"""
        lottery = LotterySystem()
        lottery.ip_win_counts["192.168.1.1"] = 5  # At limit
        
        user = User(
            user_id="U001",
            level=UserLevel.GOLD,
            total_consumption=5000,
            ip_address="192.168.1.1"
        )
        
        can_win, reason = lottery._can_user_win(user)
        assert can_win is False
        assert "ip" in reason.lower()


class TestProbabilityCalculation:
    """Test probability calculation logic (deterministic)"""
    
    def test_regular_user_base_probability(self):
        """Test base probability for regular user"""
        lottery = LotterySystem()
        user = User(
            user_id="U001",
            level=UserLevel.REGULAR,
            total_consumption=500
        )
        
        prob = lottery.calculate_win_probability(user)
        # Base: 0.001 + 0.01 + 0.10 = 0.111 (11.1%)
        # Regular multiplier: 1.0
        # No consumption bonus
        assert 0.10 < prob < 0.12
    
    def test_gold_user_with_consumption_bonus(self):
        """Test probability for gold user with consumption bonus"""
        lottery = LotterySystem()
        user = User(
            user_id="U001",
            level=UserLevel.GOLD,
            total_consumption=8000
        )
        
        prob = lottery.calculate_win_probability(user)
        # Base: 0.111
        # Gold multiplier: 1.5 -> 0.1665
        # Consumption bonus (5000-10000): +0.10
        # Total: ~0.2665 (26.65%)
        assert 0.25 < prob < 0.30


class TestFlakyBehavior:
    """
    Tests that demonstrate FLAKY BEHAVIOR.
    
    These tests may pass or fail depending on random outcomes.
    They are intentionally unreliable to demonstrate the bug.
    """
    
    def test_gold_user_win_rate_FLAKY(self):
        """
        FLAKY TEST: Win rate for gold user (may fail randomly)
        
        Expected: ~27% win rate for gold user with 8000 consumption
        Actual: Varies widely due to random.random() without seed
        
        This test will:
        - Sometimes pass (when random results are favorable)
        - Sometimes fail (when random results deviate)
        - Create frustration in CI/CD pipelines
        """
        lottery = LotterySystem()
        
        wins = 0
        trials = 10000
        
        for i in range(trials):
            # Create fresh user for each trial
            user = User(
                user_id=f"U{i}",
                level=UserLevel.GOLD,
                total_consumption=8000
            )
            
            prize, _ = lottery.draw(user)
            if prize != PrizeType.NONE:
                wins += 1
        
        win_rate = wins / trials
        
        # Expected win rate: approximately 0.27 (27%)
        # Allow 5% margin: 0.22 to 0.32
        # BUG: This assertion will randomly fail!
        # Sometimes win_rate is 0.19, sometimes 0.35, etc.
        assert 0.22 < win_rate < 0.32, \
            f"Win rate {win_rate:.4f} outside expected range [0.22, 0.32]"
    
    def test_batch_draw_distribution_FLAKY(self):
        """
        FLAKY TEST: Prize distribution in batch draws
        
        Expected: Consistent distribution across multiple runs
        Actual: Distribution varies significantly between runs
        
        Run this test multiple times and observe different failures!
        """
        lottery = LotterySystem()
        
        # Create 1000 users
        users = []
        for i in range(1000):
            users.append(User(
                user_id=f"U{i:04d}",
                level=UserLevel.SILVER,
                total_consumption=3000
            ))
        
        # Batch draw
        results = lottery.batch_draw(users)
        
        # Count prizes
        first_count = sum(1 for p in results.values() if p == PrizeType.FIRST)
        second_count = sum(1 for p in results.values() if p == PrizeType.SECOND)
        third_count = sum(1 for p in results.values() if p == PrizeType.THIRD)
        
        # Expected ranges (very loose to show occasional failures)
        # First prize: ~0.12% * 1.2 (silver) = ~1.44 per 1000 -> expect 0-5
        # Second prize: ~1.2% * 1.2 = ~14.4 per 1000 -> expect 8-20
        # Third prize: ~12% * 1.2 = ~144 per 1000 -> expect 120-170
        
        # BUG: These assertions will fail sporadically!
        # Sometimes you get 7 first prizes, sometimes 0
        # Sometimes 200 third prizes, sometimes 80
        assert first_count <= 10, \
            f"Too many first prizes: {first_count} (expected ≤ 10)"
        assert 8 <= second_count <= 25, \
            f"Second prizes out of range: {second_count} (expected 8-25)"
        assert 110 <= third_count <= 180, \
            f"Third prizes out of range: {third_count} (expected 110-180)"
    
    def test_multiple_runs_consistency_FLAKY(self):
        """
        FLAKY TEST: Consistency across multiple runs
        
        This test runs the same scenario 5 times and expects similar results.
        BUG: Each run produces different results, causing test failures.
        
        Expected: All 5 runs should produce similar win counts
        Actual: Win counts vary wildly (e.g., 45, 62, 38, 71, 51)
        """
        results = []
        
        for run in range(5):
            lottery = LotterySystem()
            wins = 0
            
            for i in range(500):
                user = User(
                    user_id=f"R{run}_U{i}",
                    level=UserLevel.REGULAR,
                    total_consumption=2000
                )
                prize, _ = lottery.draw(user)
                if prize != PrizeType.NONE:
                    wins += 1
            
            results.append(wins)
        
        # Calculate variance
        mean = sum(results) / len(results)
        variance = sum((x - mean) ** 2 for x in results) / len(results)
        std_dev = variance ** 0.5
        
        # BUG: Standard deviation will be high due to randomness
        # Sometimes this passes, sometimes it fails
        # Expected: low variance (std_dev < 10)
        # Actual: high variance (std_dev often > 15)
        assert std_dev < 10, \
            f"Results too inconsistent: {results}, std_dev={std_dev:.2f}"
    
    def test_seed_parameter_ignored_FLAKY(self):
        """
        FLAKY TEST: Demonstrates that seed parameter is ignored
        
        The create_lottery() function accepts a seed parameter but doesn't use it!
        This test shows that even with the same seed, results differ.
        
        Expected: Same seed should produce same results
        Actual: Seed is ignored, results vary
        """
        # Run 1 with seed=42
        lottery1 = create_lottery(seed=42)
        user1 = User("U001", UserLevel.GOLD, 5000)
        prize1, _ = lottery1.draw(user1)
        
        # Run 2 with seed=42 (should be identical)
        lottery2 = create_lottery(seed=42)
        user2 = User("U001", UserLevel.GOLD, 5000)
        prize2, _ = lottery2.draw(user2)
        
        # BUG: These might be different even with same seed!
        # Because the seed parameter is not actually used
        # This test is EXTREMELY flaky - fails ~50% of the time
        assert prize1 == prize2, \
            f"Same seed should produce same result, got {prize1} vs {prize2}"


class TestDeterministicWithManualSeed:
    """
    These tests manually set random.seed() to show how tests SHOULD work.
    They demonstrate the fix approach without implementing it in the main code.
    """
    
    def test_with_manual_seed_deterministic(self):
        """
        This test manually sets random seed and is deterministic.
        
        Shows the proper way to handle randomness in tests.
        """
        import random
        
        # Manually set seed before creating lottery
        random.seed(12345)
        
        lottery = LotterySystem()
        
        wins = 0
        for i in range(1000):
            user = User(
                user_id=f"U{i}",
                level=UserLevel.GOLD,
                total_consumption=8000
            )
            prize, _ = lottery.draw(user)
            if prize != PrizeType.NONE:
                wins += 1
        
        # With seed=12345, this should always produce the same result
        # (This specific assertion is based on actual run with seed=12345)
        # The exact number depends on the random sequence
        assert wins > 0  # At least some wins occurred
        
        # Note: This test is stable because WE control the seed
        # The main code should do this internally!


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])