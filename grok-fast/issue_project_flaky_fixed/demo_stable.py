"""
Interactive demonstration of STABLE behavior in the Fixed Marketing Lottery System.

This script shows how the same inputs now produce consistent outputs due to
deterministic random number generation with seed control.
"""

from src.lottery import LotterySystem, User, UserLevel, PrizeType, create_lottery


def demonstrate_basic_stability():
    """Demonstrate basic stable behavior with identical inputs"""
    print("=" * 70)
    print("DEMONSTRATION 1: Same Input, Consistent Outputs")
    print("=" * 70)
    print()
    
    print("Running the same lottery draw 5 times with IDENTICAL inputs:")
    print("User: Gold level, 8000 CNY consumption")
    print("Using seeded lottery for deterministic results")
    print()
    
    results = []
    for i in range(5):
        # Create seeded lottery system
        lottery = create_lottery(seed=12345)
        
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
    print(f"Unique results from 5 identical draws: {len(set(results))}")
    if len(set(results)) == 1:
        print("✅ STABLE: Same input produced identical outputs!")
        print("   The seed parameter now works correctly.")
    else:
        print("❌ ERROR: Results should be identical with same seed!")
    print()


def demonstrate_statistical_consistency():
    """Demonstrate consistency in win rates across multiple runs"""
    print("=" * 70)
    print("DEMONSTRATION 2: Statistical Consistency in Win Rates")
    print("=" * 70)
    print()
    
    print("Running 1000 lottery draws 3 times with SAME SEED:")
    print()
    
    win_rates = []
    
    for run in range(3):
        # FIXED: Use same seed for consistency
        lottery = create_lottery(seed=67890)
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
    avg_rate = sum(win_rates) / len(win_rates)
    variance = sum((r - avg_rate) ** 2 for r in win_rates) / len(win_rates)
    std_dev = variance ** 0.5
    
    print(f"Average:  {avg_rate:.2%}")
    print(f"Std Dev:  {std_dev:.2%}")
    print(f"Range:    {min(win_rates):.2%} - {max(win_rates):.2%}")
    print()
    
    if std_dev < 0.001:
        print("✅ STABLE: Identical win rates across runs!")
        print("   Same seed produces identical results.")
    else:
        print("❌ ERROR: Win rates should be identical with same seed!")
    print()


def demonstrate_seed_parameter_works():
    """Demonstrate that the seed parameter now works correctly"""
    print("=" * 70)
    print("DEMONSTRATION 3: Seed Parameter Now Works")
    print("=" * 70)
    print()
    
    print("Testing create_lottery(seed=42) - gives deterministic results:")
    print()
    
    results = []
    for i in range(3):
        # Create lottery with same seed
        lottery = create_lottery(seed=42)
        
        # Create identical user
        user = User(
            user_id="U001",
            level=UserLevel.GOLD,
            total_consumption=5000
        )
        
        # Draw lottery
        prize, _ = lottery.draw(user)
        results.append(prize)
        
        print(f"Draw {i+1} (seed=42): {prize.value}")
    
    print()
    if len(set(results)) == 1:
        print("✅ FIXED: Seed parameter now WORKS correctly!")
        print("   All draws with seed=42 give the same result.")
    else:
        print("❌ ERROR: All results should be identical with same seed!")
    print()


def demonstrate_batch_consistency():
    """Demonstrate consistency in batch processing"""
    print("=" * 70)
    print("DEMONSTRATION 4: Batch Processing Consistency")
    print("=" * 70)
    print()
    
    print("Processing 500 users in batches, 3 times with SAME SEED:")
    print()
    
    all_results = []
    
    for run in range(3):
        # FIXED: Use same seed for consistency
        lottery = create_lottery(seed=11111)
        
        # Create 500 identical users
        users = []
        for i in range(500):
            users.append(User(
                user_id=f"R{run}_U{i}",
                level=UserLevel.REGULAR,
                total_consumption=2000
            ))
        
        # Batch process
        results = lottery.batch_draw(users)
        all_results.append(results)
        
        # Count prizes
        prize_counts = {
            PrizeType.FIRST: 0,
            PrizeType.SECOND: 0,
            PrizeType.THIRD: 0,
            PrizeType.NONE: 0
        }
        
        for prize in results.values():
            prize_counts[prize] += 1
        
        total_wins = sum(c for p, c in prize_counts.items() if p != PrizeType.NONE)
        
        print(f"Run {run+1}:")
        print(f"  First:  {prize_counts[PrizeType.FIRST]:3d}")
        print(f"  Second: {prize_counts[PrizeType.SECOND]:3d}")
        print(f"  Third:  {prize_counts[PrizeType.THIRD]:3d}")
        print(f"  None:   {prize_counts[PrizeType.NONE]:3d}")
        print(f"  Total wins: {total_wins} ({total_wins/500:.1%})")
        print()
    
    # Check if all batch results are identical
    identical = all(results == all_results[0] for results in all_results)
    
    if identical:
        print("✅ STABLE: All batch runs produced identical results!")
        print("   Same seed ensures deterministic batch processing.")
    else:
        print("❌ ERROR: Batch results should be identical with same seed!")
    print()


def demonstrate_production_randomness():
    """Demonstrate that production can still be random"""
    print("=" * 70)
    print("DEMONSTRATION 5: Production Randomness Still Available")
    print("=" * 70)
    print()
    
    print("Running draws with NO SEED (production mode):")
    print()
    
    results = []
    for i in range(5):
        # Create lottery WITHOUT seed (random)
        lottery = LotterySystem()  # No seed parameter
        
        user = User(
            user_id="U001",
            level=UserLevel.GOLD,
            total_consumption=8000
        )
        
        prize, message = lottery.draw(user)
        results.append(prize)
        
        print(f"Run {i+1} (no seed): {prize.value:15s} - {message}")
    
    print()
    print(f"Unique results from 5 draws: {len(set(results))}")
    if len(set(results)) > 1:
        print("✅ GOOD: Without seed, results are still random for production!")
        print("   This maintains the lottery's randomness in real usage.")
    else:
        print("⚠️  All results happened to be the same (rare coincidence)")
        print("   Without seed, results should typically vary.")
    print()


def main():
    """Run all demonstrations"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "   Marketing Lottery System - STABLE Behavior Demonstration".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")
    
    demonstrate_basic_stability()
    input("Press Enter to continue to next demonstration...")
    print("\n")
    
    demonstrate_statistical_consistency()
    input("Press Enter to continue to next demonstration...")
    print("\n")
    
    demonstrate_seed_parameter_works()
    input("Press Enter to continue to next demonstration...")
    print("\n")
    
    demonstrate_batch_consistency()
    input("Press Enter to continue to next demonstration...")
    print("\n")
    
    demonstrate_production_randomness()
    
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("This FIXED system exhibits STABLE BEHAVIOR:")
    print("  1. ✅ Random number generation with seed control")
    print("  2. ✅ create_lottery() properly uses the seed parameter")
    print("  3. ✅ Deterministic test results when seeded")
    print("  4. ✅ Production randomness when no seed provided")
    print()
    print("Benefits:")
    print("  • Tests pass consistently with seeds")
    print("  • CI/CD pipelines are reliable")
    print("  • Developers can reproduce bugs easily")
    print("  • Production maintains lottery randomness")
    print()
    print("See FIX_REPORT.md for detailed fix documentation.")
    print()
    print("=" * 70)
    print("Run tests multiple times - they will always pass!")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()