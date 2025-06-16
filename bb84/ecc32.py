import itertools


class ECC32:
    def __init__(self):
        self.corrected_key = []
        self.failed_blocks = 0

    def run(self, alice_key, bob_key):
        print("\n=== Information reconciliation: running ECC32 ===")

        key_len = len(alice_key)
        truncate_len = (key_len // 31) * 31
        alice_key = alice_key[:truncate_len]
        bob_key = bob_key[:truncate_len]

        corrected_blocks = []
        failed_blocks = 0

        for i in range(0, truncate_len, 31):
            a_block = alice_key[i:i+31]
            b_block = bob_key[i:i+31]

            s = self._find_rule_for_alice_block(a_block)
            if s is None:
                failed_blocks += 1
                continue

            corrected = self._correct_bob_block(b_block, s)
            if sum(a != b for a, b in zip(corrected, a_block)) > 0:
                failed_blocks += 1
                continue

            corrected_blocks.extend(corrected)

        self.corrected_key = corrected_blocks
        self.failed_blocks = failed_blocks

        print(f"ECC32 finished: {failed_blocks} blocks failed.")
        if failed_blocks == 0:
            return "SUCCESS", corrected_blocks
        else:
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
        x1, x2, x3, x4, x5 = block[:5]
        for s in range(2**26):
            if self._generate_codeword(x1, x2, x3, x4, x5, s) == block:
                return s
        return None

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




