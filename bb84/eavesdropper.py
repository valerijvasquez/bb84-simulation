import random
import numpy as np
from .globals import ket_0, ket_1, ket_plus, ket_minus, bases

class Eavesdropper:
    def __init__(self, intercept_fraction=1.0):
        self.intercept_fraction = intercept_fraction
        self.intercepted_positions = set()
        self.bases = {}
        self.intercepted_bits = {}

    def should_intercept(self, position):
        if random.random() < self.intercept_fraction:
            self.intercepted_positions.add(position)
            return True
        return False

    def intercept(self, state, position=None):
        basis = random.choice(bases)
        if position is not None:
            self.bases[position] = basis
        measured_bit = self.measure(state, basis)
        if position is not None:
            self.intercepted_bits[position] = measured_bit
        return self.encode(measured_bit, basis)

    def measure(self, state, basis):
        if basis == 'x':
            return 0 if np.allclose(state, ket_plus) else 1
        elif basis == '+':
            return 0 if np.allclose(state, ket_0) else 1


    def encode(self, bit, basis):
        if basis == 'x':
            return ket_plus if bit == 0 else ket_minus
        elif basis == '+':
            return ket_0 if bit == 0 else ket_1

