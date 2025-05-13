class Messenger:
    def __init__(self, key_bits):
        self.key = self._prepare_key(key_bits)

    def _prepare_key(self, key_bits):
        byte_chunks = [key_bits[i:i + 8] for i in range(0, len(key_bits), 8)]
        return bytes([
            int(''.join(str(bit) for bit in chunk), 2)
            for chunk in byte_chunks
        ])

    def send_message_with_message(self, message):
        message_bytes = message.encode('utf-8')

        if len(self.key) < len(message_bytes):
            print("Error: key too short for message length.")
            return

        encrypted = bytes([m ^ k for m, k in zip(message_bytes, self.key)])
        print(f"\nEncrypted message: {encrypted}")

        decrypted = bytes([e ^ k for e, k in zip(encrypted, self.key)])
        print(f"Decrypted message (Bob): {decrypted.decode('utf-8', errors='ignore')}")
