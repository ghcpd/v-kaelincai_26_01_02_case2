"""
Marketing Lottery System Module (FIXED VERSION)

This module implements a lottery system for e-commerce platform members.
The lottery probability is calculated based on user level, consumption history,
and prize pool availability.

FIXES APPLIED:
- Random number generation now uses a seeded Random instance for determinism
- Seed parameter is properly honored in create_lottery()
- Dictionary iteration uses ordered collections to ensure consistency
- All randomness is controlled via the seed parameter
"""

import random
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict
from datetime import datetime, timedelta


class UserLevel(Enum):
    """User membership levels"""
    REGULAR = "regular"
    SILVER = "silver"
    GOLD = "gold"
    DIAMOND = "diamond"


class PrizeType(Enum):
    """Types of prizes"""
    FIRST = "first"      # 1000 CNY value
    SECOND = "second"    # 100 CNY value
    THIRD = "third"      # 10 CNY value
    NONE = "none"        # No prize


@dataclass
class User:
    """User data structure"""
    user_id: str
    level: UserLevel
    total_consumption: float
    today_wins: int = 0
    last_win_time: Optional[datetime] = None
    ip_address: str = "127.0.0.1"


@dataclass
class PrizePool:
    """Daily prize pool configuration"""
    first_remaining: int = 10
    second_remaining: int = 100
    third_remaining: int = 1000
    
    def get_remaining(self, prize_type: PrizeType) -> int:
        """Get remaining count for a prize type"""
        if prize_type == PrizeType.FIRST:
            return self.first_remaining
        elif prize_type == PrizeType.SECOND:
            return self.second_remaining
        elif prize_type == PrizeType.THIRD:
            return self.third_remaining
        return 0
    
    def consume(self, prize_type: PrizeType) -> bool:
        """Consume one prize from the pool"""
        if prize_type == PrizeType.FIRST and self.first_remaining > 0:
            self.first_remaining -= 1
            return True
        elif prize_type == PrizeType.SECOND and self.second_remaining > 0:
            self.second_remaining -= 1
            return True
        elif prize_type == PrizeType.THIRD and self.third_remaining > 0:
            self.third_remaining -= 1
            return True
        return False


