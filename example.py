from flashcache import flashcache
import time

@flashcache(ttl=5)
def slow_add(a, b):
    print("Calculating...")
    return a + b

print(slow_add(2, 3))
print(slow_add(2, 3))
