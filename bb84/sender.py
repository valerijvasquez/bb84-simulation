import numpy as np
from .globals import ket_0, ket_1, ket_plus, ket_minus, bits, bases


class QubitSender:
    def __init__(self, key_length):
        self.key_length = key_length
        self.bits = None
        self.bases = None
        self.sample_indices = []
        self.reconciled_key = None

    def prepare_qubits(self):
        self.bits = np.random.choice(bits, self.key_length)
        self.bases = np.random.choice(bases, self.key_length)

    def encode_single_qubit(self, index):
        bit = self.bits[index]
        basis = self.bases[index]
        if basis == '+':
            return ket_0 if bit == 0 else ket_1
        elif basis == 'x':
            return ket_plus if bit == 0 else ket_minus

    def choose_sample_indices(self, key_length, fraction=0.2):
        indices = sorted(np.random.choice(key_length, int(fraction * key_length), replace=False))
        self.sample_indices = indices
        return indices