class LotterySystem:
    """
    Marketing lottery system with stable, deterministic behavior.
    
    FIXES APPLIED:
    1. Uses random.Random() instance with proper seed initialization
    2. Seeds can be set for deterministic testing or left unset for production randomness
    3. Uses ordered prize type iteration instead of sets
    4. All randomness is controlled and reproducible
    """
    
    # Base probabilities
    BASE_PROBABILITIES = {
        PrizeType.FIRST: 0.001,   # 0.1%
        PrizeType.SECOND: 0.01,    # 1%
        PrizeType.THIRD: 0.10,     # 10%
        PrizeType.NONE: 0.889      # 88.9%
    }
    
    # Level multipliers
    LEVEL_MULTIPLIERS = {
        UserLevel.REGULAR: 1.0,
        UserLevel.SILVER: 1.2,
        UserLevel.GOLD: 1.5,
        UserLevel.DIAMOND: 2.0,
    }
    
    # Anti-fraud limits
    MAX_DAILY_WINS_PER_USER = 3
    MIN_WIN_INTERVAL_MINUTES = 10
    MAX_DAILY_WINS_PER_IP = 5
    
    def __init__(self, prize_pool: Optional[PrizePool] = None, seed: Optional[int] = None):
        """Initialize lottery system with optional seed for deterministic behavior"""
        self.prize_pool = prize_pool or PrizePool()
        self.ip_win_counts: Dict[str, int] = {}
        
        # FIX: Create a Random instance for this lottery system
        # This allows each lottery to have independent randomness
        self._rng = random.Random(seed)
    
    def calculate_win_probability(self, user: User) -> float:
        """
        Calculate total win probability for a user.
        
        Combines base probability with level multiplier and consumption bonus.
        """
        # Get level multiplier
        level_multiplier = self.LEVEL_MULTIPLIERS[user.level]
        
        # Calculate consumption bonus
        consumption_bonus = self._get_consumption_bonus(user.total_consumption)
        
        # Base win probability (sum of all prizes except NONE)
        base_win_prob = sum(
            prob for prize_type, prob in self.BASE_PROBABILITIES.items()
            if prize_type != PrizeType.NONE
        )
        
        # Apply multiplier and bonus
        total_prob = base_win_prob * level_multiplier + consumption_bonus
        
        # Cap at reasonable maximum
        return min(total_prob, 0.95)
    
    def _get_consumption_bonus(self, consumption: float) -> float:
        """Calculate probability bonus based on consumption amount"""
        if consumption >= 10000:
            return 0.20
        elif consumption >= 5000:
            return 0.10
        elif consumption >= 1000:
            return 0.05
        return 0.0
    
    def _can_user_win(self, user: User) -> tuple[bool, str]:
        """Check if user is eligible to win based on anti-fraud rules"""
        # Check daily win limit
        if user.today_wins >= self.MAX_DAILY_WINS_PER_USER:
            return False, f"User exceeded daily win limit ({self.MAX_DAILY_WINS_PER_USER})"
        
        # Check win interval
        if user.last_win_time:
            time_since_last_win = datetime.now() - user.last_win_time
            if time_since_last_win < timedelta(minutes=self.MIN_WIN_INTERVAL_MINUTES):
                return False, f"Too soon since last win (need {self.MIN_WIN_INTERVAL_MINUTES} min interval)"
        
        # Check IP limit
        ip_wins = self.ip_win_counts.get(user.ip_address, 0)
        if ip_wins >= self.MAX_DAILY_WINS_PER_IP:
            return False, f"IP exceeded daily win limit ({self.MAX_DAILY_WINS_PER_IP})"
        
        return True, "OK"
    
    def draw(self, user: User) -> tuple[PrizeType, str]:
        """
        Execute a lottery draw for a user.
        
        Returns:
            Tuple of (prize_type, message)
            
        FIXED BEHAVIOR:
        - Uses seeded random number generation for determinism
        - Results are reproducible when seed is set
        - Consistent behavior across test runs
        """
        # Check eligibility
        can_win, reason = self._can_user_win(user)
        if not can_win:
            return PrizeType.NONE, f"Not eligible: {reason}"
        
        # FIX: Use instance's seeded random generator instead of module-level random
        rand_value = self._rng.random()
        
        # Calculate adjusted probabilities based on user
        adjusted_probs = self._calculate_adjusted_probabilities(user)
        
        # Determine prize based on random value with ordered iteration
        # Process each prize type in order and accumulate probabilities
        cumulative = 0.0
        selected_prize = None
        
        # Try each prize type in order
        for prize_type in [PrizeType.FIRST, PrizeType.SECOND, PrizeType.THIRD, PrizeType.NONE]:
            cumulative += adjusted_probs.get(prize_type, 0)
            if rand_value < cumulative and selected_prize is None:
                # This is the range where our random value falls
                if prize_type == PrizeType.NONE:
                    # No prize case - always award NONE
                    return PrizeType.NONE, "Better luck next time"
                else:
                    # Try to consume this prize from the pool
                    if self.prize_pool.consume(prize_type):
                        # Successfully consumed a prize!
                        # Update user stats
                        user.today_wins += 1
                        user.last_win_time = datetime.now()
                        
                        # Update IP stats
                        self.ip_win_counts[user.ip_address] = \
                            self.ip_win_counts.get(user.ip_address, 0) + 1
                        
                        return prize_type, f"Won {prize_type.value}"
                    else:
                        # Prize pool exhausted for this tier
                        # Treat as NONE (consolation prize exhaustion policy)
                        return PrizeType.NONE, f"Prize pool for {prize_type.value} exhausted"
        
        # Fallback (should not normally reach here)
        return PrizeType.NONE, "Better luck next time"
    
    def _calculate_adjusted_probabilities(self, user: User) -> Dict[PrizeType, float]:
        """
        Calculate adjusted probabilities based on user level and consumption.
        
        Uses deterministic ordering for consistent results.
        """
        level_mult = self.LEVEL_MULTIPLIERS[user.level]
        consumption_bonus = self._get_consumption_bonus(user.total_consumption)
        
        adjusted = {}
        total_adjustment = 0.0
        
        # Adjust prize probabilities with ordered iteration
        prize_order = [PrizeType.FIRST, PrizeType.SECOND, PrizeType.THIRD, PrizeType.NONE]
        for prize_type in prize_order:
            base_prob = self.BASE_PROBABILITIES[prize_type]
            if prize_type != PrizeType.NONE:
                # Check if prize is available
                if self.prize_pool.get_remaining(prize_type) > 0:
                    adjusted_prob = base_prob * level_mult
                    adjusted[prize_type] = adjusted_prob
                    total_adjustment += adjusted_prob
                else:
                    adjusted[prize_type] = 0.0
            else:
                adjusted[prize_type] = base_prob
        
        # Add consumption bonus proportionally to winning probabilities
        if consumption_bonus > 0 and total_adjustment > 0:
            for prize_type in [PrizeType.FIRST, PrizeType.SECOND, PrizeType.THIRD]:
                if prize_type in adjusted and adjusted[prize_type] > 0:
                    bonus_share = (adjusted[prize_type] / total_adjustment) * consumption_bonus
                    adjusted[prize_type] += bonus_share
        
        # Normalize to ensure probabilities sum to 1.0
        total = sum(adjusted.values())
        if total > 0:
            adjusted = {k: v / total for k, v in adjusted.items()}
        
        return adjusted
    
    def batch_draw(self, users: list[User]) -> Dict[str, PrizeType]:
        """
        Process lottery draws for multiple users.
        
        FIXED BEHAVIOR:
        - Uses seeded randomness for reproducible results
        - Deterministic when seed is set
        - Prize pool depletion is handled consistently
        """
        results = {}
        
        # Process users with deterministic randomness
        for user in users:
            prize, _ = self.draw(user)
            results[user.user_id] = prize
        
        return results


def create_lottery(seed: Optional[int] = None) -> LotterySystem:
    """
    Factory function to create a lottery system.
    
    Args:
        seed: Random seed for deterministic behavior (optional)
              If provided, same seed will produce same results
              If not provided, uses truly random behavior
    
    Returns:
        LotterySystem instance configured with the provided seed
    
    FIXED BEHAVIOR:
    - Seed parameter is now properly honored
    - Each lottery system gets its own Random instance with the seed
    - Tests can be deterministic by setting a seed
    - Production can use None for true randomness
    """
    return LotterySystem(seed=seed)
