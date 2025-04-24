import numpy as np

ket_0 = np.array([1, 0])
ket_1 = np.array([0, 1])
ket_plus  = (1 / np.sqrt(2)) * (ket_0 + ket_1)
ket_minus = (1 / np.sqrt(2)) * (ket_0 - ket_1)

class Channel:
    def __init__(self, sender, receiver, eavesdropper=None, flip_probability=0.0, loss_probability=0.0):
        self.sender = sender
        self.receiver = receiver
        self.eavesdropper = eavesdropper
        self.flip_probability = flip_probability
        self.loss_probability = loss_probability
        self.loss_count = 0
        self.flip_count = 0

    def transmit(self):
        if self.eavesdropper:
            qubits = self.eavesdropper.intercept(self.sender.encoded_qubits)
        else:
            qubits = self.sender.encoded_qubits

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

        self.receiver.measure_qubits(noisy_qubits)
