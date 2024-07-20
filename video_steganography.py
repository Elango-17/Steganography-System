import cv2
import numpy as np

def encode_video(video_path, message, output_path):
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error opening video file {video_path}")
            return

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'mp4v' codec for MP4 format
        out = cv2.VideoWriter(output_path, fourcc, cap.get(cv2.CAP_PROP_FPS), (int(cap.get(3)), int(cap.get(4))))

        message_binary = ''.join(format(ord(char), '08b') for char in message)
        message_binary += '1111111111111110'  # End marker
        print(f"Message binary length: {len(message_binary)}")

        message_index = 0
        ret, frame = cap.read()
        while ret:
            frame_copy = frame.copy()
            for row in frame_copy:
                for pixel in row:
                    for color in range(3):  # Loop over BGR values
                        if message_index < len(message_binary):
                            pixel[color] = (pixel[color] & 0xFE) | int(message_binary[message_index])
                            message_index += 1
                        else:
                            break
                    if message_index >= len(message_binary):
                        break
                if message_index >= len(message_binary):
                    break

            out.write(frame_copy)
            ret, frame = cap.read()

        cap.release()
        out.release()
        print(f"Message encoded into video and saved to {output_path}")
    except Exception as e:
        print(f"Error in encoding video: {e}")

def decode_video(video_path):
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error opening video file {video_path}")
            return "Error opening video file."

        message_binary = ''
        end_marker = '1111111111111110'
        end_marker_length = len(end_marker)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            for row in frame:
                for pixel in row:
                    for color in range(3):  # Loop over BGR values
                        message_binary += str(pixel[color] & 1)

                        # Check if the end marker is found
                        if len(message_binary) >= end_marker_length and message_binary[-end_marker_length:] == end_marker:
                            message_binary = message_binary[:-end_marker_length]  # Remove the end marker
                            cap.release()
                            
                            # Ensure the binary message length is a multiple of 8
                            if len(message_binary) % 8 == 0:
                                message = ''.join(chr(int(message_binary[i:i+8], 2)) for i in range(0, len(message_binary), 8))
                                print(f"Decoded message: {message}")  # Debug print
                                return message
                            else:
                                print("Decoding error: message binary length not a multiple of 8")
                                return "This video doesn't contain any message or the message is corrupted."

        cap.release()
        print("Decoding error: end marker not found")
        return "This video doesn't contain any message or the message is corrupted."
    except Exception as e:
        print(f"Error in decoding video: {e}")
        return "Error in decoding video."
