import math

VECTOR_LENGTH = 10000


def execute_decode_flipping_critical_worse_algo_on_vector(vector, window_len):
    left = 0
    right = VECTOR_LENGTH - 2
    leftStack = []
    rightStack = []
    counter_start = 2
    weight = find_window_weight(vector, 0, window_len)
    max_weight = math.floor(window_len / 2)
    while right - left >= 3 * window_len or counter_start == 2:
        counter = counter_start
        counter_start = 1
        i = left
        while i + window_len - 1 <= right:
            if weight == max_weight and vector[i] == '0':
                counter += 1
            weight += int(vector[i + window_len])
            weight -= int(vector[i])
            i += 1

        leftStack.append(left)
        rightStack.append(right)
        left = i
        right = right + counter

    vector = remove_zero_before_ones(vector, left, window_len)
    vector = remove_zero_bits(vector, left, window_len)

    endPointer = len(vector) - 1
    while len(leftStack) != 0:
        left = leftStack.pop()
        right = rightStack.pop()
        i = right - window_len + 1
        weight = find_window_weight(vector, i, i + window_len)
        while i >= left:
            if weight == max_weight and vector[i] == '0':
                vector = set_bit(vector, i + window_len,
                                 int(vector[endPointer]))
                endPointer -= 1
            i -= 1
            weight -= int(vector[i + window_len])
            weight += int(vector[i])

        if len(leftStack) != 0:
            if vector[endPointer] == '1':
                vector = flip_vector(vector, left + window_len, right + 2)
            endPointer -= 1

    if vector[VECTOR_LENGTH + 1] == '1':
        vector = flip_vector(vector, 0, window_len)
    if vector[VECTOR_LENGTH] == '1':
        vector = flip_vector(vector, 0, VECTOR_LENGTH)

    return vector[0:VECTOR_LENGTH]


def execute_encode_flipping_critical_worse_algo_on_vector(vector, window_len):
    n = len(vector)
    vector = flip_if_heavy(vector)
    vector = flip_first_window_if_heavy(vector, window_len)
    max_weight = math.floor(window_len / 2)
    weight = find_window_weight(vector, 0, window_len)
    i = 0

    while i + window_len - 1 < n - 1:
        if weight == max_weight and vector[i] == '0':
            vector += vector[i + window_len]
            vector = set_bit(vector, i + window_len, 0)

        weight -= int(vector[i])
        weight += int(vector[i + window_len])
        i += 1

    startIndex = i
    endIndex = len(vector) - 2

    while endIndex - startIndex >= 3 * window_len:
        vector = flip_if_heavy_then_w(
            vector, startIndex + window_len, endIndex + 2, (endIndex - startIndex - window_len + 2) / 2)
        i = startIndex

        while i + window_len - 1 <= endIndex:
            if weight == max_weight and vector[i] == '0':
                vector += vector[i + window_len]
                vector = set_bit(vector, i + window_len, 0)

            weight -= int(vector[i])
            weight += int(vector[i + window_len])
            i += 1

        startIndex = i
        endIndex = len(vector) - 2

    vector = add_zero_bits(vector, startIndex, window_len)
    vector = insert_zero_before_ones(vector, startIndex, window_len)

    return vector


def remove_zero_before_ones(vector, startIndex, window_len):
    vector = list(vector)
    index = startIndex + window_len + math.ceil(window_len / 2)
    while index < len(vector):
        if vector[index] == '1':
            vector.pop(index - 1)
        index += 1

    return ''.join(vector)


def insert_zero_before_ones(vector, startIndex, window_len):
    vector = list(vector)
    index = startIndex + window_len + math.ceil(window_len / 2)
    while index < len(vector):
        if vector[index] == '1':
            vector.insert(index, '0')
            index += 1
        index += 1

    return ''.join(vector)


def remove_zero_bits(vector, startIndex, window_len):
    vector = list(vector)
    for _ in range(0, math.ceil(window_len / 2)):
        vector.pop(startIndex + window_len)

    return ''.join(vector)


def add_zero_bits(vector, startIndex, window_len):
    vector = list(vector)
    for _ in range(0, math.ceil(window_len / 2)):
        vector.insert(startIndex + window_len, '0')

    return ''.join(vector)


def flip_if_heavy_then_w(vector, startIndex, endIndex, maxWeight):
    weight = find_window_weight(vector, startIndex, endIndex)
    if weight <= maxWeight:
        vector += '0'
    else:
        vector = flip_vector(vector, startIndex, endIndex)
        vector += '1'

    return vector


def flip_if_heavy(vector):
    return flip_if_heavy_then_w(vector, 0, VECTOR_LENGTH, VECTOR_LENGTH / 2)


def flip_first_window_if_heavy(vector, window_len):
    return flip_if_heavy_then_w(vector, 0, window_len, window_len / 2)


def set_bit(vector, index, value):
    vector = list(vector)
    vector[index] = str(value)
    return ''.join(vector)


def flip_vector(vector, start_index, end_index):
    vector = list(vector)
    for i in range(start_index, end_index):
        vector[i] = str(1 - int(vector[i]))
    return ''.join(vector)


def find_window_weight(vector, start_index, end_index):
    weight = 0
    for i in range(start_index, end_index):
        weight += int(vector[i])

    return weight
