import hashlib
import itertools


class ECC32:
    def __init__(self):
        self.corrected_key = []

    def run(self, alice_key, bob_key):
        key_len = len(alice_key)
        truncate_len = (key_len // 31) * 31
        alice_key = alice_key[:truncate_len]
        bob_key = bob_key[:truncate_len]

        corrected_blocks = []

        for i in range(0, truncate_len, 31):
            alice_block = alice_key[i:i+31]
            bob_block = bob_key[i:i+31]
            try:
                s = self._find_rule_for_alice_block(alice_block)
            except ValueError:
                corrected_blocks.extend(bob_block)
                continue

            corrected_block = self._correct_bob_block(bob_block, s)
            corrected_blocks.extend(corrected_block)

        self.corrected_key = corrected_blocks

        def hash_bits(bits):
            return hashlib.sha256(bytes(bits)).hexdigest()
        
        alice_hash = hash_bits(alice_key)
        bob_hash = hash_bits(corrected_blocks)

        print(f"Alice hash: {alice_hash[:10]}...")
        print(f"Bob hash: {bob_hash[:10]}...")

        if alice_hash == bob_hash:
            print("ECC32 attempt successful: hashes match.")
            return "SUCCESS", corrected_blocks
        else:
            print("ECC32 attempt failed: hashes do not match.")
            return "FAILURE", corrected_blocks

    def _generate_codeword(self, x1, x2, x3, x4, x5, s):
        p = [
            x1 ^ x2,
            x1 ^ x3,
            x1 ^ x4,
            x1 ^ x5,
            x2 ^ x3,
            x2 ^ x4,
            x2 ^ x5,
            x3 ^ x4,
            x3 ^ x5,
            x4 ^ x5,
            x1 ^ x2 ^ x3,
            x1 ^ x2 ^ x4,
            x1 ^ x2 ^ x5,
            x1 ^ x3 ^ x4,
            x1 ^ x3 ^ x5,
            x1 ^ x4 ^ x5,
            x2 ^ x3 ^ x4,
            x2 ^ x3 ^ x5,
            x2 ^ x4 ^ x5,
            x3 ^ x4 ^ x5,
            x1 ^ x2 ^ x3 ^ x4,
            x1 ^ x2 ^ x3 ^ x5,
            x1 ^ x2 ^ x4 ^ x5,
            x1 ^ x3 ^ x4 ^ x5,
            x2 ^ x3 ^ x4 ^ x5,
            x1 ^ x2 ^ x3 ^ x4 ^ x5
        ]

        for i in range(26):
            if (s >> i) & 1:
                p[i] ^= 1

        return [x1, x2, x3, x4, x5] + p

    def _find_rule_for_alice_block(self, block):
        x = block[:5]
        p = [
            x[0] ^ x[1],
            x[0] ^ x[2],
            x[0] ^ x[3],
            x[0] ^ x[4],
            x[1] ^ x[2],
            x[1] ^ x[3],
            x[1] ^ x[4],
            x[2] ^ x[3],
            x[2] ^ x[4],
            x[3] ^ x[4],
            x[0] ^ x[1] ^ x[2],
            x[0] ^ x[1] ^ x[3],
            x[0] ^ x[1] ^ x[4],
            x[0] ^ x[2] ^ x[3],
            x[0] ^ x[2] ^ x[4],
            x[0] ^ x[3] ^ x[4],
            x[1] ^ x[2] ^ x[3],
            x[1] ^ x[2] ^ x[4],
            x[1] ^ x[3] ^ x[4],
            x[2] ^ x[3] ^ x[4],
            x[0] ^ x[1] ^ x[2] ^ x[3],
            x[0] ^ x[1] ^ x[2] ^ x[4],
            x[0] ^ x[1] ^ x[3] ^ x[4],
            x[0] ^ x[2] ^ x[3] ^ x[4],
            x[1] ^ x[2] ^ x[3] ^ x[4],
            x[0] ^ x[1] ^ x[2] ^ x[3] ^ x[4]
        ]

        parity_bits = block[5:]
        s_bits = [p[i] ^ parity_bits[i] for i in range(26)]

        # Convert list of bits to integer
        s = sum((bit << i) for i, bit in enumerate(s_bits))
        return s

    def _correct_bob_block(self, bob_block, s):
        min_dist = 32
        best = None
        for xbits in itertools.product([0, 1], repeat=5):
            candidate = self._generate_codeword(*xbits, s)
            dist = sum((a != b) for a, b in zip(candidate, bob_block))
            if dist < min_dist:
                min_dist = dist
                best = candidate
        return best

