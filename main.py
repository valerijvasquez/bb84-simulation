from bb84.simulation import BB84Simulation

def main():
    print("\n--- BB84 Quantum Key Distribution Simulation ---")

    key_length = int(input("How many qubits to send? "))

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
            print("\n✅ Simulation successful and within error threshold.")
            break

if __name__ == "__main__":
    main()
