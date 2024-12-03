from datetime import datetime
import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import re
from googleapiclient.discovery import build
import requests
import streamlit.components.v1 as components
import time
import yt_dlp
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from deepgram import DeepgramClient, DeepgramClientOptions, PrerecordedOptions, FileSource
import httpx

# Load environment variables
load_dotenv()
huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
youtube_api_key = os.getenv("YOUTUBE_API_KEY")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
assemblyai_api_key = os.getenv("ASSEMBLYAI_API_KEY")

# Configuring the page content
st.title('svAIsthi - Svasth with AI')
st.caption('Your AI assistant for health education and help')

# Image uploader (Allow the user to upload images)
imaged = st.file_uploader("Choose the image", type=["jpg", "png", "jpeg", "webp"])
if imaged:
    st.image(imaged, caption="Image Uploaded", use_container_width=True)

enable = st.checkbox('Enable camera')
picture = st.camera_input('Take a picture', disabled=not enable)

if imaged or picture is not None:
    imgg = Image.open(imaged if imaged else picture)




# User information inputs
st.header('User Information')
user_name = st.text_input('Please input your name')
user_age = st.number_input('Please enter your age', min_value=0)
previous_conditions = st.text_input('Please enter your previous conditions')
current_condition = st.text_input('Please enter your current medical conditions')
previous_medication = st.text_input('Please enter your previous medication')
current_medication = st.text_input('Please enter your current medication')
medication_routine = st.text_input('Please enter your medication routine')

# User input prompt
user_inp = f"""provide a disclaimer that this is not a medical advice but just a handy tool. According to these factors the user is {user_age} years old, the user had {previous_conditions} previously and now suffering from {current_condition} the user used {previous_medication} for {previous_conditions}, now using {current_medication} for {current_condition} for {medication_routine}, can you please look at the uploaded image and help the user to properly use the device with a step-by-step detailed guide along with any relevant internet resources? make sure the prompt is generated according to the user's age. Start the guide with the greeting Hi {user_name} then "Title:" name of the device and in the next paragraph provide an overview of the Purpose of the device, highlighting how it may support the user’s specific current condition and needs related to age, then proceed with the step-by-step guide with relevant side headings, in the next section Explain the importance of following the current medication routine consistently to achieve the best therapeutic outcome. in the next section Check for potential interactions between current medications and previous medications. also explain the basic effects of the medication other than the intended effect If relevant, provide specific instructions on time intervals for using the device safely in relation to their medication schedule. and finally provide the user with the relevant internet resources for further information. In the end, wish the user good luck and a speedy recovery."""

# Hugging Face API Query Function

from huggingface_hub import InferenceClient

def query_huggingface_api(payload, model_name, huggingface_api_key):
    # Initialize the InferenceClient
    client = InferenceClient(api_key=huggingface_api_key)
    
    # Prepare the model's inputs
    messages = [{"role": "user", "content": payload["inputs"]}]
    
    # Get the model's output (generate completion)
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=500
        )
        # Extract the generated summary text
        return completion.choices[0].message['content']
    
    except Exception as e:
        print(f"Error while querying Hugging Face API: {str(e)}")
        return None


# Generate guide using Gemini AI
def genmodel(user_input, img):
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content([user_input, img])
        return response.text
    except Exception as e:
        st.error(f"Error generating content with Gemini: {str(e)}")
        return ""

