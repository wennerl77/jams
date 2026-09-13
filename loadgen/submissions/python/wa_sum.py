import sys

def main():
    lines = sys.stdin.read().split()
    if len(lines) >= 2:
        a, b = int(lines[0]), int(lines[1])
        print(a + b + 42) # Wrong Answer

if __name__ == "__main__":
    main()
