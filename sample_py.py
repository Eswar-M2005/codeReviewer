

# Unused imports
import math
import random
import sys

# Global variable that is never used
GLOBAL_LIMIT = 100

def calculate_something(numbers):
    # Unused local variables
    total = 0
    temp_list = []

    # Deeply nested loops (often a code smell when not needed)
    result = []
    for i in range(len(numbers)):
        for j in range(len(numbers)):
            for k in range(3):
                # Bad: recomputing and shadowing variables
                total = numbers[i] + numbers[j]
                x = 0  # unused
                if total % 2 == 0:
                    result.append(total)

    # Another unused variable
    debug_flag = True

    return result


def process_data(data):
    # Unused parameter example: 'data' might not be used properly
    filtered = []
    for item in data:
        # Unused variable inside loop
        temp = item * 2
        if item > 10:
            filtered.append(item)

    # Silly nested loop just to show structure
    count = 0
    for x in filtered:
        for y in filtered:
            if x == y:
                count += 1

    return count


def main():
    nums = [1, 5, 10, 15, 20]
    # Unused variable holding a function result
    some_values = calculate_something(nums)

    # Nested loop again
    for i in range(5):
        for j in range(5):
            print(f"Pair: {i}, {j}")

    # Unused import usage attempt (commented out)
    # print(sys.version)

    # Function call whose result is not used meaningfully
    process_data(nums)


if __name__ == "__main__":
    main()