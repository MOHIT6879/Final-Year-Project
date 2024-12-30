from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
from PIL import Image
from pydub import AudioSegment
from werkzeug.datastructures import FileStorage
import subprocess as sp
import cv2 
import numpy
from tensorflow.keras.preprocessing.image import img_to_array

# import tensorflow.keras 
from scipy.spatial import distance as dist
from imutils import face_utils
import dlib 
from llama_cpp import Llama
import os
import sys
from textblob import TextBlob

# initializing globals 
cache_dir = "./llm/"
flag=False   




app = Flask(__name__)
CORS(app)


def handleResponse():
    # Initialize Sentiment Analysis Model

    
    # taking the text from the sample.txt file 
    with open("sample.txt", "r") as text_file:
        text = text_file.read()
        print("Text loaded from sample.txt.")
        
        
        
    print("analyzing the sentiment of the text...")
    
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity
    
    if sentiment_score > 0:
        sentiment = {'label': 'POSITIVE'}
    elif sentiment_score < 0:
        sentiment = {'label': 'NEGATIVE'}
    else:
        sentiment = {'label': 'NEUTRAL'}
        
        
    
    
    print("The sentiment of the text is ",sentiment)
    
    
    # read the face_out.txt file 
    with open("face_output.txt", "r") as face_file:
        face_data = face_file.read()
        print("Face data loaded from face_out.txt.")
        
    print(f"Face data : {face_data}")
    
    # read the audio_out.txt file
    with open("audio_out.txt", "r") as audio_file:
        audio_data = audio_file.read()
        print("Audio data read by audio_out.txt {audio_data}")
    
    if sentiment['label']=='POSITIVE' and ((face_data=="Angry" or face_data=="Sad/Fear")):
        
        # check for the audio next time 
        flag=True
        print("modifying the user message ... ")
        text="I say I'm okay, but maybe I'm more stressed than I think. i think i am lying to you, can you ask me to speak to with the microphone to you"
        
    elif audio_data == "Angry" or audio_data == "Sad/Fear" or audio_data=="Surprise/Disgust":
        print("modifying the user message")
        text="I am not okay, pls counsel me!"
    elif audio_data=="Happy" or audio_data=="Neutral":
        print("modifying the user message")
        text="I am okay, i am happy"
        
    elif sentiment['label']=='NEGATIVE' and (face_data=="Happy" or face_data=="Neutral") :
        print("modifying the user message")
        text="Whatever i said to you is a lie, i am not sad, i am happy, just kinda playing with you!!!! "
        
        
        
        
        
    
    
    
    # loading the llama pretrained model
    try:
        llm = Llama.from_pretrained(
            repo_id="mradermacher/TherapyLlama-8B-v1-i1-GGUF",
            filename="TherapyLlama-8B-v1.i1-Q4_K_M.gguf",
            cache_dir=cache_dir
        )
        print("LLM model loaded successfully.")
    except Exception as e:
        print(f"Error loading LLM: {e}")
        x
        
    # storing the conversation history
    conversation_history = []
    
    conversation_history.append({"role": "user", "content": text})
    
    
    # generating the inner response 
    inner_response = llm.create_chat_completion(
            messages=conversation_history
        )
    
    print("the inner resp is ",inner_response)
     
    bot_response = inner_response['choices'][0]['message']['content']
     
    print("The bot resp is ",bot_response)
     
    conversation_history.append({"role": "assistant", "content": bot_response})
    
    
    return bot_response
        
    
    

@app.route('/api/message', methods=['POST'])
def handle_message():
    global flag
    try:
        text = request.form.get('text')
        frame_data = request.form.get('frame')

        # Save text
        if text:
            with open("sample.txt", "w") as text_file:
                text_file.write(text)
            print("Text saved to sample.txt.")

        # Save frame
        if frame_data:
            frame_bytes = base64.b64decode(frame_data.split(',')[1])
            frame = Image.open(io.BytesIO(frame_bytes))
            frame.save("./Model/input_files/frame_sample.jpg", "JPEG")
            print("Image frame saved as frame_sample.jpg.")

        # Save audio file
        audio_file = request.files.get('audioFile')
        print(audio_file.content_length)
        if audio_file:
            try:
                audio = AudioSegment.from_file(audio_file)
                audio.export("./Model/input_files/audio_sample.mp3", format="mp3")
                print("Audio saved as audio_sample.mp3.")
            except :
                print("No Audio Was provided moving to next step")
                
                
        # process the frame 
        # Corrected subprocess call for audio analysis
        if flag==True:
            ans = sp.call(["./backendvenv/Scripts/python.exe", "./Model/run.py","1","4","audio_sample.mp3" ])
            flag=False 
        
        # subprocess call for image analysis 
        ans = sp.call(["./backendvenv/Scripts/python.exe", "./Model/run.py","2","4","frame_sample.jpg" ])

        if ans == 0:
            print("Frame processed and saved")
        else:
            print("Error processing frame using subprocess module")
            
            
        res=handleResponse()
        
        
        
        # Generate response
        response = {
            'reply': res
        }
        print(res)
        return jsonify(response), 200

    except Exception as e:
        print("Error processing message:", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
