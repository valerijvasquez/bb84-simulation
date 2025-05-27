import numpy as np
from .globals import ket_0, ket_1, ket_plus, ket_minus, bases

class QubitReceiver:

    def __init__(self):
        self.bases = []
        self.received_states = []
        self.measured_bits = []
        self.reconciled_key = None
        self.sample_indices = []


    def receive_single_qubit(self, state, index):
        basis = np.random.choice(bases)
        self.bases.append(basis)
        self.received_states.append(state)

        if state is None:
            self.measured_bits.append(None)
            return

        if basis == '+':
            bit = 0 if np.allclose(state, ket_0) else 1
        elif basis == 'x':
            bit = 0 if np.allclose(state, ket_plus) else 1


        self.measured_bits.append(bit)



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


    def receive_sample_indices(self, indices):
        self.sample_indices = indices

    def compare_sample(self, bob_key, alice_key):
        sample_a = [alice_key[i] for i in self.sample_indices]
        sample_b = [bob_key[i] for i in self.sample_indices]
        errors = sum(a != b for a, b in zip(sample_a, sample_b))
        return errors / len(self.sample_indices)

    def set_corrected_key(self, corrected_key):
        self.reconciled_key = corrected_key
