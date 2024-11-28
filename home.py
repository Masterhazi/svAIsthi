
import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import re
from googleapiclient.discovery import build
import requests
import streamlit.components.v1 as components
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Ensure the user is authenticated
if not st.session_state.get("logged_in", False):
    st.warning("Please log in first.")
    st.session_state["current_page"] = "Login"
    st.experimental_rerun()

# Load environment variables
load_dotenv()
youtube_api_key = os.getenv("YOUTUBE_API_KEY")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Configuring the page
st.set_page_config(
    page_title="💊 svAIsthi",
    page_icon="https://github.com/Masterhazi/svAIsthi/blob/main/health-8.ico",
)


# Configuring the page content
st.title('svAIsthi - Svasth with AI')
st.caption('Your AI assistant for health education and help')

# Image uploader
imaged = st.file_uploader("Choose the image", type=["jpg", "png", "jpeg", "webp"])
if imaged:
    st.image(imaged, caption="Image Uploaded", use_column_width=True)
    
enable = st.checkbox('Enable camera')
picture = st.camera_input('Take a picture', disabled = not enable)

if picture is not None:
    imaged = picture
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
user_inp = f"""provide a disclaimer that this is not a medical advice but just a handy tool. According to these factors the user is {user_age} years old, the user had {previous_conditions} previously and now suffering from {current_condition} the user used {previous_medication} for {previous_conditions}, now using {current_medication} for {current_condition} for {medication_routine}, can you please look at the uploaded image and help the user to properly use the device with a step-by-step detailed guide along with any relevant internet resources? make sure the prompt is generated according to the user's age. Start the guide with the greeting Hi {user_name} then "Title:" name of the device and in the next paragraph provide an overview of the Purpose of the device, highlighting how it may support the user’s specific current condition and needs related to age, then proceed with the step-by-step guide with relevant side headings, in the next section Explain the importance of following the current medication routine consistently to achieve the best therapeutic outcome. in the next section Check for potential interactions between current medications and previous medications. also explain the basic effects of the medication other than the intended effect If relevant, provide specific instructions on time intervals for using the device safely in relation to their medication schedule. and finally provide the user with the relevant internet resources for further information. In the end, wish the user good luck and a speedy recovery."""

def genmodel(user_input, img):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content([user_input, img])
    return response.text

def extract_youtube_link(text):
    # Regular expression to find the YouTube link
    match = re.search(r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+', text)
    return match.group(0) if match else None

def extract_device_title(response_text):
    # Regular expression to find the device title after 'Title:' and remove trailing period or newline
    match = re.search(r'Title:\s*(.+?)[\.\n]', response_text)
    if match:
        title = match.group(1).strip()  # Extract and strip any trailing spaces
        return title.rstrip('.')  # Remove any trailing period
    return None

def get_youtube_video(query):
    youtube = build("youtube", "v3", developerKey=youtube_api_key)
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=1
    )
    response = request.execute()
    
    # Extract video ID from the first search result
    video_id = response["items"][0]["id"]["videoId"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    return video_url

# Function to send notification through OneSignal REST API
def send_onesignal_notification(title, message):
    if not os.getenv("ONESIGNAL_REST_API_KEY") or not os.getenv("ONESIGNAL_APP_ID"):
        st.error("OneSignal REST API Key or App ID not set in the .env file.")
        return None, None

    headers = {
        "Authorization": f"Basic {os.getenv('ONESIGNAL_REST_API_KEY')}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {
        "app_id": os.getenv("ONESIGNAL_APP_ID"),  # Use the environment variable
        "headings": {"en": title},
        "contents": {"en": message},
        "included_segments": ["Subscribed Users"]
    }
    response = requests.post(
        "https://onesignal.com/api/v1/notifications",
        headers=headers,
        json=payload
    )
    return response.status_code, response.json()

# Button to trigger test notification
if st.button("Send Notification"):
    status_code, response = send_onesignal_notification(
        "Test Notification", 
        "This is a test notification from svAIsthi."
    )
    if status_code == 200:
        st.success("Notification sent successfully!")
    else:
        st.error(f"Failed to send notification. Response: {response}")

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

# Log out button
if st.button("Log Out"):
    st.session_state["authenticated"] = False
    st.session_state["current_page"] = "Home"
    st.experimental_rerun()
