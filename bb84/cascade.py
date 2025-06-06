import random
import hashlib

from bb84.globals import truncate_to_power_of_two, shuffle_indices, parity, hash_bits


def binary_search_fix(alice_key, bob_key, indices):
    if len(indices) == 1:
        return [indices[0]]

    mid = len(indices) // 2
    left = indices[:mid]
    right = indices[mid:]

    a_left = [alice_key[i] for i in left]
    b_left = [bob_key[i] for i in left]
    a_right = [alice_key[i] for i in right]
    b_right = [bob_key[i] for i in right]

    if parity(a_left) != parity(b_left):
        return binary_search_fix(alice_key, bob_key, left)
    else:
        return binary_search_fix(alice_key, bob_key, right)


def cascade_round(alice_key, bob_key, block_size, shuffled_indices):
    corrected = []


    blocks = [shuffled_indices[i:i + block_size] for i in range(0, len(shuffled_indices), block_size)]

    # First pass — print all parities, collect mismatches
    mismatched_blocks = []

    for block_num, block in enumerate(blocks):
        a_block = [alice_key[i] for i in block]
        b_block = [bob_key[i] for i in block]
        p_a = parity(a_block)
        p_b = parity(b_block)

        block_log = []
        block_log.append(f"Block {block_num}: parity(Alice) = {p_a}, parity(Bob) = {p_b}")

        # Save block log immediately
       

        if p_a != p_b:
            mismatched_blocks.append((block_num, block))

    # Second pass — now dissect mismatched blocks
    for block_num, block in mismatched_blocks:
        # Add header line for clarity:
    
        
        fix = binary_search_fix(alice_key, bob_key, block)
        


        for idx in fix:
            bob_key[idx] ^= 1
            corrected.append(idx)

    return bob_key, corrected

# --------------------------------------------------------------------------

def Cascade(alice_key, bob_key):
    effective_length = truncate_to_power_of_two(len(alice_key))
    alice = alice_key[:effective_length]
    bob = bob_key[:effective_length]

    print(f"\nRunning Cascade — adjusted to {effective_length} bits (power of two).")
    print(f"Alice sifted key: {alice[:30]}...")
    print(f"Bob sifted key:   {bob[:30]}...")

    block_size = effective_length
    round_num = 1
    passes_at_block_size_2 = 0

    while True:
        print(f"Round {round_num}, block size {block_size}, ", end="")

        shuffled = list(range(effective_length)) if round_num == 1 else shuffle_indices(effective_length)
        bob, corrected = cascade_round(alice, bob, block_size, shuffled)

        print(f"corrected positions: {len(corrected)}")

        if block_size == 2:
            passes_at_block_size_2 += 1
            if passes_at_block_size_2 >= 5:
                break
        else:
            block_size //= 2

        round_num += 1

    # Final hash check
    hash_alice = hash_bits(alice)
    hash_bob = hash_bits(bob)

    if hash_alice == hash_bob:
        print("Hash match: SUCCESS")
        return "SUCCESS", bob
    else:
        print("Hash match: FAILURE — aborting.")
        return "FAILURE", None

