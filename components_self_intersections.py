from thompson import words_to_gauss

def numbers_of_self_intersections(gauss_code):
    components, signs = gauss_code
    result = []
    for component in components:
        distinct = set(map(abs, component))
        self_intersections = len(component) - len(distinct)
        result.append(self_intersections)
    return tuple(result)


if __name__ == "__main__":

    from link_classification import pairs_of_binary_words

    for pair in pairs_of_binary_words(7):
        gauss = words_to_gauss(*pair)
        numbers = numbers_of_self_intersections(gauss)
        if any(x % 2 for x in numbers):
            print(pair)
            print(*numbers)
