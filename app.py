import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

# Configuring the page
st.title('svAIsthi - Svasth with AI')
st.caption('Your AI assistant for health education and help')

# Image uploader
imaged = st.file_uploader("Choose the image", type=["jpg", "png", "jpeg", "webp"])
if imaged:
    st.image(imaged, caption="Image Uploaded", use_column_width=True)
    imgg = Image.open(imaged)


# User information
st.header('User Information')
user_name = st.text_input('Please input your name')
user_age = st.number_input('Please enter your age', min_value=0)
previous_conditions = st.text_input('Please enter your previous conditions')
current_condition = st.text_input('Please enter your current medical conditions')
previous_medication = st.text_input('Please enter your previous medication')
current_medication = st.text_input('Please enter your current medication')
medication_routine = st.text_input('Please enter your medication routine')

# User input
user_inp = f"""provide a disclaimer that this is not a medical advice but just a 
            handy tool. According to these factors {user_age}, 
            {previous_conditions}, {current_condition}, {previous_medication}, 
            {current_medication}, {medication_routine}, can you please look at the uploaded image and help the user
            to properly use the device with a step-by-step detailed guide along with any relevant internet resources?
            Start the guide with the name of the device and the purpose of the device, then proceed with the step-by-step guide,
            and finally provide the user with the relevant internet resources for further information. In the end, wish the user
            good luck and a speedy recovery."""

# Load the environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def genmodel(user_input, img):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content([user_input, img])
    return response.text

submit = st.button('Generate', type='primary')

if submit and imaged:
    with st.spinner("Generating your guide..."):
        try:
            response = genmodel(user_input=user_inp, img=imgg)
            st.subheader('Your Step-by-Step Guide', divider=True)
            st.write(response)
        except Exception as e:
            st.write("An error occurred:", str(e))

