# TASK 1
# Make the code pass even if fails

a = None

print(a.split())

print(a / 0)

print(int('abc'))

d = {}

print(d['name'])

l = []

print(l[100])

print(l[None])


# TASK 2
def count_evens(numbers: list) -> int:
    """
    Return the number of even (четный) numbers in the given list.
    If the argument is not a list, throw ValueError
    """
    pass


assert count_evens([2, 1, 2, 3, 4]), 3
assert count_evens([2, 2, 0]), 3
assert count_evens([1, 3, 5]), 0


# TASK 1
'''
Write a function `find_sum` that returns the sum of three numbers.
However, 13 is unlucky, so if one of the values is
13, then the function throws `ThirteenError`.
'''

# Uncomment these lines when function is ready to check
# print(find_sum(1, 2, 3))  # 6
# print(find_sum(1, 2, 13))  # raises ThirteenError exception