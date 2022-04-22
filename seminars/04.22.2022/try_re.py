# Task 1. Extract host from the given log
# Task 2. Extract username from the given log
# Task 3. Extract request as string from the given log
# Task 4. Extract time as string from the given log
# Task 5. Extract time as datetime object from the given log
# Task 6. Wrap log analysis as a function and find out how many entrances (should be 979)
import re


def main():
    name = 'Tom Gayler, 19 y.o.'

    # 1. Create a pattern
    p = re.compile(r'\w+ \w+, \d{1,3} y\.o\.')

    # 2. Run match for a pattern
    res = p.match(name)

    # 3. Working with match object - first group returns the match
    print(res.group(0))
    print(f'Match is placed in following indexes: {res.span()}')

    # Information retrieval assumes tasks of getting data from text, not just
    # checking is string matches the template
    # for information retrieval we use groups
    p_groups = re.compile(r'(\w+) (\w+), (\d{1,3}) y\.o\.')

    # Going through all the matches - unstructured approach - returns list of tuples
    print(p_groups.findall(name))

    # Going through all the matches - structured approach - returns Iterator with Match instances
    for match in p_groups.finditer(name):
        print(match.group(0))
        print(f'Name: {match.group(1)}')
        print(f'Surname: {match.group(2)}')
        print(f'Age: {match.group(3)}')

    # Using named groups is a preferred option, but Python-specific
    p_groups = re.compile(r'(?P<name>\w+) (?P<surname>\w+), (?P<age>\d{1,3}) y\.o\.')
    for match in p_groups.finditer(name):
        print(f'Name: {match.group("name")}')
        print(f'Surname: {match.group("surname")}')
        print(f'Age: {match.group("age")}')


if __name__ == '__main__':
    main()
