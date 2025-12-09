# BEFORE STARTING:
# We need to open the virtual environment, so run the following in the Terminal:
# source dht-env/bin/activate

# Imports and setups
import os
import smtplib
import ssl
from email.message import EmailMessage

# Connect to the .gmail server and encrypts the connection
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587  # TLS

# Reads the email name and password from the .bash environment
SENDER_EMAIL = os.environ["$ALERT_EMAIL"]
SENDER_PASSWORD = os.environ["$ALERT_EMAIL_PASSWORD"]

# To send the email alert
def send_alert_email(to_address: str, subject: str, body: str):
    # Create the email
    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.set_content(body)

    # Connect and send
    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

# Example: send to your normal email (phone will ping with notification)
send_alert_email(
    to_address="fr422@ic.ac.uk",
    subject="Raspberry Pi Alert!",
    body="Email Test 1."
)