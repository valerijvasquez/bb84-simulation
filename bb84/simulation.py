import numpy as np
import hashlib

from .sender import QubitSender
from .receiver import QubitReceiver
from .quantum_channel import QuantumChannel
from .classical_channel import ClassicalChannel
from .eavesdropper import Eavesdropper

class BB84Simulation:
    def __init__(self, key_length=20, use_eve=False, eve_fraction=1.0,
                 use_hashing=False, flip_probability=0.0, loss_probability=0.0):
        self.key_length = key_length
        self.use_eve = use_eve
        self.eve_fraction = eve_fraction
        self.use_hashing = use_hashing
        self.flip_probability = flip_probability
        self.loss_probability = loss_probability
        self.alice = None
        self.bob = None
        self.eve = None
        self.quantum_channel = None
        self.classical_channel = None
        self.shared_key = None
        self.error_rate = None
        self.hashed_key = None

    def run(self):
        self.alice = QubitSender(self.key_length)
        self.bob = QubitReceiver(self.key_length)
        self.eve = Eavesdropper(self.eve_fraction) if self.use_eve else None

        self.alice.prepare_qubits()
        self.alice.encode_qubits()
        self.bob.choose_bases()

        self.quantum_channel = QuantumChannel(
            flip_probability=self.flip_probability,
            loss_probability=self.loss_probability,
            eavesdropper=self.eve
        )
        self.quantum_channel.transmit(self.alice.encoded_qubits, self.bob)

        self.classical_channel = ClassicalChannel(self.alice, self.bob)
        self.shared_key = self.classical_channel.reconcile()
        self.error_rate = self.classical_channel.calculate_error_rate()

        if self.use_hashing:
            bitstring = ''.join(map(str, self.shared_key))
            self.hashed_key = hashlib.sha256(bitstring.encode()).hexdigest()

    def show_results(self):
        print("Alice bits:       ", self.alice.bits)
        print("Alice bases:      ", self.alice.bases)
        if self.eve:
            print("Eve bases:        ", self.eve.bases)
            print("Eve bits:         ", self.eve.intercepted_bits)
        print("Bob bases:        ", self.bob.bases)
        print("Bob measurements: ", self.bob.measured_bits)
        print("Matching bases:   ", self.alice.bases == self.bob.bases)
        print("Reconciled key:   ", self.shared_key)
        print("Error rate:       ", "N/A" if self.error_rate is None else f"{round(self.error_rate * 100, 2)}%")
        print(f"Channel lost qubits: {self.quantum_channel.loss_count}")
        print(f"Channel flipped qubits: {self.quantum_channel.flip_count}")
        if self.hashed_key:
            print("Final hashed key (SHA-256):", self.hashed_key)


