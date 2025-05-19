import numpy as np
from .globals import ket_0, ket_1, ket_plus, ket_minus, bases
class QubitReceiver:
    def __init__(self, key_length):
        self.key_length = key_length
        self.bases = None
        self.received_states = None
        self.measured_bits = None
        self.reconciled_key = None
        self.sample_indices = []
    def choose_bases(self):
        self.bases = np.random.choice(bases, size=self.key_length)
    def receive_qubits(self, states):
        self.received_states = states
        self.measure_qubits(states)
    def measure_qubits(self, encoded_qubits):
        self.measured_bits = []
        for i, received_state in enumerate(encoded_qubits):
            if received_state is None:
                self.measured_bits.append(None)
                continue
            basis = self.bases[i]
            if basis == '+':
                bit = 0 if np.allclose(received_state, ket_0) else 1
            else:
                bit = 0 if np.allclose(received_state, ket_plus) else 1
            self.measured_bits.append(bit)
    def reconcile_with(self, alice_bases):
        matching_indices = np.where(self.bases == alice_bases)[0]
        self.reconciled_key = np.array(self.measured_bits)[matching_indices]
        return self.reconciled_key
    def error_rate(self, alice_bits, alice_bases):
        matching_indices = np.where(self.bases == alice_bases)[0]
        alice_key = np.array(alice_bits)[matching_indices]
        bob_key = np.array(self.measured_bits)[matching_indices]
        valid = [i for i in range(len(bob_key)) if bob_key[i] is not None]
        if not valid:
            return 1.0
        alice_key = alice_key[valid]
        bob_key = bob_key[valid]
        errors = np.sum(alice_key != bob_key)
        return errors / len(valid)
    def receive_sample_indices(self, indices):
        self.sample_indices = indices
    def compare_sample(self, bob_key, alice_key):
        sample_a = [alice_key[i] for i in self.sample_indices]
        sample_b = [bob_key[i] for i in self.sample_indices]
        errors = sum(a != b for a, b in zip(sample_a, sample_b))
        return errors / len(self.sample_indices)

    def set_corrected_key(self, corrected_key):
        self.reconciled_key = corrected_key
