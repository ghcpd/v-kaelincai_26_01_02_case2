from src.lottery import create_lottery, User, UserLevel

l1 = create_lottery(seed=42)
l2 = create_lottery(seed=42)
u = User("U001", UserLevel.GOLD, 5000)
p1, _ = l1.draw(u)
p2, _ = l2.draw(u)
print("seed_test: p1=", p1, "p2=", p2, "equal=", p1 == p2)

# Also check different seeds produce different results (likely)
l3 = create_lottery(seed=123)
p3, _ = l3.draw(u)
print("seed_test_different: p3=", p3)