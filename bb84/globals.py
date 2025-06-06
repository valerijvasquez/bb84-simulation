"""
Global constants and quantum basis states used in the BB84 protocol.
"""

import numpy as np
import math
import random
import hashlib

# Computational basis states
ket_0 = np.array([1, 0])
ket_1 = np.array([0, 1])

# Diagonal basis states
ket_plus  = (1 / np.sqrt(2)) * (ket_0 + ket_1)
ket_minus = (1 / np.sqrt(2)) * (ket_0 - ket_1)

# Allowed bit values and basis labels used in BB84
bits = [0, 1]
bases = ['+', 'x']

# Basis rotation matrices for measurment simulation, identity for "+" basis, hadamard for "x basis".
identity = np.eye(2)
hadamard = (1 / np.sqrt(2)) * np.array([[1, 1],
                                        [1, -1]])

# --------------------------------------------------
# Utility functions
# --------------------------------------------------



def next_power_of_two(n):
    power = 1
    while power < n:
        power *= 2
    return power

def binary_entropy(e):
    if e == 0 or e == 1:
        return 0.0
    return -e * math.log2(e) - (1 - e) * math.log2(1 - e)

def shuffle_indices(n):
    indices = list(range(n))
    random.shuffle(indices)
    return indices

def truncate_to_power_of_two(n):
    power = 1
    while power * 2 <= n:
        power *= 2
    return power

def parity(bits):
    return sum(bits) % 2

def hash_bits(bits):
    return hashlib.sha256(''.join(map(str, bits)).encode()).hexdigest()
