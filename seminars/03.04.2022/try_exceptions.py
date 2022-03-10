# TASK 1
# Make the code pass even if fails
try:
    a = None

    #print(a.split())

    #print(a / 0)

    #print(int('abc'))

    d = {}

    #print(d['name'])

    l = []

    #print(l[100])

    print(l[None])
except AttributeError:
    print('This is not a text')
except TypeError as e:
    print('Impossible action for the variable\'s type')
    print(e)
except ValueError:
    print('Impossible action for this value')
except (KeyError, IndexError):
    print('The dict or list does not have such item')




# TASK 2
def count_evens(numbers: list) -> int:
    """
    Return the number of even (четный) numbers in the given list.
    If the argument is not a list, throw ValueError
    """
    if not isinstance(numbers, list):
        raise ValueError('List type variable is required')
    evens = 0
    for number in numbers:
        if number % 2 == 0:
            evens += 1
    print(evens)
    return evens


assert count_evens([2, 1, 2, 3, 4]), 3
assert count_evens([2, 2, 0]), 3
try:
    count_evens(3)
except ValueError:
    print('We cannot detect a list')

# TASK 1
'''
Write a function `find_sum` that returns the sum of three numbers.
However, 13 is unlucky, so if one of the values is
13, then the function throws `ThirteenError`.
'''
class ThirteenError(Exception):
    ''''Unlucky number'''
    pass

def find_sum(n1, n2, n3):
    summa = 0
    numbers = [n1, n2, n3]
    try:
        for i in range(3):
            if numbers[i] == 13:
                raise ThirteenError
            summa += numbers[i]
    except:
        print('Error')
        return None

    return summa

# Uncomment these lines when function is ready to check
print(find_sum(1, 2, 3))  # 6
print(find_sum(1, 2, 13))  # raises ThirteenError exception
