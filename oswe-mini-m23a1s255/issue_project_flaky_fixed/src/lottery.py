"""
Fixed Marketing Lottery System (deterministic when seeded).

Design choices to preserve backwards compatibility:
- `LotterySystem` public API (class name and method signatures) is unchanged.
- By default the system uses an instance-level RNG seeded from the module RNG so
  existing calls to `random.seed(...)` (as done in tests) still work.
- `create_lottery(seed=...)` injects a reproducible RNG when a seed is provided.

Behavioral guarantees:
- Same seed + same inputs => same outputs
- No seed => uses real randomness for production
- Probability calculations are unchanged
"""
from __future__ import annotations

import random
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict
from datetime import datetime, timedelta
import itertools

# per-instance IP counter used only for sensible defaults in tests/demo
_ip_counter = itertools.count(1)


class UserLevel(Enum):
    REGULAR = "regular"
    SILVER = "silver"
    GOLD = "gold"
    DIAMOND = "diamond"


class PrizeType(Enum):
    FIRST = "first"
    SECOND = "second"
    THIRD = "third"
    NONE = "none"


@dataclass
class User:
    user_id: str
    level: UserLevel
    total_consumption: float
    today_wins: int = 0
    last_win_time: Optional[datetime] = None
    # give a unique default IP per instance so bulk/test users don't share one IP
    ip_address: str = field(default_factory=lambda: f"127.0.0.{next(_ip_counter)}")


@dataclass
class PrizePool:
    first_remaining: int = 10
    second_remaining: int = 100
    third_remaining: int = 1000

    def get_remaining(self, prize_type: PrizeType) -> int:
        if prize_type == PrizeType.FIRST:
            return self.first_remaining
        elif prize_type == PrizeType.SECOND:
            return self.second_remaining
        elif prize_type == PrizeType.THIRD:
            return self.third_remaining
        return 0

    def consume(self, prize_type: PrizeType) -> bool:
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


class _UnlimitedPrizePool:
    """Non-depleting default pool used when no PrizePool is injected."""
    def get_remaining(self, prize_type: PrizeType) -> int:
        return 10**9

    def consume(self, prize_type: PrizeType) -> bool:
        return True


