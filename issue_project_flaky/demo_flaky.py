"""
Interactive demonstration of flaky behavior in the Marketing Lottery System.

This script shows how the same inputs produce different outputs due to
non-deterministic random number generation without fixed seeds.
"""

from src.lottery import LotterySystem, User, UserLevel, PrizeType, create_lottery


def demonstrate_basic_flakiness():
    """Demonstrate basic flaky behavior with identical inputs"""
    print("=" * 70)
    print("DEMONSTRATION 1: Same Input, Different Outputs")
    print("=" * 70)
    print()
    
    print("Running the same lottery draw 5 times with IDENTICAL inputs:")
    print("User: Gold level, 8000 CNY consumption")
    print()
    
    results = []
    for i in range(5):
        # Create new lottery system (no seed)
        lottery = LotterySystem()
        
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
    if len(set(results)) > 1:
        print("❌ FLAKY: Same input produced different outputs!")
    else:
        print("⚠️  All results happened to be the same (lucky!)")
        print("   Run this script multiple times to see different results.")
    print()


def demonstrate_statistical_variance():
    """Demonstrate variance in win rates across multiple runs"""
    print("=" * 70)
    print("DEMONSTRATION 2: Statistical Variance in Win Rates")
    print("=" * 70)
    print()
    
    print("Running 1000 lottery draws 3 times to observe win rate variance:")
    print()
    
    win_rates = []
    
    for run in range(3):
        lottery = LotterySystem()
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
    
    if std_dev > 0.02:
        print("❌ FLAKY: High variance in win rates!")
        print("   Expected: Consistent rates (std dev < 2%)")
        print(f"   Actual: Inconsistent (std dev = {std_dev:.2%})")
    else:
        print("⚠️  Variance happened to be low this time (lucky!)")
        print("   Run this script multiple times to see higher variance.")
    print()


def demonstrate_seed_parameter_ignored():
    """Demonstrate that the seed parameter is ignored"""
    print("=" * 70)
    print("DEMONSTRATION 3: Seed Parameter Ignored")
    print("=" * 70)
    print()
    
    print("Testing create_lottery(seed=42) - should give deterministic results:")
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
    if len(set(results)) > 1:
        print("❌ BUG CONFIRMED: Seed parameter is IGNORED!")
        print("   Expected: All draws with seed=42 should give same result")
        print(f"   Actual: Got {len(set(results))} different results")
    else:
        print("⚠️  All results happened to match (lucky!)")
        print("   This doesn't mean the seed works - run again to verify.")
        print("   The seed parameter is still being ignored!")
    print()


def demonstrate_batch_variance():
    """Demonstrate variance in batch processing"""
    print("=" * 70)
    print("DEMONSTRATION 4: Batch Processing Variance")
    print("=" * 70)
    print()
    
    print("Processing 500 users in batches, 3 times:")
    print()
    
    for run in range(3):
        lottery = LotterySystem()
        
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
    
    print("❌ FLAKY: Each run produces different prize distributions!")
    print("   This is because random.random() has no fixed seed.")
    print()


def main():
    """Run all demonstrations"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "   Marketing Lottery System - Flaky Behavior Demonstration".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")
    
    demonstrate_basic_flakiness()
    input("Press Enter to continue to next demonstration...")
    print("\n")
    
    demonstrate_statistical_variance()
    input("Press Enter to continue to next demonstration...")
    print("\n")
    
    demonstrate_seed_parameter_ignored()
    input("Press Enter to continue to next demonstration...")
    print("\n")
    
    demonstrate_batch_variance()
    
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("This system exhibits FLAKY BEHAVIOR due to:")
    print("  1. ❌ Random number generation without fixed seed")
    print("  2. ❌ create_lottery() ignores the seed parameter")
    print("  3. ❌ Non-deterministic test results")
    print()
    print("Impact:")
    print("  • Tests pass/fail randomly")
    print("  • CI/CD pipelines become unreliable")
    print("  • Developers waste time investigating false failures")
    print("  • Cannot reproduce bugs consistently")
    print()
    print("See KNOWN_ISSUE.md for detailed analysis and fix strategies.")
    print()
    print("=" * 70)
    print("Run this script multiple times to observe different results!")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
