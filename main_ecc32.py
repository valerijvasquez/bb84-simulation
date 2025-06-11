from bb84.simulation_ecc32 import BB84Simulation
from bb84.otp import OneTimePad
from bb84.globals import binary_entropy


def main():
    print("\n--- BB84 quantum key distribution simulation ---")

    # Ask for parameters first
    use_eve = input("Include eavesdropping? (y/n): ").strip().lower() == 'y'
    eve_fraction = 0.0
    if use_eve:
        eve_fraction = float(input("Fraction of qubits Eve should intercept (0.0 to 1.0): "))

    flip_probability = float(input("Bit flip probability (0.0 to 1.0): "))
    loss_probability = float(input("Qubit loss probability (0.0 to 1.0): "))

    practical_efficiency_factor = 1.2

    # === Probe transmission ===
    probe_qubits = 100
    print(f"\nSending {probe_qubits} qubits through quantum channel to estimate error.")

    sim = BB84Simulation(
        key_length=probe_qubits,
        use_eve=use_eve,
        eve_fraction=eve_fraction,
        flip_probability=flip_probability,
        loss_probability=loss_probability
    )

    sim.run()
    sim.estimate_error_from_sample(sample_fraction=1.0)

    # Efficiency estimation
    usable_fraction = 1 - binary_entropy(sim.error_rate)
    estimated_efficiency = usable_fraction / practical_efficiency_factor

    print(f"\n=== Efficiency estimation ===")
    print(f"Error rate: {round(sim.error_rate * 100, 2)}%")
    print(f"Estimated efficiency after reconciliation: {round(estimated_efficiency * 100, 2)}%")

    # Ask user whether to proceed with full run
    proceed = input("Do you want to proceed with full message transmission based on this efficiency? (y/n): ").strip().lower()
    if proceed != 'y':
        print("Aborting simulation.")
        return

    # === Now ask for message ===
    message = input("\nEnter the message to send: ").strip()
    message_bytes = message.encode('utf-8')
    required_key_bits = len(message_bytes) * 8
    print(f"Message requires {required_key_bits} bits for OTP encryption.")

    # Compute how many qubits to send
    sifted_key_needed = required_key_bits
    raw_qubits_needed = sifted_key_needed / (estimated_efficiency * 0.5)
    key_length = int(raw_qubits_needed)

    print(f"\nAdjusted number of qubits to send: {key_length}")

    # === Full run ===
    sim = BB84Simulation(
        key_length=key_length,
        use_eve=use_eve,
        eve_fraction=eve_fraction,
        flip_probability=flip_probability,
        loss_probability=loss_probability
    )

    sim.message = message
    sim.run()
    sim.show_results()

    if not hasattr(sim, 'final_key') or sim.final_key is None:
        print("No usable final key. Cascade failed or key was too short.")
        return

    print("\n--- One-time pad encryption ---")
    use_message = input("Send the message using the final key? (y/n): ").strip().lower()
    if use_message == 'y':
        otp = OneTimePad(sim.final_key)
        encrypted = otp.encrypt(message)
        if encrypted is None:
            print("Final key too short for encryption.")
        else:
            decrypted = otp.decrypt(encrypted)
            print("Encrypted message:", encrypted)
            print("Decrypted message (Bob):", decrypted)
    else:
        print("Message transmission aborted.")

    print("Simulation complete.")

if __name__ == "__main__":
    main()
