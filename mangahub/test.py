from timeit import timeit


def main() -> int:
    num = 0
    for i in range(100_000_000):
        num += i
    return num

if __name__ == "__main__":
    times = []
    for i in range(5):
        t = timeit(main, number=1)
        times.append(t)
        print(t)
    print(f"Avg: {sum(times) / len(times)}")
    print()
    
    times = []
    for i in range(5):
        t = timeit(main, number=10)
        times.append(t)
        print(t)
    print(f"Avg: {sum(times) / len(times)}")