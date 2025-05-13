#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 12 12:19:39 2025

@author: valerijvasquez
"""

from bb84.simulation import BB84Simulation
from bb84.messenger import Messenger

def main():
    print("\n--- BB84 Quantum Key Distribution Simulation ---")

    # Step 1: Enter message first
    message = input("Enter the message to send: ").strip()
    message_bytes = message.encode('utf-8')
    required_key_bits = len(message_bytes) * 8
    print(f"Message requires {required_key_bits} bits of key for one-time pad encryption.")

    # Step 2: Estimate how many qubits to send
    estimated_efficiency = 0.25
    key_length = int(required_key_bits / estimated_efficiency)
    print(f"Estimated number of qubits to send: {key_length}")

    # Step 3: Get simulation settings
    use_eve_input = input("Include eavesdropping? (y/n): ").strip().lower()
    use_eve = use_eve_input == 'y'
    eve_fraction = 0.0
    if use_eve:
        eve_fraction = float(input("Fraction of qubits Eve should intercept (e.g., 0.5): "))

    flip_probability = float(input("Bit flip probability (0.0 to 1.0): "))
    loss_probability = float(input("Qubit loss probability (0.0 to 1.0): "))

    use_hashing_input = input("Use SHA-256 hashing for privacy amplification? (y/n): ").strip().lower()
    use_hashing = use_hashing_input == 'y'

    error_threshold = float(input("Set error rate threshold for accepting the key (e.g., 0.1): "))

    while True:
        sim = BB84Simulation(
            key_length=key_length,
            use_eve=use_eve,
            eve_fraction=eve_fraction,
            use_hashing=use_hashing,
            flip_probability=flip_probability,
            loss_probability=loss_probability
        )

        sim.run()
        sim.show_results()

        if sim.error_rate is not None and sim.error_rate > error_threshold:
            print(f"\n⚠️  ERROR RATE TOO HIGH ({round(sim.error_rate * 100, 2)}%) > THRESHOLD ({error_threshold * 100}%)")
            retry = input("Do you want to try a new channel? (y/n): ").strip().lower()
            if retry != 'y':
                print("Aborting simulation.")
                break
            else:
                continue
        else:
            print("\n✅ Simulation successful and within error threshold.")

        key_available = sim.hashed_key if sim.hashed_key else sim.shared_key
        if key_available is not None and len(key_available) >= required_key_bits:
            use_message = input("\nDo you want to send the message using the final key? (y/n): ").strip().lower()
            if use_message == 'y':
                messenger = Messenger(key_available[:required_key_bits])
                messenger.send_message_with_message(message)
            else:
                print("Message transmission aborted.")
        else:
            print("Error: Final key too short for encryption.")
        break

if __name__ == "__main__":
    main()
