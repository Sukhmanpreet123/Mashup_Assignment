import streamlit as st
import subprocess
import zipfile
import os
import smtplib
from email.message import EmailMessage
import re
from dotenv import load_dotenv # Import the new library

# Load the hidden variables from the .env file
load_dotenv() 

# Securely fetch the credentials
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
PROGRAM_1_SCRIPT = "102313003.py" # Ensure this matches your Program 1 filename

def validate_email(email):
    """Checks if the email format is correct"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

# --- WEB APP UI ---
st.title("Audio Mashup Web Service")
st.write("Generate a custom YouTube audio mashup and have it emailed to you!")

# User must provide singer name, number of videos, duration of each video and email id. [cite: 38]
with st.form("mashup_form"):
    singer_name = st.text_input("Singer Name", "Sharry Mann")
    num_videos = st.number_input("# of videos", min_value=11, value=20, step=1)
    duration = st.number_input("Duration of each video (sec)", min_value=21, value=30, step=1)
    email_id = st.text_input("Email Id", "psrana@gmail.com")
    
    submit_button = st.form_submit_button("Submit")

# --- PROCESSING LOGIC ---
if submit_button:
    # Email id must be correct [cite: 40]
    if not validate_email(email_id):
        st.error("Please enter a valid email address.")
    else:
        with st.spinner("Downloading and processing audio... This might take a few minutes!"):
            output_audio = "mashup_output.mp3"
            zip_filename = "mashup_result.zip"
            
            try:
                # 1. Run the command line program you built in Program 1
                result = subprocess.run(
                    ["python", PROGRAM_1_SCRIPT, singer_name, str(num_videos), str(duration), output_audio],
                    capture_output=True, text=True
                )
                
                if result.returncode != 0:
                    st.error(f"Error running the script: {result.stderr}")
                else:
                    # 2. User should get the result file in zip format 
                    with zipfile.ZipFile(zip_filename, 'w') as zipf:
                        zipf.write(output_audio)
                    
                    # 3. Send through email 
                    st.info("Zipping complete. Sending email...")
                    
                    msg = EmailMessage()
                    msg['Subject'] = 'Your Audio Mashup is Ready!'
                    msg['From'] = SENDER_EMAIL
                    msg['To'] = email_id
                    msg.set_content(f"Here is the mashup of {num_videos} videos of {singer_name}.")
                    
                    with open(zip_filename, 'rb') as f:
                        file_data = f.read()
                        msg.add_attachment(file_data, maintype='application', subtype='zip', filename=zip_filename)
                        
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                        server.login(SENDER_EMAIL, SENDER_PASSWORD)
                        server.send_message(msg)
                        
                    st.success(f"Success! The mashup zip file has been sent to {email_id}.")
                    
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                
            finally:
                # Clean up the generated files from the server/local folder
                if os.path.exists(output_audio):
                    os.remove(output_audio)
                if os.path.exists(zip_filename):
                    os.remove(zip_filename)