# Extract YouTube video link
def extract_youtube_link(text):
    match = re.search(r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+', text)
    return match.group(0) if match else None

# Extract device title from response text
def extract_device_title(response_text):
    match = re.search(r'Title:\s*(.+?)[\.\n]', response_text)
    if match:
        title = match.group(1).strip()
        return title.rstrip('.')
    return None

# Fetch a YouTube video based on a query
def get_youtube_video(query):
    youtube = build("youtube", "v3", developerKey=youtube_api_key)
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=1
    )
    response = request.execute()
    video_id = response["items"][0]["id"]["videoId"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    return video_url

def download_youtube_audio(youtube_url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'quiet': True,  # Suppress unnecessary output
            'postprocessors': [],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            audio_file_path = f"downloads/{info_dict['id']}.webm"  # You may get webm or another audio format
            return audio_file_path
    except Exception as e:
        st.error(f"Error downloading audio from YouTube: {str(e)}")
        return None


def transcribe_audio_using_deepgram(audio_file):
    try:
        # Create a Deepgram client using the API key
        config = DeepgramClientOptions(verbose=True)
        deepgram = DeepgramClient(deepgram_api_key, config)

        # Read the audio file
        with open(audio_file, "rb") as file:
            buffer_data = file.read()

        # Prepare the payload with the audio file data
        payload = {
            "buffer": buffer_data,
        }

        # Set transcription options
        options = PrerecordedOptions(
            model="nova-2",  # You can use the appropriate model for your use case
            smart_format=True,
            punctuate=True,
            diarize=False,  # Optional: for speaker separation
        )

        # Send the file for transcription and measure time
        before = datetime.now()
        response = deepgram.listen.rest.v("1").transcribe_file(
            payload, options, timeout=httpx.Timeout(300.0, connect=10.0)
        )
        after = datetime.now()

        # Output the transcription response
        print(response.to_json(indent=4))
        
        transcript = response.results.channels[0].alternatives[0].transcript
        return transcript  # Return the paragraph-style transcript 

    except Exception as e:
        print(f"Exception: {e}")
        return None
    
# AssemblyAI Fallback Transcription
def transcribe_audio_using_assemblyai(audio_file):
    headers = {
        "authorization": assemblyai_api_key
    }

    # Upload the audio file to AssemblyAI
    upload_url = "https://api.assemblyai.com/v2/upload"
    with open(audio_file, 'rb') as file:
        response = requests.post(upload_url, headers=headers, files={"file": file})
    
    if response.status_code != 200:
        raise Exception(f"Error uploading audio to AssemblyAI: {response.text}")
    
    audio_url = response.json()["upload_url"]
    
    # Request transcription of the uploaded audio file
    transcription_url = "https://api.assemblyai.com/v2/transcript"
    transcription_request = {
        "audio_url": audio_url
    }
    
    transcription_response = requests.post(transcription_url, headers=headers, json=transcription_request)
    
    if transcription_response.status_code != 200:
        raise Exception(f"Error requesting transcription: {transcription_response.text}")
    
    transcription_id = transcription_response.json()["id"]

    # Poll for the transcription to be completed
    while True:
        time.sleep(5)  # Poll every 5 seconds
        status_response = requests.get(f"https://api.assemblyai.com/v2/transcript/{transcription_id}", headers=headers)
        status_data = status_response.json()
        
        if status_data["status"] == "completed":
            return status_data["text"]
        elif status_data["status"] == "failed":
            raise Exception("Transcription failed.")
    
    return ""


# Process video summary
import os
from huggingface_hub import InferenceClient

# Assuming `download_youtube_audio`, `transcribe_audio_using_deepgram`, and `transcribe_audio_using_assemblyai` are defined

def process_video_summary(youtube_url):
    # Step 1: Download audio from YouTube
    audio_file = download_youtube_audio(youtube_url)
    if not audio_file:
        raise Exception("Failed to download audio from YouTube.")
    
    # Step 2: Transcribe the audio using Deepgram first, then AssemblyAI if needed
    transcription_text = transcribe_audio_using_deepgram(audio_file)
    if not transcription_text:
        transcription_text = transcribe_audio_using_assemblyai(audio_file)
    
    # Step 3: Check if transcription was successful
    if transcription_text:
        # Step 4: Create a detailed prompt for summarization
        prompt = f"""
        Summarize this YouTube video transcription into a step-by-step guide for users of the 'svAIsthi' application.
        The guide should help the user clearly understand the steps for using a device, 
        taking into account their current medical condition and medication routine.
        The user should end up with at least 10 steps like step-by-step guidance that helps in using the device.
        Here is the transcription of the video. Use this:
        {transcription_text}, you dont have to reiterate the task which you have been given instead just proceed with the task
        """
        print(transcription_text)  # For debugging purposes
        
        # Step 5: Prepare the payload for Hugging Face API
        payload = {"inputs": prompt}
        
        # Step 6: Use Hugging Face API to summarize the transcription
        model_name = "Qwen/QwQ-32B-Preview"  # The desired Hugging Face model
        summary = query_huggingface_api(payload, model_name, huggingface_api_key)
        
        # Step 7: Handle the response from Hugging Face API
        if summary:
            return summary
        else:
            raise Exception("Failed to generate a summary from Hugging Face API.")
    else:
        raise Exception("Failed to transcribe the video.")

# Generate button
submit = st.button('Generate', type='primary')

if submit and imaged:
    if picture is not None:
        imaged = picture
        imgg = Image.open(imaged)
    else:
        imgg = Image.open(imaged)
    with st.spinner("Generating your guide..."):
        try:
            response_text = genmodel(user_input=user_inp, img=imgg)
            st.subheader('Your Step-by-Step Guide')
            st.write(response_text)
            st.session_state.previous_summary = response_text
            
            youtube_video_url = extract_youtube_link(response_text)
            if youtube_video_url:
                st.subheader("Relevant Video Resource")
                st.video(youtube_video_url)
            else:
                device_title = extract_device_title(response_text)
                if device_title:
                    search_query = f"how to use {device_title}"
                    youtube_video_url = get_youtube_video(search_query)
                    st.session_state.youtube_video_url = youtube_video_url
                    st.subheader("Relevant Video Resource")
                    st.video(youtube_video_url)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Summarize video button
summarize = st.button('Summarize Video', type='primary')

if summarize and st.session_state.youtube_video_url:
    with st.spinner("Summarizing the video..."):
        try:
            youtube_video_link = st.session_state.youtube_video_url
            video_summary = process_video_summary(youtube_video_link)
            st.subheader(f'''{user_name}, your guide is ready''')
            st.session_state.previous_summary += "\n\n" + "Video Summary:" + "\n\n" +video_summary
            st.write(st.session_state.previous_summary)
            #st.write(video_summary)
        except Exception as e:
            st.error(f"Error summarizing the video: {str(e)}")