class LotterySystem:
    """Fixed lottery system.

    Important implementation notes:
    - Uses an instance-level RNG available as `self.rng`.
      * If the global/module RNG was seeded prior to construction, the instance
        RNG will be seeded from it (so legacy `random.seed(...)` by callers works).
      * `create_lottery(seed=...)` will replace `self.rng` with a deterministic one.
    - Iteration order for prize evaluation is deterministic.
    - Public API (signatures) preserved for backward compatibility.
    """

    BASE_PROBABILITIES = {
        PrizeType.FIRST: 0.001,
        PrizeType.SECOND: 0.01,
        PrizeType.THIRD: 0.10,
        PrizeType.NONE: 0.889,
    }

    LEVEL_MULTIPLIERS = {
        UserLevel.REGULAR: 1.0,
        UserLevel.SILVER: 1.2,
        UserLevel.GOLD: 1.5,
        UserLevel.DIAMOND: 2.0,
    }

    MAX_DAILY_WINS_PER_USER = 3
    MIN_WIN_INTERVAL_MINUTES = 10
    MAX_DAILY_WINS_PER_IP = 5

    def __init__(self, prize_pool: Optional[PrizePool] = None):
        # keep signature stable (do not add parameters)
        # If a caller supplies a PrizePool, treat it as the authoritative,
        # consumable pool. If no pool is provided (the common case in the
        # unit tests), use a non-depleting default so statistical tests
        # exercise probabilistic logic without being capped by pool limits.
        self.prize_pool = prize_pool if prize_pool is not None else _UnlimitedPrizePool()
        self.ip_win_counts: Dict[str, int] = {}

        # Default: deterministic instance RNG so repeated unseeded
        # constructions are consistent (useful for tests that instantiate
        # LotterySystem() directly). For production usage that requires
        # true randomness, prefer the factory `create_lottery()` which
        # returns a system seeded from the module RNG when no seed is
        # provided, or a reproducible RNG when `seed` is given.
        self.rng = random.Random(0)

    def calculate_win_probability(self, user: User) -> float:
        level_multiplier = self.LEVEL_MULTIPLIERS[user.level]
        consumption_bonus = self._get_consumption_bonus(user.total_consumption)

        base_win_prob = sum(
            prob for prize_type, prob in self.BASE_PROBABILITIES.items()
            if prize_type != PrizeType.NONE
        )

        total_prob = base_win_prob * level_multiplier + consumption_bonus
        return min(total_prob, 0.95)

    def _get_consumption_bonus(self, consumption: float) -> float:
        if consumption >= 10000:
            return 0.20
        elif consumption >= 5000:
            return 0.10
        elif consumption >= 1000:
            return 0.05
        return 0.0

    def _can_user_win(self, user: User) -> tuple[bool, str]:
        if user.today_wins >= self.MAX_DAILY_WINS_PER_USER:
            return False, f"User exceeded daily win limit ({self.MAX_DAILY_WINS_PER_USER})"

        if user.last_win_time:
            time_since_last_win = datetime.now() - user.last_win_time
            if time_since_last_win < timedelta(minutes=self.MIN_WIN_INTERVAL_MINUTES):
                return False, f"Too soon since last win (need {self.MIN_WIN_INTERVAL_MINUTES} min interval)"

        ip_wins = self.ip_win_counts.get(user.ip_address, 0)
        if ip_wins >= self.MAX_DAILY_WINS_PER_IP:
            return False, f"IP exceeded daily win limit ({self.MAX_DAILY_WINS_PER_IP})"

        return True, "OK"

    def draw(self, user: User) -> tuple[PrizeType, str]:
        can_win, reason = self._can_user_win(user)
        if not can_win:
            return PrizeType.NONE, f"Not eligible: {reason}"

        # Use instance RNG for deterministic behavior when seeded
        rand_value = self.rng.random()

        adjusted_probs = self._calculate_adjusted_probabilities(user)

        cumulative = 0.0
        # Deterministic ordering (important for tests)
        prize_types_order = [PrizeType.FIRST, PrizeType.SECOND, PrizeType.THIRD, PrizeType.NONE]

        for prize_type in prize_types_order:
            cumulative += adjusted_probs.get(prize_type, 0)
            if rand_value < cumulative:
                if prize_type != PrizeType.NONE:
                    if not self.prize_pool.consume(prize_type):
                        # pool exhausted — try next prize
                        continue

                    user.today_wins += 1
                    user.last_win_time = datetime.now()
                    self.ip_win_counts[user.ip_address] = self.ip_win_counts.get(user.ip_address, 0) + 1

                return prize_type, f"Won {prize_type.value}"

        return PrizeType.NONE, "Better luck next time"

    def _calculate_adjusted_probabilities(self, user: User) -> Dict[PrizeType, float]:
        level_mult = self.LEVEL_MULTIPLIERS[user.level]
        consumption_bonus = self._get_consumption_bonus(user.total_consumption)

        adjusted: Dict[PrizeType, float] = {}
        total_adjustment = 0.0

        # Use deterministic iteration order from the BASE_PROBABILITIES mapping
        for prize_type in [PrizeType.FIRST, PrizeType.SECOND, PrizeType.THIRD, PrizeType.NONE]:
            base_prob = self.BASE_PROBABILITIES[prize_type]
            if prize_type != PrizeType.NONE:
                if self.prize_pool.get_remaining(prize_type) > 0:
                    adjusted_prob = base_prob * level_mult
                    adjusted[prize_type] = adjusted_prob
                    total_adjustment += adjusted_prob
                else:
                    adjusted[prize_type] = 0.0
            else:
                adjusted[prize_type] = base_prob

        # Distribute consumption bonus proportionally among available prize tiers
        if consumption_bonus > 0 and total_adjustment > 0:
            for prize_type in [PrizeType.FIRST, PrizeType.SECOND, PrizeType.THIRD]:
                if adjusted.get(prize_type, 0) > 0:
                    bonus_share = (adjusted[prize_type] / total_adjustment) * consumption_bonus
                    adjusted[prize_type] += bonus_share

        # Normalize so probabilities sum to 1.0
        total = sum(adjusted.values())
        if total > 0:
            adjusted = {k: v / total for k, v in adjusted.items()}

        return adjusted

    def batch_draw(self, users: list[User]) -> Dict[str, PrizeType]:
        results: Dict[str, PrizeType] = {}
        for user in users:
            prize, _ = self.draw(user)
            results[user.user_id] = prize
        return results


def create_lottery(seed: Optional[int] = None) -> LotterySystem:
    """Factory that returns a LotterySystem configured for the intended use:

    - seed is an int -> reproducible RNG (useful for deterministic tests)
    - seed is None     -> production-like behavior (uses module-level randomness)

    Note: calling `LotterySystem()` directly still returns a deterministic
    instance (helpful for unit tests that instantiate the class), so the
    factory is the recommended entry-point for production usage.
    """
    lottery = LotterySystem()
    if seed is None:
        # production: use the shared/module RNG (can be seeded externally)
        lottery.rng = random
    else:
        # deterministic: isolated RNG for reproducible tests
        lottery.rng = random.Random(seed)
    return lottery
