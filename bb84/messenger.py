
class Messenger:
    def __init__(self, key_bits):
        self.key = self._prepare_key(key_bits)

    def _prepare_key(self, key_bits):
        if isinstance(key_bits, str):  # hashed string in hex
            return [int(b) for b in bin(int(key_bits, 16))[2:].zfill(256)]
        return key_bits

    def message_to_bits(self, message: str):
        return [int(b) for char in message for b in format(ord(char), '08b')]

    def bits_to_message(self, bits):
        chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
        return ''.join(chr(int(''.join(map(str, c)), 2)) for c in chars)

    def xor_bits(self, bits1, bits2):
        return [b1 ^ b2 for b1, b2 in zip(bits1, bits2)]

    def send_message(self):
        max_chars = len(self.key) // 8
        print(f"\n🔐 Final key is {len(self.key)} bits long — max {max_chars} ASCII characters.")

        while True:
            message = input("✉️  Enter message to send: ")
            message_bits = self.message_to_bits(message)

            if len(message_bits) > len(self.key):
                print(f"⚠️  Message too long. Try again (max {max_chars} chars).")
                continue

            key_segment = self.key[:len(message_bits)]
            encrypted = self.xor_bits(message_bits, key_segment)
            decrypted = self.xor_bits(encrypted, key_segment)
            decrypted_msg = self.bits_to_message(decrypted)

            print("\n--- 🛰️ Message Transmission ---")
            print("Original message:      ", message)
            print("Message bits:          ", message_bits)
            print("Key bits used:         ", key_segment)
            print("Encrypted bits:        ", encrypted)

            print("\n--- 🤖 Bob's Decryption ---")
            print("Decrypted bits:        ", decrypted)
            print("🔓 Bob receives:       ", decrypted_msg)
            break
