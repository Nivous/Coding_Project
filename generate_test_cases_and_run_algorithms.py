
from enum import Enum
import math
from timeit import default_timer as timer
import os
import random
import matplotlib.pyplot as plt

VECTOR_LENGTH = 10000
TEST_CASES = 15000
RANDOM_SEED = 42


class Operations(Enum):
    FLIPPING_AVERAGE_CRITICAL, FLIPPING_WORSE_CRITICAL = range(1, 3)

    def to_print(self):
        return self.name.lower()


def calculate_redundancy(op):
    dir_path = os.path.join(os.getcwd(), op.to_print() + "_algo_results")
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    results_file = dir_path + "/" + op.to_print() + "_vector_length_" + \
        str(VECTOR_LENGTH) + "_results" + ".txt"
    if os.path.exists(results_file):
        os.remove(results_file)
    g = open(results_file, "w")
    g.write("---Starting---\n")
    g.close()
    g = open(results_file, "a")
    windows = [math.floor(math.log(VECTOR_LENGTH, 2)), math.floor(
        math.sqrt(VECTOR_LENGTH)), math.floor(math.pow(VECTOR_LENGTH, 1 / 3))]
    for window_len in windows:
        if window_len <= 1:
            continue
        print_str = "Vector Length - " + \
            str(VECTOR_LENGTH) + ", Window Length - " + str(window_len) + ", Test Cases - " + \
            str(TEST_CASES) + "\n"
        g.write(print_str)
        redundancy_sum, total_encode_time, total_decode_time, max_redundency, min_redundency, hist = calculate_red_per_vector(
            window_len, op)
        redundancy_avg = redundancy_sum / TEST_CASES
        time_encode_avg = total_encode_time / TEST_CASES
        time_decode_avg = total_decode_time / TEST_CASES
        redundancy_avg_to_window_len = redundancy_avg / window_len
        print_str = "Average time to encode is - " + \
            str(time_encode_avg) + "\n"
        print_str += "Average time to decode is - " + \
            str(time_decode_avg) + "\n"
        print_str += "Minimum redundancy bits needed is - " + \
            str(min_redundency) + "\n"
        print_str += "Maximal redundancy bits needed is - " + \
            str(max_redundency) + "\n"
        print_str += "Average redundancy bits needed is - " + \
            str(redundancy_avg) + "\n"
        print_str += "Average redundancy bits to window length is - " + \
            str(redundancy_avg_to_window_len) + "\n"
        g.write(print_str)

        plt.xlabel("Redundancy bits")
        plt.ylabel("Number of test cases")
        if op == Operations.FLIPPING_AVERAGE_CRITICAL:
            title = "First coding scheme\n"
        else:
            title = "Second coding scheme\n"
        title += "Vector length: " + \
            str(VECTOR_LENGTH) + ", Window length: " + str(window_len)
        filename = dir_path + "/vector_length_" + \
            str(VECTOR_LENGTH) + "_window_length_" + \
            str(window_len) + "_hist.png"
        plt.hist(hist)
        plt.title(title)
        plt.savefig(filename)
        # plt.show()
        plt.clf()
        plt.cla()
        plt.close()

        print("Done with vecotr length: " + str(VECTOR_LENGTH) +
              ", window length: " + str(window_len))


def calculate_red_per_vector(window_len, op):
    redundancy_bits_total = 0
    min_redundancy = 0
    max_redundancy = 0
    total_encode_time = 0
    total_decode_time = 0
    counter = 0
    random.seed(RANDOM_SEED)
    hist = []
    while counter < TEST_CASES:
        if counter % 1000 == 0:
            print("passed " + str(counter) + " vectors!")
        vector = get_next_num()
        time_start = timer()
        enc_vector = execute_encoding_algo_on_vector(vector, window_len, op)
        time_took = timer() - time_start
        redundancy_bits_total += len(enc_vector) - len(vector)
        hist.append(len(enc_vector) - len(vector))
        total_encode_time += time_took
        if not is_locally_bounded(enc_vector, window_len):
            print("Encoding Failure!\n")
            print("Window length: " + str(window_len))
            print("Vector encoded:        " + vector)
            print("Vector after encoding: " + enc_vector)
        time_start = timer()
        dec_vector = execute_decoding_algo_on_vector(
            enc_vector, window_len, op)
        time_took = timer() - time_start
        if dec_vector != vector:
            print("Decoding failure!\n")
            print("Window length: " + str(window_len))
            print("Vector encoded:        " + vector)
            print("Vector after encoding: " + enc_vector)
            print("Vector after decoding: " + dec_vector)
        total_decode_time += time_took
        counter += 1
    return redundancy_bits_total, total_encode_time, total_decode_time, max_redundancy, min_redundancy, hist


def get_next_num():
    vector = ""
    for _ in range(0, VECTOR_LENGTH):
        vector += str(math.floor(random.random() + 0.5))

    return vector


def execute_decoding_algo_on_vector(enc_vector, window_len, op):
    if op == Operations.FLIPPING_AVERAGE_CRITICAL:
        return execute_decode_flipping_critical_average_algo_on_vector(enc_vector, window_len)
    if op == Operations.FLIPPING_WORSE_CRITICAL:
        return execute_decode_flipping_critical_worse_algo_on_vector(enc_vector, window_len)


def execute_encoding_algo_on_vector(vector, window_len, op):
    if op == Operations.FLIPPING_AVERAGE_CRITICAL:
        return execute_encode_flipping_critical_average_algo_on_vector(vector, window_len)
    if op == Operations.FLIPPING_WORSE_CRITICAL:
        return execute_encode_flipping_critical_worse_algo_on_vector(vector, window_len)


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


def execute_decode_flipping_critical_average_algo_on_vector(vector, window_len):
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


def execute_encode_flipping_critical_average_algo_on_vector(vector, window_len):
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


def is_locally_bounded(vector, window_len):
    max_weight = math.floor(window_len)
    weight = find_window_weight(vector, 0, window_len)
    if weight > max_weight:
        return False
    i = 1

    while i + window_len - 1 < len(vector):
        weight -= int(vector[i - 1])
        weight += int(vector[i + window_len - 1])
        if weight > max_weight:
            return False
        i += 1

    return True


if __name__ == "__main__":
    calculate_redundancy(Operations.FLIPPING_AVERAGE_CRITICAL)
    calculate_redundancy(Operations.FLIPPING_WORSE_CRITICAL)
