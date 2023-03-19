import math

VECTOR_LENGTH = 10000


def encode(vector, window_len):
    endPointer = len(vector) - 1
    i = endPointer - window_len
    weight = find_window_weight(vector, i, i + window_len)
    max_weight = math.floor(window_len / 2)

    while i >= 0:
        if weight == max_weight and vector[i] == '0':
            vector = set_bit(vector, i + window_len, int(vector[endPointer]))
            endPointer -= 1
        i -= 1
        weight -= int(vector[i + window_len])
        weight += int(vector[i])

    if vector[VECTOR_LENGTH + 1] == '1':
        vector = flip_vector(vector, 0, window_len)
    if vector[VECTOR_LENGTH] == '1':
        vector = flip_vector(vector, 0, VECTOR_LENGTH)

    return vector[0: VECTOR_LENGTH]


def decode(vector, window_len):
    vector = flip_if_heavy(vector)
    vector = flip_first_window_if_heavy(vector, window_len)
    n = len(vector)
    max_weight = math.floor(window_len / 2)
    weight = find_window_weight(vector, 0, window_len)
    i = 0

    while i + window_len - 1 < n - 1:
        if weight == max_weight and vector[i] == '0':
            vector += vector[i + window_len]
            vector = set_bit(vector, i + window_len, 0)
            n += 1

        weight -= int(vector[i])
        weight += int(vector[i + window_len])
        i += 1

    return vector


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
