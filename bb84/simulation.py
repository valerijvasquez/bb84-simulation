import hashlib
import random
from .sender import QubitSender
from .receiver import QubitReceiver
from .quantum_channel import QuantumChannel
from .classical_channel import ClassicalChannel
from .eavesdropper import Eavesdropper
from .privacy_amplification import PrivacyAmplifier
from .ecc_xor import ECCXOR
from .ecc16 import ECC16
from .ecc32 import ECC32
from .hamming74 import Hamming74
from .cascade import Cascade
from .otp import OneTimePad

class BB84Simulation:
  
    def __init__(self, key_length=20, use_eve=False, eve_fraction=1.0,
                 flip_probability=0.0, loss_probability=0.0, ecc=None):
        self.key_length = key_length
        self.use_eve = use_eve
        self.eve_fraction = eve_fraction
        self.flip_probability = flip_probability
        self.loss_probability = loss_probability
        self.ecc = ecc
        self.message = None


    def run(self):
        self._prepare_parties()
        self._transmit_qubits()
        self._basis_reconciliation()
        self._estimate_error()
        self._print_transmission_info()
        self._select_and_run_ecc()
        self._show_privacy_amplification()
        self._otp_encrypt()


    def _prepare_parties(self):
        self.alice = QubitSender(self.key_length)
        self.bob = QubitReceiver()
        self.eve = Eavesdropper(self.eve_fraction) if self.use_eve else None
        self.alice.prepare_qubits()
        self.quantum_channel = QuantumChannel(
            flip_probability=self.flip_probability,
            loss_probability=self.loss_probability,
            eavesdropper=self.eve
        )


    def _transmit_qubits(self):
        transmitted = [
            self.quantum_channel.transmit(self.alice.encode_single_qubit(i), i)
            for i in range(self.key_length)
        ]
        for i, state in enumerate(transmitted):
            self.bob.receive_single_qubit(state, i)


    def _basis_reconciliation(self):
        self.classical_channel = ClassicalChannel(self.alice, self.bob)
        self.shared_key = self.classical_channel.reconcile_key()


    def _estimate_error(self):
        alice = self.alice.reconciled_key
        bob = self.bob.reconciled_key
        sample_size = int(0.2 * len(alice))
        self.sample_indices = random.sample(range(len(alice)), sample_size)
        sample_alice = [alice[i] for i in self.sample_indices]
        sample_bob = [bob[i] for i in self.sample_indices]
        errors = sum(a != b for a, b in zip(sample_alice, sample_bob))
        self.estimated_error_rate = errors / sample_size if sample_size else 0.0
        self.alice.reconciled_key = [bit for i, bit in enumerate(alice) if i not in self.sample_indices]
        self.bob.reconciled_key = [bit for i, bit in enumerate(bob) if i not in self.sample_indices]


    def _print_transmission_info(self):
        print("\n=== Transmission information ===")
        print("Alice bits:", self.alice.bits[:10], "...")
        print("Alice bases:", self.alice.bases[:10], "...")
        if self.eve:
            print("\nEve bases:", list(self.eve.bases.items())[:10], "...")
            print("Eve bits:", list(self.eve.intercepted_bits.values())[:10], "...")
        print("\nBob bases:", self.bob.bases[:10], "...")
        print("Bob measurements:", self.bob.measured_bits[:10], "...")
        print("\nSifted key:", self.shared_key[:10], "...")
        print(f"Sifted key length: {len(self.shared_key)} bits")
        print(f"Channel lost qubits: {self.quantum_channel.loss_count}")
        print(f"Channel flipped qubits: {self.quantum_channel.flip_count}")

        print("\n=== Error estimation ===")
        sample_used = len(self.sample_indices)
        total_before = sample_used + len(self.alice.reconciled_key)
        percent = round(100 * sample_used / total_before)
        print(f"Used {sample_used} bits ({percent}%) of key for error estimation.")
        print(f"Estimated error rate: {round(self.estimated_error_rate * 100, 2)}%")
        print(f"Remaining key length after discarding sample: {len(self.alice.reconciled_key)} bits")


    def _select_and_run_ecc(self):
        print("\n=== Error correction ===")
        options = {
            "xor": ECCXOR(),
            "hamming": Hamming74(),
            "ecc16": ECC16(),
            "ecc32": ECC32(),
            "cascade": Cascade()
        }
        print("Available ECCs:")
        for name in options:
            print(f" - {name}")
        choice = input("\nSelect ECC: ").strip().lower()
        ecc = options.get(choice)
        if ecc is None:
            print("Invalid ECC selected.")
            return
        print(f"\nRunning {choice}")
        self.ecc = ecc
        status, corrected = self.ecc.run(
            alice_key=self.shared_key,
            bob_key=self.classical_channel.bob_key
        )
        if status != "SUCCESS":
            print(f"{choice} failed: aborting protocol.")
            self.final_key = None
            return
        self.final_key = corrected


    def _show_privacy_amplification(self):
        if not self.final_key:
            return
        print("\n=== Privacy amplification ===")
        if self.message:
            required_bits = len(self.message.encode()) * 8
            print(f"Reconciled key truncated to {required_bits} bits to match message length for OTP encryption.")
        else:
            required_bits = 40
            print("No message found. Defaulting to 40-bit key.")

        amplifier = PrivacyAmplifier(output_bits=required_bits)
        self.final_key = amplifier.apply(self.final_key)

        shake = hashlib.shake_256()
        padded_len = ((len(self.final_key) + 7) // 8) * 8
        padded = self.final_key + [0] * (padded_len - len(self.final_key))
        byte_str = int(''.join(str(b) for b in padded), 2).to_bytes(padded_len // 8, 'big')
        shake.update(amplifier.seed + byte_str)
        digest = shake.digest(amplifier.output_bytes)
        print(f"Hash function used: SHAKE-256")
        print(f"Seed used (hex): {amplifier.seed.hex()}")
        print(f"Hashed key (hex): {digest.hex()}")
        print(f"Hashed key (binary, {required_bits} bits):", self.final_key)


    def _otp_encrypt(self):
        if not self.final_key or not self.message:
            return
        print("\n--- One-time pad encryption ---")
        otp = OneTimePad(self.final_key)
        encrypted = otp.encrypt(self.message)
        decrypted = otp.decrypt(encrypted)
        print("Encrypted message:", encrypted)
        print("Decrypted message:", decrypted)
        print("\nSimulation complete.")
