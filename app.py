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
# User input
user_inp = f"""provide a disclaimer that this is not a medical advice but just a 
            handy tool. According to these factors the user is {user_age} years old, 
            the user had {previous_conditions} previously and now suffering from {current_condition}
            the user used {previous_medication} for {previous_conditions}, now using
            {current_medication} for {current_condition} for {medication_routine}, can you please look at the uploaded image and help the user
            to properly use the device with a step-by-step detailed guide along with any relevant internet resources?
            make sure the prompt is generated according to the user's age.
            Start the guide with the greeting Hi {user_name} then "Title:" name of the device and in the 
            next paragraph provide an overview of the Purpose of the device, 
            highlighting how it may support the user’s specific current condition and needs related to age, then proceed with the step-by-step guide with relevant side headings,
            in the next section Explain the importance of following the current medication routine consistently to achieve the best therapeutic outcome.
            in the next section Check for potential interactions between current medications and previous medications. 
            also explain the basic effects of the medication other than the intended effect
            If relevant, provide specific instructions 
            on time intervals for using the device safely in relation to their medication schedule.
            and finally provide the user with the relevant internet resources for further information. 
            In the end, wish the user good luck and a speedy recovery."""

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
