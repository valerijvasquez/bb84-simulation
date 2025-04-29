import numpy as np
from .globals import ket_0, ket_1, ket_plus, ket_minus

class QuantumChannel:
    def __init__(self, flip_probability=0.0, loss_probability=0.0, eavesdropper=None):
        self.flip_probability = flip_probability
        self.loss_probability = loss_probability
        self.eavesdropper = eavesdropper
        self.loss_count = 0
        self.flip_count = 0

    def transmit(self, encoded_qubits, receiver):
        if self.eavesdropper:
            qubits = self.eavesdropper.intercept(encoded_qubits)
        else:
            qubits = encoded_qubits

        noisy_qubits = []
        for state, basis in qubits:
            if np.random.rand() < self.loss_probability:
                self.loss_count += 1
                noisy_qubits.append((None, basis))
            else:
                if np.random.rand() < self.flip_probability:
                    self.flip_count += 1
                    flipped_bit = 1 if np.allclose(state, ket_0) or np.allclose(state, ket_plus) else 0
                    flipped_state = ket_1 if flipped_bit == 1 else ket_0
                    noisy_qubits.append((flipped_state, basis))
                else:
                    noisy_qubits.append((state, basis))

        receiver.measure_qubits(noisy_qubits)
