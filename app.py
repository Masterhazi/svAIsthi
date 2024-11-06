import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import re
from googleapiclient.discovery import build
import requests
import streamlit.components.v1 as components

# Load environment variables
load_dotenv()
youtube_api_key = os.getenv("YOUTUBE_API_KEY")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Configuring the page
st.set_page_config(page_title="💊 svAIsthi", page_icon="https://raw.githubusercontent.com/Masterhazi/svAIsthi/refs/heads/main/health-8.ico")
st.title('svAIsthi - Svasth with AI')
st.caption('Your AI assistant for health education and help')

# Inject OneSignal JavaScript SDK and initialize with your App ID
onesignal_script = """
<script src="https://cdn.onesignal.com/sdks/OneSignalSDK.js" async=""></script>
<script>
    window.OneSignal = window.OneSignal || [];
    OneSignal.push(function() {
        OneSignal.init({
            appId: "1e596efe-b658-4e16-91c4-bf1052d49eba",  // Replace with your actual OneSignal App ID
            notifyButton: {
                enable: true,
            },
            serviceWorkerPath: '/OneSignalSDKWorker.js'
        });

        OneSignal.on('subscriptionChange', function(isSubscribed) {
            if (isSubscribed) {
                OneSignal.getUserId(function(userId) {
                    console.log("OneSignal User ID:", userId);
                    // Here, you can also save the userId to your backend if needed
                });
            }
        });
    });
</script>
"""
onesignal_script += """
<button onclick="OneSignal.showSlidedownPrompt();">Subscribe to Notifications</button>
"""

components.html(onesignal_script, height=0)

# Image uploader
imaged = st.file_uploader("Choose the image", type=["jpg", "png", "jpeg", "webp"])
if imaged:
    st.image(imaged, caption="Image Uploaded", use_column_width=True)
    imgg = Image.open(imaged)

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
user_inp = f"""provide a disclaimer that this is not a medical advice but just a handy tool. According to these factors...
"""

# Function for generating AI response
def genmodel(user_input, img):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content([user_input, img])
    return response.text

# Function for extracting YouTube links
def extract_youtube_link(text):
    match = re.search(r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+', text)
    return match.group(0) if match else None

# Function for device title extraction
def extract_device_title(response_text):
    match = re.search(r'Title:\s*(.+?)[\.\n]', response_text)
    return match.group(1).strip().rstrip('.') if match else None

# Function to get YouTube video link
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
    return f"https://www.youtube.com/watch?v={video_id}"

# Function to send notification through OneSignal REST API
def send_onesignal_notification(title, message):
    headers = {
        "Authorization": f"Basic {os.getenv('ONESIGNAL_REST_API_KEY')}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {
        "app_id": "1e596efe-b658-4e16-91c4-bf1052d49eba",  # Replace with your OneSignal App ID
        "headings": {"en": title},
        "contents": {"en": message},
        "included_segments": ["Subscribed Users"]
    }
    response = requests.post("https://onesignal.com/api/v1/notifications", headers=headers, json=payload)
    return response.status_code, response.json()

# Button to trigger test notification
if st.button("Send Notification"):
    status_code, response = send_onesignal_notification("Test Notification", "This is a test notification from svAIsthi.")
    if status_code == 200:
        st.success("Notification sent successfully!")
    else:
        st.error("Failed to send notification.")

# Generate guide button
submit = st.button('Generate', type='primary')

if submit and imaged:
    with st.spinner("Generating your guide..."):
        try:
            response_text = genmodel(user_input=user_inp, img=imgg)
            st.subheader('Your Step-by-Step Guide')
            st.write(response_text)
            
            youtube_video_url = extract_youtube_link(response_text)
            
            if youtube_video_url:
                st.subheader("Relevant Video Resource")
                st.video(youtube_video_url)
            else:
                device_title = extract_device_title(response_text)
                if device_title:
                    search_query = f"how to use {device_title}"
                    youtube_video_url = get_youtube_video(search_query)
                    st.subheader("Relevant Video Resource")
                    st.video(youtube_video_url)
                else:
                    st.write("Device title not found in the response.")
        except Exception as e:
            st.write("An error occurred:", str(e))
