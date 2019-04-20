from .constants import CARDS


def sort(array):
    less = []
    equal = []
    greater = []

    if len(array) > 1:
        pivot = CARDS[array[0]] if isinstance(array[0], str) else array[0]
        for x in array:
            y = CARDS[x] if isinstance(x, str) else x
            if y < pivot:
                less.append(x)
            elif y == pivot:
                equal.append(x)
            else:
                greater.append(x)

        return sort(less) + equal + sort(greater)

    else:
        return array
