import numpy as np

from .globals import ket_0, ket_1, ket_plus, ket_minus, bits, bases

class QubitReceiver:
    def __init__(self, key_length):
        self.key_length = key_length
        self.bases = None
        self.measured_bits = None

    def choose_bases(self):
        self.bases = np.random.choice(bases, self.key_length)

    def measure_qubits(self, encoded_qubits):
        measured = []
        for i, (state, alice_basis) in enumerate(encoded_qubits):
            if state is None:
                measured.append(None)
                continue
            bob_basis = self.bases[i]
            if bob_basis == alice_basis:
                bit = 0 if np.allclose(state, ket_0) or np.allclose(state, ket_plus) else 1
            else:
                bit = np.random.choice(bits)
            measured.append(bit)
        self.measured_bits = measured

    def reconcile_with(self, alice_bases):
        matching_indices = (self.bases == alice_bases) & (np.array(self.measured_bits) != None)
        self.reconciled_key = np.array(self.measured_bits)[matching_indices]
        return self.reconciled_key

    def error_rate(self, alice_bits, alice_bases):
        matching_indices = (self.bases == alice_bases) & (np.array(self.measured_bits) != None)
        alice_reconciled = alice_bits[matching_indices]
        bob_reconciled = np.array(self.measured_bits)[matching_indices]

        if len(alice_reconciled) == 0:
            return None

        errors = alice_reconciled != bob_reconciled
        return np.mean(errors)
