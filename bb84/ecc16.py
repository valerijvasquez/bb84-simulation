import itertools

class ECC16:
    def __init__(self):
        self.corrected_key = []
        self.failed_blocks = 0

    def run(self, alice_key, bob_key):

        key_len = len(alice_key)
        truncate_len = (key_len // 7) * 7
        alice_key = alice_key[:truncate_len]
        bob_key = bob_key[:truncate_len]

        corrected_blocks = []
        failed_blocks = 0

        for i in range(0, truncate_len, 7):
            alice_block = alice_key[i:i+7]
            bob_block = bob_key[i:i+7]

            try:
                s = self._find_rule_index_from_codeword(alice_block)
            except ValueError:
                failed_blocks += 1
                continue

            corrected_block = self._correct_bob_codeword(bob_block, s)
            dist = sum((a != b) for a, b in zip(corrected_block, alice_block))
            if dist > 0:
                failed_blocks += 1
                continue

            corrected_blocks.extend(corrected_block)

        self.corrected_key = corrected_blocks
        self.failed_blocks = failed_blocks

        print(f"\nECC16 finished: {failed_blocks} blocks failed to be corrected.")
        if failed_blocks == 0:
            print("ECC16 attempt succesful: all blocks corrected")
            return "SUCCESS", corrected_blocks
        else:
            print("ECC16 attempt failed: some blocks could not be corrected")
            return "FAILURE", corrected_blocks

    def _generate_codeword(self, x1, x2, x3, s):
        p = [
            x1 ^ x2,
            x2 ^ x3,
            x1 ^ x3,
            x1 ^ x2 ^ x3
        ]
        for i in range(4):
            if (s >> i) & 1:
                p[i] ^= 1
        return [x1, x2, x3] + p

    def _find_rule_index_from_codeword(self, z_chunk):
        x1, x2, x3 = z_chunk[:3]
        for s in range(16):
            if self._generate_codeword(x1, x2, x3, s) == z_chunk:
                return s
        raise ValueError("No ECC rule found.")

    def _correct_bob_codeword(self, bob_codeword, s):
        min_dist = 7
        best = None
        for xbits in itertools.product([0, 1], repeat=3):
            candidate = self._generate_codeword(*xbits, s)
            dist = sum((a != b) for a, b in zip(candidate, bob_codeword))
            if dist < min_dist:
                min_dist = dist
                best = candidate
        return best



