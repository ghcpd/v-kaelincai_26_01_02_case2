from random import Random

rng = Random(77)
print("Index, Value, Threshold, Hit?")
for i in range(30):
    val = rng.random()
    threshold = 0.2306
    hit = "YES" if val < threshold else "NO"
    print(f"{i:2d}, {val:.6f}, {threshold:.4f}, {hit}")
