import numpy as np

# Quantum states
ket_0 = np.array([1, 0])
ket_1 = np.array([0, 1])
ket_plus  = (1 / np.sqrt(2)) * (ket_0 + ket_1)
ket_minus = (1 / np.sqrt(2)) * (ket_0 - ket_1)

bits = [0, 1]
bases = ['+', 'x']

class QubitSender:
    def __init__(self, key_length):
        self.key_length = key_length
        self.bits = None
        self.bases = None

    def prepare_qubits(self):
        self.bits = np.random.choice(bits, self.key_length)
        self.bases = np.random.choice(bases, self.key_length)

    def encode_qubits(self):
        states = []
        for bit, basis in zip(self.bits, self.bases):
            if basis == '+':
                state = ket_0 if bit == 0 else ket_1
            else:
                state = ket_plus if bit == 0 else ket_minus
            states.append((state, basis))
        self.encoded_qubits = states

