# Import necessary libraries
import streamlit as st
import speech_recognition as sr
import google.generativeai as gen_ai
import os
from dotenv import load_dotenv
from gtts import gTTS
from io import BytesIO

# Load environment variables
load_dotenv()

# Initialize recognizer
recognizer = sr.Recognizer()

# Configure Google Gemini API
GOOGLE_API_KEY = 'AIzaSyAhYPPra6fcIa96tkTTYgez5QWY0ydVzb0'

if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY environment variable not set.")
else:
    try:
        gen_ai.configure(api_key=GOOGLE_API_KEY)
        model = gen_ai.GenerativeModel('gemini-pro')
    except Exception as e:
        st.error(f"Error configuring Google Gemini API: {e}")

# Function to convert speech to text
def speech_to_text(audio_data):
    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return "Sorry, I did not understand that. Try again recording."
    except sr.RequestError:
        return "Sorry, there seems to be a network issue."

# Function to get response from Gemini
def get_gemini_response(prompt):
    if prompt == "Sorry, I did not understand that. Try again recording." or prompt == "Sorry, there seems to be a network issue.":
        return "Please, Speak clearly !!"
    else:
        text_prompt = "Give a response in a single line for the following prompt without emojis and symbols (give only text as output): "
        user_prompt = text_prompt + prompt
        
        # Initialize chat session if not already present
        if "chat_session" not in st.session_state:
            st.session_state.chat_session = model.start_chat(history=[])

        # Send the user's message to Gemini-Pro and get the response
        chat_session = st.session_state.chat_session
        gemini_response = chat_session.send_message(user_prompt)
        return gemini_response.text.strip()

# Function to convert text to speech
def text_to_speech(text):
    tts = gTTS(text, lang='en')
    audio_data = BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)
    return audio_data

# Streamlit UI
st.title("Speech-to-Speech LLM Bot")

# Initialize user_input and recording_state
user_input = ""
response = ""
recording = False

# Placeholder for the "Listening..." message
status_placeholder = st.empty()

# Audio capture button
if st.button("Start Recording"):
    recording = True
    status_placeholder.write("Listening...")

    # Capture audio via microphone
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
        user_input = speech_to_text(audio)
        st.write(f"You said: {user_input}")
    
    # Clear the "Listening..." message
    status_placeholder.empty()
    recording = False

# Call Gemini API to generate response if user_input has a value
if user_input:
    response = get_gemini_response(user_input)
    st.write(f"Bot: {response}")
    audio_data = text_to_speech(response)
    st.audio(audio_data, format='audio/mp3')