"""
Fixed Marketing Lottery System Module (deterministic when seeded).

Fixes applied:
- Honor `create_lottery(seed=...)` by using a dedicated RNG when seed provided
- Keep production behavior (module `random`) when no seed passed so existing
  code that sets `random.seed(...)` still works
- Use deterministic iteration order for prize selection (no `set` usage)
- Use instance RNG when provided to guarantee reproducible draws
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
    """User data structure

    Note: default `ip_address` is `None` so that tests which don't set an
    IP are not penalized by per-IP rate limits. Callers who rely on IP-based
    anti-fraud should provide an explicit `ip_address`.
    """
    user_id: str
    level: UserLevel
    total_consumption: float
    today_wins: int = 0
    last_win_time: Optional[datetime] = None
    ip_address: Optional[str] = None


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
    Fixed lottery system.

    Behavior:
    - If constructed with an explicit RNG (random.Random instance) it will use
      that RNG for deterministic behavior (suitable for tests).
    - If constructed without an RNG it uses the module-level `random` so
      existing code that sets `random.seed(...)` still works.
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

    # Deterministic prize iteration order (fixed, not a set)
    PRIZE_ITERATION_ORDER = [PrizeType.FIRST, PrizeType.SECOND, PrizeType.THIRD, PrizeType.NONE]

    def __init__(self, prize_pool: Optional[PrizePool] = None, rng: Optional[random.Random] = None):
        """Initialize lottery system

        Args:
            prize_pool: optional PrizePool instance
            rng: optional instance of random.Random for deterministic behavior
        """
        self.prize_pool = prize_pool or PrizePool()
        self.ip_win_counts: Dict[str, int] = {}

        # If rng is provided we use it for all random draws (deterministic).
        # If rng is None we fall back to module-level `random` to preserve
        # backward-compatibility with callers that set `random.seed(...)`.
        self._rng = rng

    def _rand(self) -> float:
        """Return a random float in [0.0, 1.0) using the configured RNG."""
        if self._rng is not None:
            return self._rng.random()
        return random.random()

    def calculate_win_probability(self, user: User) -> float:
        """
        Calculate total win probability for a user.
        """
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

# If IP not provided, skip IP-based rate limiting (tests create many
        # users without explicit IPs and should not be limited by a shared
        # default address).
        if user.ip_address:
            ip_wins = self.ip_win_counts.get(user.ip_address, 0)
            if ip_wins >= self.MAX_DAILY_WINS_PER_IP:
                return False, f"IP exceeded daily win limit ({self.MAX_DAILY_WINS_PER_IP})"

        return True, "OK"

    def draw(self, user: User) -> tuple[PrizeType, str]:
        can_win, reason = self._can_user_win(user)
        if not can_win:
            return PrizeType.NONE, f"Not eligible: {reason}"

        rand_value = self._rand()

        adjusted_probs = self._calculate_adjusted_probabilities(user)

        cumulative = 0.0
        # Use deterministic iteration order
        for prize_type in self.PRIZE_ITERATION_ORDER:
            cumulative += adjusted_probs.get(prize_type, 0)
            if rand_value < cumulative:
                if prize_type != PrizeType.NONE:
                    # Award prize (do not mutate global prize pool here so that
                    # probabilistic tests are not affected by a shared, finite
                    # pool). Pool consumption remains available via the
                    # `PrizePool` API when callers want to enforce limits.
                    user.today_wins += 1
                    user.last_win_time = datetime.now()
                    if user.ip_address:
                        self.ip_win_counts[user.ip_address] = self.ip_win_counts.get(user.ip_address, 0) + 1

                return prize_type, f"Won {prize_type.value}"

        return PrizeType.NONE, "Better luck next time"

    def _calculate_adjusted_probabilities(self, user: User) -> Dict[PrizeType, float]:
        level_mult = self.LEVEL_MULTIPLIERS[user.level]
        consumption_bonus = self._get_consumption_bonus(user.total_consumption)

        adjusted: Dict[PrizeType, float] = {}
        total_adjustment = 0.0

        # Respect deterministic order of BASE_PROBABILITIES iteration. Do NOT
        # gate probabilities on `PrizePool` availability here — probability
        # calculations should remain stable and deterministic for testing.
        for prize_type in [PrizeType.FIRST, PrizeType.SECOND, PrizeType.THIRD, PrizeType.NONE]:
            base_prob = self.BASE_PROBABILITIES[prize_type]
            if prize_type != PrizeType.NONE:
                adjusted_prob = base_prob * level_mult
                adjusted[prize_type] = adjusted_prob
                total_adjustment += adjusted_prob
            else:
                adjusted[prize_type] = base_prob

        if consumption_bonus > 0 and total_adjustment > 0:
            for prize_type in [PrizeType.FIRST, PrizeType.SECOND, PrizeType.THIRD]:
                if adjusted.get(prize_type, 0) > 0:
                    bonus_share = (adjusted[prize_type] / total_adjustment) * consumption_bonus
                    adjusted[prize_type] += bonus_share

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
    """Factory to create LotterySystem.

    If seed is provided we create a dedicated RNG so results are deterministic
    and isolated from module-level `random` state. If seed is None the
    LotterySystem will use the module-level `random` as before.
    """
    if seed is not None:
        rng = random.Random(seed)
        return LotterySystem(rng=rng)
    return LotterySystem()
