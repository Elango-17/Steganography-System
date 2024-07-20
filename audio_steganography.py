import wave
import os

def encode_audio(audio_file, message, output_path):
    try:
        # Open the audio file
        audio = wave.open(audio_file, mode='rb')
        frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))
        print(f"Original audio frame bytes length: {len(frame_bytes)}")

        # Convert the message to binary
        message_binary = ''.join(format(ord(char), '08b') for char in message)
        message_binary += '1111111111111110'  # End-of-message marker
        print(f"Message binary length: {len(message_binary)}")

        # Embed the message into the audio file
        message_index = 0
        for i in range(len(frame_bytes)):
            if message_index < len(message_binary):
                frame_bytes[i] = (frame_bytes[i] & 0xFE) | int(message_binary[message_index])
                message_index += 1

        # Create a new audio file with the embedded message
        frame_modified = bytes(frame_bytes)
        with wave.open(output_path, 'wb') as encoded_audio:
            encoded_audio.setparams(audio.getparams())
            encoded_audio.writeframes(frame_modified)
        audio.close()
        print(f"Encoded audio saved to {output_path}")

        # Verify that the file has been created
        if os.path.exists(output_path):
            print("File creation successful")
        else:
            print("File creation failed")
    except Exception as e:
        print(f"Error in encoding audio: {e}")

def decode_audio(audio_file):
    try:
        # Open the audio file
        audio = wave.open(audio_file, mode='rb')
        frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))

        # Extract the least significant bit of each byte
        message_binary = ''
        for byte in frame_bytes:
            message_binary += str(byte & 1)

        # Convert the binary message to characters
        message_bytes = [message_binary[i:i+8] for i in range(0, len(message_binary), 8)]
        decoded_message = ''.join([chr(int(byte, 2)) for byte in message_bytes])
        audio.close()
        
        # Extract message up to end-of-message marker
        end_marker = '1111111111111110'
        end_index = message_binary.find(end_marker)
        if end_index != -1:
            decoded_message = ''.join([chr(int(message_binary[i:i+8], 2)) for i in range(0, end_index, 8)])
            return decoded_message
        else:
            return "End marker not found. Decoded message may be incomplete or corrupted."
    except Exception as e:
        print(f"Error in decoding audio: {e}")
        return "Error in decoding audio."