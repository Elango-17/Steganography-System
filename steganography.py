from PIL import Image
import numpy as np

def encode_image(image_path, message, output_path):
    try:
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image_array = np.array(image)

        # Convert the message to binary
        message_binary = ''.join(format(ord(char), '08b') for char in message)
        # Add end marker
        message_binary += '1111111111111110'
        
        # Check if the image has enough capacity to store the message
        if len(message_binary) > image_array.size:
            raise ValueError("Message is too large to be hidden in the image.")
        
        flat_image = image_array.flatten()
        message_index = 0
        
        for i in range(len(flat_image)):
            if message_index < len(message_binary):
                flat_image[i] = (flat_image[i] & 0xFE) | int(message_binary[message_index])
                message_index += 1
        
        # Reshape the image back to its original dimensions
        encoded_image = flat_image.reshape(image_array.shape)
        encoded_image_pil = Image.fromarray(encoded_image.astype('uint8'))
        encoded_image_pil.save(output_path)
        
        print("Encoding complete")
    except Exception as e:
        print(f"Error during encoding: {e}")

def decode_image(image_path):
    try:
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image_array = np.array(image)
        
        flat_image = image_array.flatten()
        message_binary = ''
        end_marker = '1111111111111110'
        
        for value in flat_image:
            message_binary += str(value & 1)
            if len(message_binary) >= len(end_marker) and message_binary[-len(end_marker):] == end_marker:
                message_binary = message_binary[:-len(end_marker)]
                break
        
        if len(message_binary) % 8 != 0:
            return "This image doesn't contain any message or the message is corrupted."
        
        message = ''.join(chr(int(message_binary[i:i+8], 2)) for i in range(0, len(message_binary), 8))
        print("Decoding complete")
        return message
    except Exception as e:
        print(f"Error during decoding: {e}")
        return "Error during decoding."

# Test the functions
# encode_image('example.jpg', 'Hello, World!', 'encoded_example.jpg')
# print(decode_image('encoded_example.jpg'))
