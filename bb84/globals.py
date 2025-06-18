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



