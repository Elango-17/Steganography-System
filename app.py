from flask import Flask, request, render_template, send_file, redirect, url_for
import os
from werkzeug.utils import secure_filename
import steganography
import audio_steganography
import video_steganography
import encryption

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'your_secret_key'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

# Image Steganography Routes
@app.route('/image_steganography')
def image_steganography():
    return render_template('image_steganography.html')

@app.route('/encode_image', methods=['POST'])
def encode_image():
    if 'image' not in request.files or 'message' not in request.form:
        return redirect(request.url)
    
    image = request.files['image']
    message = request.form['message']
    
    if image.filename == '':
        return redirect(request.url)
    
    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)
    
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encoded_' + filename)
    steganography.encode_image(image_path, message, output_path)
    
    return send_file(output_path, as_attachment=True)

@app.route('/decode_image', methods=['POST'])
def decode_image():
    if 'image' not in request.files:
        return redirect(request.url)
    
    image = request.files['image']
    
    if image.filename == '':
        return redirect(request.url)
    
    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)
    
    message = steganography.decode_image(image_path)
    
    return render_template('image_steganography.html', decoded_message=message)




# Audio Steganography Routes

@app.route('/audio_steganography')
def audio_steganography_page():
    return render_template('audio_steganography.html')

@app.route('/encode_audio', methods=['POST'])
def encode_audio_route():
    if 'audio' not in request.files or 'message' not in request.form:
        print("Audio or message not found in the request")
        return redirect(request.url)
    
    audio = request.files['audio']
    message = request.form['message']
    
    if audio.filename == '':
        print("No file selected for uploading")
        return redirect(request.url)
    
    filename = secure_filename(audio.filename)
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    audio.save(audio_path)
    
    output_filename = 'encoded_' + filename
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    # Debug prints
    print(f"Audio file path: {audio_path}")
    print(f"Output file path: {output_path}")
    
    try:
        audio_steganography.encode_audio(audio_path, message, output_path)
    except Exception as e:
        print(f"Error during encoding: {e}")
        return "Error during encoding. Please try again."
    
    # Check if the file exists
    if os.path.exists(output_path):
        print("Output file created successfully")
        return send_file(output_path, as_attachment=True)
    else:
        print("Output file not found after encoding")
        return "File not found. Please try again."

@app.route('/decode_audio', methods=['POST'])
def decode_audio_route():
    if 'audio' not in request.files:
        print("Audio not found in the request")
        return redirect(request.url)
    
    audio = request.files['audio']
    
    if audio.filename == '':
        print("No file selected for uploading")
        return redirect(request.url)
    
    filename = secure_filename(audio.filename)
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    audio.save(audio_path)
    
    # Debug print
    print(f"Audio file path: {audio_path}")
    
    try:
        message = audio_steganography.decode_audio(audio_path)
        print(f"Decoded message: {message}")  # Debug print
    except Exception as e:
        print(f"Error during decoding: {e}")
        return "Error during decoding. Please try again."
    
    return render_template('audio_steganography.html', decoded_message=message)

# Video Steganography Routes

@app.route('/video_steganography')
def video_steganography_page():
    return render_template('video_steganography.html')

@app.route('/encode_video', methods=['POST'])
def encode_video_route():
    if 'video' not in request.files or 'message' not in request.form:
        return redirect(request.url)
    
    video = request.files['video']
    message = request.form['message']
    
    if video.filename == '':
        return redirect(request.url)
    
    filename = secure_filename(video.filename)
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    video.save(video_path)
    
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encoded_' + filename)
    
    try:
        video_steganography.encode_video(video_path, message, output_path)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        print(f"Error during encoding: {e}")
        return "Error during encoding. Please try again."

@app.route('/decode_video', methods=['POST'])
def decode_video_route():
    if 'video' not in request.files:
        return redirect(request.url)
    
    video = request.files['video']
    
    if video.filename == '':
        return redirect(request.url)
    
    filename = secure_filename(video.filename)
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    video.save(video_path)
    
    try:
        message = video_steganography.decode_video(video_path)
        return render_template('video_steganography.html', decoded_message=message)
    except Exception as e:
        print(f"Error during decoding: {e}")
        return "Error during decoding. Please try again."

# Encryption Routes
@app.route('/encryption')
def encryption_page():
    return render_template('encryption.html')

@app.route('/encrypt', methods=['POST'])
def encrypt():
    if 'message' not in request.form:
        return redirect(request.url)
    
    message = request.form['message']
    key = encryption.generate_key()
    encrypted_message = encryption.encrypt_message(message, key)
    
    return render_template('encryption.html', encrypted_message=encrypted_message.decode(), key=key.decode())

@app.route('/decrypt', methods=['POST'])
def decrypt():
    if 'encrypted_message' not in request.form or 'key' not in request.form:
        return redirect(request.url)
    
    encrypted_message = request.form['encrypted_message']
    key = request.form['key']
    
    try:
        decrypted_message = encryption.decrypt_message(encrypted_message.encode(), key.encode())
    except Exception as e:
        decrypted_message = "Invalid key or message."
    
    return render_template('encryption.html', decrypted_message=decrypted_message)

if __name__ == '__main__':
    app.run(debug=True)
