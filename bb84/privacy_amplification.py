
import hashlib
import secrets

class PrivacyAmplifier:
    def __init__(self, output_bits: int = 40):
        self.output_bits = output_bits
        self.output_bytes = (output_bits + 7) // 8
        self.seed = secrets.token_bytes(16)

    def apply(self, key_bits: list) -> list:
        # Pad key_bits to make its length divisible by 8
        padded_len = ((len(key_bits) + 7) // 8) * 8
        padded_bits = key_bits + [0] * (padded_len - len(key_bits))

        # Convert to bytes
        bitstring = ''.join(str(b) for b in padded_bits)
        key_bytes = int(bitstring, 2).to_bytes(padded_len // 8, byteorder='big')

        # Hash using SHAKE-256 with seed
        shake = hashlib.shake_256()
        shake.update(self.seed + key_bytes)
        digest = shake.digest(self.output_bytes)

        # Convert digest to bit list
        digest_bits = ''.join(f"{byte:08b}" for byte in digest)
        return [int(bit) for bit in digest_bits[:self.output_bits]]
