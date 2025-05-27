import numpy as np
import hashlib

from .sender import QubitSender
from .receiver import QubitReceiver
from .quantum_channel import QuantumChannel
from .classical_channel import ClassicalChannel
from .eavesdropper import Eavesdropper
from .ecc import ErrorCorrector

class BB84Simulation:
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

        transmitted_states = []
        for i in range(self.key_length):
            state = self.alice.encode_single_qubit(i)
            transmitted = self.quantum_channel.transmit(state, i)
            transmitted_states.append(transmitted)


        for i, state in enumerate(transmitted_states):
            self.bob.receive_single_qubit(state, i)


        self.classical_channel = ClassicalChannel(self.alice, self.bob)
        self.shared_key = self.classical_channel.reconcile()

    def estimate_error_from_sample(self, fraction=0.2):
        key_length = len(self.classical_channel.bob_key)
        indices = self.alice.choose_sample_indices(key_length, fraction)
        self.classical_channel.send_sample_indices(indices)
        self.sample_indices = indices

        self.error_rate = self.bob.compare_sample(
            bob_key=self.classical_channel.bob_key,
            alice_key=self.shared_key
        )

        self.shared_key = [bit for i, bit in enumerate(self.shared_key) if i not in indices]
        self.classical_channel.bob_key = [bit for i, bit in enumerate(self.classical_channel.bob_key) if i not in indices]

    def show_results(self):
        print("\n=== RESULTS ===")
        print("Alice bits:       ", self.alice.bits)
        print("Alice bases:      ", self.alice.bases)
        if self.eve:
            print("Eve bases:        ", self.eve.bases)
            print("Eve bits:         ", self.eve.intercepted_bits)
        print("Bob bases:        ", self.bob.bases)
        print("Bob measurements: ", self.bob.measured_bits)
        print("Reconciled key:   ", self.shared_key)
        print(f"Channel lost qubits: {self.quantum_channel.loss_count}")
        print(f"Channel flipped qubits: {self.quantum_channel.flip_count}")

        if self.sample_indices is not None:
            print("\n=== ERROR ESTIMATION ===")
            print(f"Used {len(self.sample_indices)} bits ({round(100 * len(self.sample_indices) / (len(self.shared_key) + len(self.sample_indices)), 1)}%) of key for error estimation.")
            print(f"Remaining key length after discarding sample: {len(self.shared_key)} bits")
            print(f"Sampled error rate: {round(self.error_rate * 100, 2)}%")

        # 3. ECC Section
        ec = ErrorCorrector()
        print("\n=== ERROR CORRECTION ===")
        adjusted_length = len(self.shared_key) - (len(self.shared_key) % 3)
        print(f"Adjusted key length to multiple of 3: {adjusted_length}")
        print(f"Alice sifted key ({adjusted_length} bits):     ", self.shared_key[:adjusted_length])
        print(f"Bob sifted key ({adjusted_length} bits):       ", self.classical_channel.bob_key[:adjusted_length])
        corrected = ec.correct(self.shared_key[:adjusted_length], self.classical_channel.bob_key[:adjusted_length])
        if corrected is None:
            print("❌ ECC FAILED: mismatched or invalid input for correction.")
            self.final_key = None  
            return

        print(f"Corrected Bob key ({adjusted_length} bits):    ", corrected[:adjusted_length])

        alice_hash = hashlib.sha256(bytes(self.shared_key[:adjusted_length])).hexdigest()[:12]
        bob_hash = hashlib.sha256(bytes(corrected)).hexdigest()[:12]
        print(f"Hash (Alice): {alice_hash}")
        print(f"Hash (Corrected Bob): {bob_hash}")

        if alice_hash == bob_hash:
            print("✅ ECC SUCCESS: keys match.")

            # 4. Privacy Amplification
            from .privacy_amplification import PrivacyAmplifier

            print("\n=== PRIVACY AMPLIFICATION ===")
            if hasattr(self, 'message') and self.message:
                required_bits = len(self.message.encode()) * 8
                print(f"Message requires {required_bits} bits for OTP encryption.")
            else:
                required_bits = 40
                print("No message found. Defaulting to 40-bit final key.")

            amplifier = PrivacyAmplifier(output_bits=required_bits)
            self.final_key = amplifier.apply(corrected)

            shake = hashlib.shake_256()
            padded_len = ((len(corrected) + 7) // 8) * 8
            padded_bits = corrected + [0] * (padded_len - len(corrected))
            bitstring = ''.join(str(b) for b in padded_bits)
            key_bytes = int(bitstring, 2).to_bytes(padded_len // 8, byteorder='big')
            shake.update(amplifier.seed + key_bytes)
            digest = shake.digest(amplifier.output_bytes)
            digest_bits = ''.join(f"{byte:08b}" for byte in digest)

            print(f"Hash function used: SHAKE-256")
            print(f"Seed used (hex): {amplifier.seed.hex()}")
            print("Hashed key (hex):", digest.hex())
            print(f"Hashed key (binary, {required_bits} bits):", self.final_key)


          

        else:
            print("❌ ECC FAILED: keys differ.")
