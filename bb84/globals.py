import numpy as np


ket_0 = np.array([1, 0])
ket_1 = np.array([0, 1])

ket_plus  = (1 / np.sqrt(2)) * (ket_0 + ket_1)
ket_minus = (1 / np.sqrt(2)) * (ket_0 - ket_1)

bits = [0, 1]
bases = ['+', 'x']

identity = np.eye(2)
hadamard = (1 / np.sqrt(2)) * np.array([[1, 1],
                                        [1, -1]])



