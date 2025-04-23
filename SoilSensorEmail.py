import RPi.GPIO as GPIO
import smtplib
from email.message import EmailMessage
import time
from datetime import datetime
import schedule

# GPIO SETUP
channel = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)

# Set sender and recipient information
from_email_addr = "1843017840@qq.com"
from_email_pass = "dclxjjjrkmxfchfe"
to_email_addr = "2025352914@qq.com"


def check_moisture_and_send_email():
    try:
        # read sensor state
        if GPIO.input(channel):
            status = "No Water Detected! Please water your plant."
        else:
            status = "Water Detected! Water NOT needed."

        # creat email object
        msg = EmailMessage()
        msg.set_content(f"Plant Status at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:\n{status}")
        msg['From'] = from_email_addr
        msg['To'] = to_email_addr
        msg['Subject'] = 'Plant Moisture Status'

        # connect to SMTP server and send email
        server = smtplib.SMTP('smtp.qq.com', 587)
        server.starttls()
        server.login(from_email_addr, from_email_pass)
        server.send_message(msg)
        print(f"Email sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {status}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server.quit()


# set regular time to send email
schedule.every().day.at("08:00").do(check_moisture_and_send_email)
schedule.every().day.at("12:00").do(check_moisture_and_send_email)
schedule.every().day.at("16:00").do(check_moisture_and_send_email)
schedule.every().day.at("20:00").do(check_moisture_and_send_email)

# main loop
try:
    while True:
        schedule.run_pending()
        time.sleep(60)
except KeyboardInterrupt:
    GPIO.cleanup()
    print("Program terminated and GPIO cleaned up")