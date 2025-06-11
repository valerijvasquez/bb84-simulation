import numpy as np
import hashlib

from .sender import QubitSender
from .receiver import QubitReceiver
from .quantum_channel import QuantumChannel
from .classical_channel import ClassicalChannel
from .eavesdropper import Eavesdropper
from .ecc16 import ECC16
from .privacy_amplification import PrivacyAmplifier

class BB84Simulation:
    """
    Orchestrates the entire BB84 quantum key distribution protocol,
    including transmission, reconciliation, error estimation, ECC,
    and privacy amplification.
    """

    def __init__(self, key_length=20, use_eve=False, eve_fraction=1.0,
                 flip_probability=0.0, loss_probability=0.0):
        """
        Initialize simulation parameters.

        Args:
            key_length (int): Number of qubits to send.
            use_eve (bool): Whether Eve should intercept.
            eve_fraction (float): Fraction of qubits Eve intercepts.
            flip_probability (float): Channel bit flip probability.
            loss_probability (float): Channel loss probability.
        """
        self.key_length = key_length
        self.use_eve = use_eve
        self.eve_fraction = eve_fraction
        self.flip_probability = flip_probability
        self.loss_probability = loss_probability
        self.alice = None
        self.bob = None
        self.eve = None
        self.quantum_channel = None
        self.classical_channel = None
        self.shared_key = None
        self.error_rate = None
        self.sample_indices = None

    def run(self):
        """
        Run the full BB84 protocol up to key reconciliation.
        """
        self.alice = QubitSender(self.key_length)
        self.bob = QubitReceiver()
        self.eve = Eavesdropper(self.eve_fraction) if self.use_eve else None

        self.alice.prepare_qubits()

        self.quantum_channel = QuantumChannel(
            flip_probability=self.flip_probability,
            loss_probability=self.loss_probability,
            eavesdropper=self.eve
        )

        transmitted_states = [
            self.quantum_channel.transmit(self.alice.encode_single_qubit(i), i)
            for i in range(self.key_length)
        ]

        for i, state in enumerate(transmitted_states):
            self.bob.receive_single_qubit(state, i)

        self.classical_channel = ClassicalChannel(self.alice, self.bob)
        self.shared_key = self.classical_channel.reconcile_key()

    def estimate_error_from_sample(self, sample_fraction=0.2):
        """
        Perform error estimation using a random sample of the reconciled key.

        Args:
            fraction (float): Fraction of the key to sample.
        """
        key_length = len(self.classical_channel.bob_key)
        indices = self.alice.choose_sample_indices(key_length, sample_fraction)
        self.classical_channel.send_sample_indices_to_bob(indices)
        self.sample_indices = indices

        self.error_rate = self.bob.compare_sample(
            bob_key=self.classical_channel.bob_key,
            alice_key=self.shared_key
        )

        self.shared_key = [int(bit) for i, bit in enumerate(self.shared_key) if i not in indices]
        self.classical_channel.bob_key = [int(bit) for i, bit in enumerate(self.classical_channel.bob_key) if i not in indices]

    def run_ecc16(self):
        status, corrected_key = ECC16(
            alice_key=self.shared_key,
            bob_key=self.classical_channel.bob_key
        ).run()

        if status == "SUCCESS":
            print("ECC16 succeeded.")
            self.shared_key = corrected_key
            self.final_key = corrected_key 
            return True
        else:
            print("ECC16 failed: aborting protocol.")
            self.final_key = None         
            return False





    def show_results(self):
        """
        Print out all results: measurement outcomes, ECC status,
        final key hash, and privacy amplification results.
        """
        print("\n=== Results ===")
        print("Alice bits:", self.alice.bits[:10], "...")
        print("Alice bases:", self.alice.bases[:10], "...")
        if self.eve:
            print("Eve bases:", list(self.eve.bases.items())[:10], "...")
            print("Eve bits:", list(self.eve.intercepted_bits.items())[:10], "...")
        print("Bob bases:", self.bob.bases[:10], "...")
        print("Bob measurements:", self.bob.measured_bits[:10], "...")
        print("Reconciled key:", self.shared_key[:10], "...")
        print(f"Reconciled key length: {len(self.shared_key)} bits")
        print(f"Channel lost qubits: {self.quantum_channel.loss_count}")
        print(f"Channel flipped qubits: {self.quantum_channel.flip_count}")

        if self.sample_indices is not None:
            print("\n=== Error estimation ===")
            used = len(self.sample_indices)
            total = used + len(self.shared_key)
            print(f"Used {used} bits ({round(100 * used / total, 1)}%) of key for error estimation.")
            print(f"Remaining key length after discarding sample: {len(self.shared_key)} bits")
            print(f"Sampled error rate: {round(self.error_rate * 100, 2)}%")

        success = self.run_ecc16()
        if not success:
            self.final_key = None
            return

        print("\n=== Privacy amplification ===")

        if hasattr(self, 'message') and self.message:
            required_bits = len(self.message.encode()) * 8
            print(f"Truncating reconciled key to {required_bits} bits for OTP encryption.")

        else:
            required_bits = 40
            print("No message found. Defaulting to 40-bit final key.")

        amplifier = PrivacyAmplifier(output_bits=required_bits)
        self.final_key = amplifier.apply(self.shared_key)

        shake = hashlib.shake_256()
        padded_len = ((len(self.shared_key) + 7) // 8) * 8
        padded_bits = self.shared_key + [0] * (padded_len - len(self.shared_key))
        bitstring = ''.join(str(b) for b in padded_bits)
        key_bytes = int(bitstring, 2).to_bytes(padded_len // 8, byteorder='big')
        shake.update(amplifier.seed + key_bytes)
        digest = shake.digest(amplifier.output_bytes)
        digest_bits = ''.join(f"{byte:08b}" for byte in digest)

        print(f"Hash function used: SHAKE-256")
        print(f"Seed used (hex): {amplifier.seed.hex()}")
        print("Hashed key (hex):", digest.hex())
        print(f"Hashed key (binary, {required_bits} bits):", self.final_key)