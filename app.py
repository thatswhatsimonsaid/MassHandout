import os
import smtplib
from email.message import EmailMessage
import streamlit as st
from src.main import generate_booklet_from_web

st.title("📖 VEYM Mass Booklet Generator")

user_email = st.text_input("Your Email Address")
target_date = st.text_input("Mass Date (MMDDYY)", value="093026")
org_name = st.text_input("Organization / Chapter", value="VEYM Chapter")

def send_email_with_attachment(recipient_email: str, file_path: str):
    # Retrieve credentials from Streamlit secrets (or environment variables)
    smtp_server = st.secrets.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(st.secrets.get("SMTP_PORT", 465))
    sender_email = st.secrets.get("EMAIL_USER", "simon.nguyen1@veym.net")
    sender_password = st.secrets.get("EMAIL_PASSWORD", "")

    msg = EmailMessage()
    msg["Subject"] = "Your Requested Mass Booklet"
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg.set_content("Hello!\n\nAttached is your generated VEYM Mass Booklet. Please review and proofread before printing.\n\nLeave the Mass, live the Mass!")

    # Attach the .docx file
    with open(file_path, "rb") as f:
        file_data = f.read()
        file_name = os.path.basename(file_path)
    
    msg.add_attachment(file_data, maintype="application", subtype="vnd.openxmlformats-officedocument.wordprocessingml.document", filename=file_name)

    # Send securely via SSL
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

if st.button("Generate & Email Booklet"):
    if user_email:
        with st.spinner("Generating your booklet and dispatching email..."):
            try:
                # 1. Run core generation logic returning the .docx path
                output_path = generate_booklet_from_web(target_date, org_name)

                # 2. Send via SMTP from simon.nguyen1@veym.net
                send_email_with_attachment(user_email, output_path)

                st.success(f"Success! Your booklet has been emailed to {user_email}.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
    # Fix: Corrected indentation alignment to match `if st.button` block
        st.error("Please provide a valid email address.")