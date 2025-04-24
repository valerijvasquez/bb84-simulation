import numpy as np

ket_0 = np.array([1, 0])
ket_1 = np.array([0, 1])
ket_plus  = (1 / np.sqrt(2)) * (ket_0 + ket_1)
ket_minus = (1 / np.sqrt(2)) * (ket_0 - ket_1)

bits = [0, 1]
bases = ['+', 'x']

class Eavesdropper:
    def __init__(self, interception_fraction=1.0):
        self.interception_fraction = interception_fraction
        self.bases = None
        self.intercepted_bits = None

    def intercept(self, encoded_qubits):
        total = len(encoded_qubits)
        num_to_intercept = int(total * self.interception_fraction)
        indices_to_intercept = np.random.choice(total, num_to_intercept, replace=False)

        measured_bits = []
        measured_bases = []

        for i, (state, alice_basis) in enumerate(encoded_qubits):
            if i in indices_to_intercept:
                eve_basis = np.random.choice(bases)
                if eve_basis == alice_basis:
                    bit = 0 if np.allclose(state, ket_0) or np.allclose(state, ket_plus) else 1
                else:
                    bit = np.random.choice(bits)
            else:
                eve_basis = alice_basis
                bit = 0 if np.allclose(state, ket_0) or np.allclose(state, ket_plus) else 1

            measured_bases.append(eve_basis)
            measured_bits.append(bit)

        self.bases = np.array(measured_bases)
        self.intercepted_bits = np.array(measured_bits)

        return list(zip([ket_0 if b == 0 else ket_1 for b in measured_bits], measured_bases))
