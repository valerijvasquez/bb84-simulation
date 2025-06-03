import numpy as np
import hashlib

from bb84.sender import QubitSender
from bb84.receiver import QubitReceiver
from bb84.quantum_channel import QuantumChannel
from bb84.classical_channel import ClassicalChannel
from bb84.eavesdropper import Eavesdropper
from bb84.hamming74 import Hamming74Corrector
from bb84.privacy_amplification import PrivacyAmplifier


class BB84SimulationHamming74:
    def __init__(self, key_length=20, use_eve=False, eve_fraction=1.0,
                 flip_probability=0.0, loss_probability=0.0):
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
        self.final_key = None
        self.message = None  # Optional: to enable OTP estimation

    def run(self):
        self.alice = QubitSender(self.key_length)
        self.bob = QubitReceiver()
        self.eve = Eavesdropper(self.eve_fraction) if self.use_eve else None
        self.alice.prepare_qubits()

        self.quantum_channel = QuantumChannel(
            flip_probability=self.flip_probability,
            loss_probability=self.loss_probability,
            eavesdropper=self.eve
        )

        for i in range(self.key_length):
            qubit = self.alice.encode_single_qubit(i)
            received = self.quantum_channel.transmit(qubit, i)
            self.bob.receive_single_qubit(received, i)

        self.classical_channel = ClassicalChannel(self.alice, self.bob)
        self.shared_key = self.classical_channel.reconcile_key()

    def estimate_error_from_sample(self, fraction=0.2):
        key_length = len(self.classical_channel.bob_key)
        indices = self.alice.choose_sample_indices(key_length, fraction)
        self.classical_channel.send_sample_indices_to_bob(indices)
        self.sample_indices = indices

        self.error_rate = self.bob.compare_sample(
            bob_key=self.classical_channel.bob_key,
            alice_key=self.shared_key
        )

        self.shared_key = [bit for i, bit in enumerate(self.shared_key) if i not in indices]
        self.classical_channel.bob_key = [bit for i, bit in enumerate(self.classical_channel.bob_key) if i not in indices]

    def show_results(self):
        print("\n=== Hamming(7,4) ECC Results ===")
        print("Alice bits:", self.alice.bits)
        print("Alice bases:", self.alice.bases)
        if self.eve:
            print("Eve bases:", self.eve.bases)
            print("Eve bits:", self.eve.intercepted_bits)
        print("Bob bases:", self.bob.bases)
        print("Bob measurements:", self.bob.measured_bits)
        print("Reconciled key:", self.shared_key)
        print(f"Channel lost qubits: {self.quantum_channel.loss_count}")
        print(f"Channel flipped qubits: {self.quantum_channel.flip_count}")

        if self.sample_indices is not None:
            print("\n=== Error estimation ===")
            used = len(self.sample_indices)
            total = used + len(self.shared_key)
            print(f"Used {used} bits ({round(100 * used / total, 1)}%) of key for error estimation.")
            print(f"Remaining key length after discarding sample: {len(self.shared_key)} bits")
            print(f"Sampled error rate: {round(self.error_rate * 100, 2)}%")

        print("\n=== Error correction ===")
        ec = Hamming74Corrector()
        adjusted_length = (min(len(self.shared_key), len(self.classical_channel.bob_key)) // 4) * 4
        print(f"Adjusted key length to multiple of 4: {adjusted_length}")
        print(f"Alice sifted key ({adjusted_length} bits):", self.shared_key[:adjusted_length])
        print(f"Bob sifted key ({adjusted_length} bits):", self.classical_channel.bob_key[:adjusted_length])

        corrected = ec.correct(
            self.classical_channel.bob_key[:adjusted_length],
            reference=self.shared_key[:adjusted_length]
        )

        if corrected is None:
            print("ECC failed: keys differ after decoding.")
            return

        corrected = [int(b) for b in corrected]
        self.shared_key = [int(b) for b in self.shared_key]
        print(f"Corrected Bob key ({adjusted_length} bits):", corrected)

        alice_hash = hashlib.sha256(bytes(self.shared_key[:adjusted_length])).hexdigest()[:12]
        bob_hash = hashlib.sha256(bytes(corrected)).hexdigest()[:12]
        print(f"Hash (Alice): {alice_hash}")
        print(f"Hash (Corrected Bob): {bob_hash}")

        if alice_hash == bob_hash:
            print("ECC succeeded: keys match.")
            print("\n=== Privacy amplification ===")
            required_bits = len(self.message.encode()) * 8 if self.message else 40
            amplifier = PrivacyAmplifier(output_bits=required_bits)
            self.final_key = amplifier.apply(corrected)

            shake = hashlib.shake_256()
            padded_len = ((len(corrected) + 7) // 8) * 8
            padded_bits = corrected + [0] * (padded_len - len(corrected))
            bitstring = ''.join(str(b) for b in padded_bits)
            key_bytes = int(bitstring, 2).to_bytes(padded_len // 8, byteorder='big')
            shake.update(amplifier.seed + key_bytes)
            digest = shake.digest(amplifier.output_bytes)

            print(f"Hash function used: SHAKE-256")
            print(f"Seed used (hex): {amplifier.seed.hex()}")
            print("Hashed key (hex):", digest.hex())
            print(f"Final key (binary, {required_bits} bits):", self.final_key)
        else:
            print("ECC failed: hashes differ.")
