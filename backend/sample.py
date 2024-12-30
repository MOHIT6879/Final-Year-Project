from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
from PIL import Image
from pydub import AudioSegment


# # Explicitly set paths for ffmpeg and ffprobe if necessary
# AudioSegment.ffmpeg = which("ffmpeg")
# AudioSegment.ffprobe = which("ffprobe")

app = Flask(__name__)
CORS(app)

@app.route('/api/message', methods=['POST'])
def handle_message():
    try:
        # Parse incoming JSON data
        data = request.get_json()
        text = data.get('text')
        frame_data = data.get('frame')
        audio_data = data.get('audioData')

        # Process and save the text
        if text:
            with open("sample.txt", "w") as text_file:
                text_file.write(text)
            print("Text saved to sample.txt.")

        # Process and save the image frame (base64-encoded JPEG image)
        if frame_data:
            frame_bytes = base64.b64decode(frame_data.split(',')[1])  # Remove the data URI prefix
            frame = Image.open(io.BytesIO(frame_bytes))
            frame.save("frame_sample.jpg", "JPEG")
            print("Image frame saved as frame_sample.jpg.")

        # Process and save the audio data as an MP3
        if audio_data:
            # Convert audio data to bytes
            audio_bytes = bytes(audio_data)
            audio_file = io.BytesIO(audio_bytes)

            # Convert audio data to MP3 format using pydub
            audio_segment = AudioSegment.from_file(audio_file, format="wav")  # Assuming 'audio/wav' format
            audio_segment.export("audio_sample.mp3", format="mp3")
            print("Audio saved as audio_sample.mp3.")

        # Generate response based on the processed data
        response = {
            'reply': "Data processed and saved. Check current directory for saved files."
        }
        return jsonify(response), 200

    except Exception as e:
        print("Error processing message:", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
