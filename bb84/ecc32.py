import itertools


class ECC32:
    def __init__(self):
        self.corrected_key = []
        self.failed_blocks = 0

    def run(self, alice_key, bob_key):

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

        print(f"\nECC32 finished: {failed_blocks} blocks failed to be corrected.")
        if failed_blocks == 0:
            print("ECC32 attempt successful: all blocks corrected.")
            return "SUCCESS", corrected_blocks
        else:
            print("ECC32 attempt failed: some blocks could not be corrected.")
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

