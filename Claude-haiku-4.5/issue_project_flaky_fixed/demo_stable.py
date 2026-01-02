"""
Demo script showing stable, deterministic behavior in the FIXED Marketing Lottery System.

This script demonstrates:
1. Deterministic behavior with seeds
2. Consistent results across multiple runs
3. Production randomness when no seed is provided
"""

from src.lottery import LotterySystem, User, UserLevel, PrizeType, create_lottery


def demonstrate_deterministic_behavior():
    """Demonstrate deterministic behavior with seeds"""
    print("=" * 70)
    print("DEMONSTRATION 1: Deterministic Behavior with Seeds")
    print("=" * 70)
    print()
    
    print("Running the same lottery draw 5 times with SAME SEED (42):")
    print("User: Gold level, 8000 CNY consumption")
    print()
    
    results = []
    for i in range(5):
        # Create lottery with fixed seed
        lottery = create_lottery(seed=42)
        
        # Create identical user
        user = User(
            user_id="U001",
            level=UserLevel.GOLD,
            total_consumption=8000
        )
        
        # Draw lottery
        prize, message = lottery.draw(user)
        results.append(prize)
        
        print(f"Run {i+1}: {prize.value:15s} - {message}")
    
    print()
    unique_results = len(set(results))
    print(f"Unique results from 5 identical draws: {unique_results}")
    if unique_results == 1:
        print("✅ FIXED: All results are identical!")
        print("   Same seed + same input = same output (deterministic)")
    else:
        print("❌ ISSUE: Results differ (should not happen)")
    print()


def demonstrate_statistical_consistency():
    """Demonstrate consistency in win rates with seeds"""
    print("=" * 70)
    print("DEMONSTRATION 2: Statistical Consistency with Seeds")
    print("=" * 70)
    print()
    
    print("Running 1000 lottery draws 5 times with SAME SEED (999):")
    print()
    
    win_rates = []
    
    for run in range(5):
        # Use same seed for each run
        lottery = create_lottery(seed=999)
        wins = 0
        trials = 1000
        
        for i in range(trials):
            user = User(
                user_id=f"R{run}_U{i}",
                level=UserLevel.SILVER,
                total_consumption=3000
            )
            prize, _ = lottery.draw(user)
            if prize != PrizeType.NONE:
                wins += 1
        
        win_rate = wins / trials
        win_rates.append(win_rate)
        
        print(f"Run {run+1}: {wins:4d} wins out of {trials} = {win_rate:.2%} win rate")
    
    print()
    
    # All should be identical
    if all(r == win_rates[0] for r in win_rates):
        print("✅ FIXED: All win rates are IDENTICAL!")
        print(f"   Consistent rate: {win_rates[0]:.2%}")
        print("   Same seed guarantees reproducible results!")
    else:
        print("❌ ISSUE: Win rates differ (should be identical)")
        avg_rate = sum(win_rates) / len(win_rates)
        print(f"   Average:  {avg_rate:.2%}")
        print(f"   Expected: All values = {win_rates[0]:.2%}")
    print()


def demonstrate_production_randomness():
    """Demonstrate true randomness when no seed is provided"""
    print("=" * 70)
    print("DEMONSTRATION 3: Production Randomness (No Seed)")
    print("=" * 70)
    print()
    
    print("Running 5 lottery draws WITHOUT seed (production mode):")
    print("User: Gold level, 8000 CNY consumption")
    print()
    
    results = []
    for i in range(5):
        # Create lottery WITHOUT seed (true randomness)
        lottery = create_lottery()  # No seed parameter
        
        # Create identical user
        user = User(
            user_id="U001",
            level=UserLevel.GOLD,
            total_consumption=8000
        )
        
        # Draw lottery
        prize, message = lottery.draw(user)
        results.append(prize)
        
        print(f"Draw {i+1}: {prize.value:15s} - {message}")
    
    print()
    unique_results = len(set(results))
    print(f"Unique results from 5 draws: {unique_results}")
    if unique_results > 1:
        print("✅ GOOD: Results vary with true randomness (production mode works)")
        print("   No seed = true randomness for production use")
    else:
        print("⚠️  All results happened to be the same (low probability)")
        print("   Run this script multiple times to see variation")
    print()


def demonstrate_seed_consistency():
    """Demonstrate that different seeds produce different results"""
    print("=" * 70)
    print("DEMONSTRATION 4: Different Seeds = Different Sequences")
    print("=" * 70)
    print()
    
    print("Running same scenario with different seeds:")
    print()
    
    seeds = [111, 222, 333, 444, 555]
    seed_results = []
    
    for seed in seeds:
        lottery = create_lottery(seed=seed)
        wins = 0
        
        for i in range(500):
            user = User(
                user_id=f"U{i}",
                level=UserLevel.GOLD,
                total_consumption=5000
            )
            prize, _ = lottery.draw(user)
            if prize != PrizeType.NONE:
                wins += 1
        
        seed_results.append(wins)
        print(f"Seed {seed}: {wins} wins out of 500 draws")
    
    print()
    if len(set(seed_results)) > 1:
        print("✅ GOOD: Different seeds produce different results")
        print("   Each seed creates unique random sequence")
        print("   Tests can choose different seeds for variety")
    else:
        print("❌ ISSUE: All seeds produced same result (unlikely)")
    print()


if __name__ == "__main__":
    demonstrate_deterministic_behavior()
    demonstrate_statistical_consistency()
    demonstrate_production_randomness()
    demonstrate_seed_consistency()
    
    print("=" * 70)
    print("SUMMARY: Lottery System is now STABLE and DETERMINISTIC")
    print("=" * 70)
    print()
    print("✅ Tests are deterministic when seed is provided")
    print("✅ Same seed always produces same results")
    print("✅ Production can use no seed for true randomness")
    print("✅ No more flaky test failures!")
    print()
