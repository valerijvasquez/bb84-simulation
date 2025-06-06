def xor(a, b):
    return a ^ b

def not_bit(b):
    return 0 if b == 1 else 1

def generate_codeword_ecc16(x1, x2, x3, s):
    """Generate a 7-bit codeword using one of the 16 ECCs (s ∈ [0,15])"""
    p1 = xor(x1, x2)
    p2 = xor(x2, x3)
    p3 = xor(x1, x3)
    p4 = xor(x1, xor(x2, x3))
    parity = [p1, p2, p3, p4]

    # Flip selected parity bits based on 4-bit index
    flips = [(s >> i) & 1 for i in [3, 2, 1, 0]]
    for i in range(4):
        if flips[i]:
            parity[i] = not_bit(parity[i])

    return [x1, x2, x3] + parity

def find_rule_index_from_codeword(z_chunk):
    """
    Given a 7-bit ECC codeword z_chunk, find the ECC rule index (0–15)
    that reproduces this codeword using its first 3 bits.
    """
    x1, x2, x3 = z_chunk[:3]
    for s in range(16):
        candidate = generate_codeword_ecc16(x1, x2, x3, s)
        if candidate == z_chunk:
            return s
    raise ValueError("No ECC rule found that generates the codeword.")

def hamming_distance(a, b):
    return sum(x != y for x, y in zip(a, b))

def correct_bob_codeword(z_bob, s):
    """
    Bob uses the index s to generate all 8 possible codewords using the ECC rule
    and picks the one with smallest Hamming distance to correct his received codeword.
    """
    candidates = []
    for x1 in [0, 1]:
        for x2 in [0, 1]:
            for x3 in [0, 1]:
                candidate = generate_codeword_ecc16(x1, x2, x3, s)
                candidates.append(candidate)

    return min(candidates, key=lambda cw: hamming_distance(cw, z_bob))

def simulate_fixed_example_with_one_and_two_errors():
    print("=== One Error Example ===")
    z_alice = [1, 0, 1, 0, 1, 1, 1]
    z_bob = z_alice.copy()
    z_bob[4] ^= 1  # One bit error

    x1, x2, x3 = z_alice[:3]
    s = find_rule_index_from_codeword(z_alice)

    print("Alice's original codeword (z):    ", z_alice)
    print("Alice extracts first 3 bits:      ", (x1, x2, x3))
    print("Alice determines ECC rule index: ", s)
    print("Bob receives noisy codeword (z'): ", z_bob)

    print("\nBob generates codewords with rule", s)
    candidates = []
    for a in [0, 1]:
        for b in [0, 1]:
            for c in [0, 1]:
                candidate = generate_codeword_ecc16(a, b, c, s)
                dist = hamming_distance(candidate, z_bob)
                candidates.append((candidate, dist))
                print(f"Candidate: {candidate}, Hamming distance: {dist}")

    best = min(candidates, key=lambda x: x[1])
    print("\nBob selects codeword with smallest distance:")
    print("Bob's corrected codeword (z~):    ", best[0])
    print("Match with Alice's original z:    ", "✅" if best[0] == z_alice else "❌")

    print("\n\n=== Two Error Example ===")
    z_bob_two_errors = z_alice.copy()
    z_bob_two_errors[4] ^= 1
    z_bob_two_errors[6] ^= 1

    print("Alice's original codeword (z):    ", z_alice)
    print("Bob receives noisy codeword (z'): ", z_bob_two_errors)

    print("\nBob generates codewords with rule", s)
    candidates_two = []
    for a in [0, 1]:
        for b in [0, 1]:
            for c in [0, 1]:
                candidate = generate_codeword_ecc16(a, b, c, s)
                dist = hamming_distance(candidate, z_bob_two_errors)
                candidates_two.append((candidate, dist))
                print(f"Candidate: {candidate}, Hamming distance: {dist}")

    best_two = min(candidates_two, key=lambda x: x[1])
    print("\nBob selects codeword with smallest distance:")
    print("Bob's corrected codeword (z~):    ", best_two[0])
    print("Match with Alice's original z:    ", "✅" if best_two[0] == z_alice else "❌")

simulate_fixed_example_with_one_and_two_errors()
