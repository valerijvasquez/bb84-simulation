import hashlib
from itertools import product


class ECCXOR:
    def __init__(self):
        self.codebook = self._generate_codebook()

    def _generate_codebook(self):
        codebook = {}
        for x1, x2, x3 in product([0, 1], repeat=3):
            data = [x1, x2, x3]
            codeword = [
                x1, x2, x3,
                x1 ^ x2,
                x1 ^ x3,
                x2 ^ x3,
                x1 ^ x2 ^ x3
            ]
            codebook[tuple(codeword)] = data
        return codebook

    def _hamming_distance(self, a, b):
        return sum(x != y for x, y in zip(a, b))

    def _decode_block(self, noisy_block):
        min_dist = 8
        best = None
        for codeword, data in self.codebook.items():
            dist = self._hamming_distance(noisy_block, codeword)
            if dist < min_dist:
                min_dist = dist
                best = data
        return best

    def encode(self, bits):
        encoded = []
        for i in range(0, len(bits), 3):
            chunk = bits[i:i+3]
            while len(chunk) < 3:
                chunk += [0]
            x1, x2, x3 = chunk
            encoded += [
                x1, x2, x3,
                x1 ^ x2,
                x1 ^ x3,
                x2 ^ x3,
                x1 ^ x2 ^ x3
            ]
        return encoded

    def correct(self, alice_bits, bob_bits):
        length = (min(len(alice_bits), len(bob_bits)) // 3) * 3
        alice_bits = alice_bits[:length]
        bob_bits = bob_bits[:length]

        corrected = []
        for i in range(0, length, 3):
            a_block = alice_bits[i:i+3]
            b_block = bob_bits[i:i+3]
            if len(b_block) < 3:
                continue

            x1, x2, x3 = a_block
            received = [
                b_block[0], b_block[1], b_block[2],
                x1 ^ x2,
                x1 ^ x3,
                x2 ^ x3,
                x1 ^ x2 ^ x3
            ]

            decoded = self._decode_block(received)
            corrected += decoded

        ha = self.hash_bits(alice_bits)
        hb = self.hash_bits(corrected)

        if ha == hb:
            return corrected
        else:
            return None

    def hash_bits(self, bits):
        return hashlib.sha256(''.join(map(str, bits)).encode()).hexdigest()
    
    def run(self, alice_key, bob_key):
        corrected = self.correct(alice_key, bob_key)
        print("\nECCXOR finished: checking key consistency via hash.")
        if corrected:
            print("ECCXOR attempt successful: all blocks corrected.")
            return "SUCCESS", corrected
        else:
            print("ECCXOR attempt failed: key mismatch detected.")
            return "FAILURE", None



