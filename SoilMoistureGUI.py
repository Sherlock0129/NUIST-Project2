import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import time
import threading
import smtplib
from email.message import EmailMessage
import RPi.GPIO as GPIO
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import smtplib

# GPIO SETUP
channel = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)

# Email settings for QQ Mail
from_email_addr = "1843017840@qq.com"  
from_email_pass = "dclxjjjrkmxfchfe"  
to_email_addr = "2025352914@qq.com"    

def read_sensor():
    if GPIO.input(channel):
        return "No water detected. Please water."
    else:
        return "Water has been detected."


def send_email(status):
    server = None
    try:
        print("Attempting to connect to QQ SMTP server...")
        # Use SSL on port 465 for QQ Mail
        server = smtplib.SMTP_SSL('smtp.qq.com', 465, timeout=10)
        print("Connected to SMTP server")

        # Login to the server
        server.login(from_email_addr, from_email_pass)
        print("Logged in successfully")

        # Create a multipart email
        msg = MIMEMultipart('alternative')
        msg['From'] = from_email_addr
        msg['To'] = to_email_addr
        msg['Subject'] = 'Plant Moisture Status Update'

        # Plain-text content (fallback)
        text_content = f"""
====================================
      Plant Moisture Status Update
====================================

Dear Plant Caretaker,

Your plant was checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Status: {status}

{'*** Please water your plant soon to keep it healthy! ***' if 'No water detected' in status else 'Your plant is well-hydrated. No action needed.'}

------------------------------------
Sent by your Raspberry Pi Plant Moisture Sensor
====================================
"""
        # HTML content with color-coded design
        # Red/orange for dry, green for moist
        header_color = '#ff4d4d' if 'No water detected' in status else '#4CAF50'
        action_color = '#ff4d4d' if 'No water detected' in status else '#388E3C'
        action_message = '*** Please water your plant soon to keep it healthy! ***' if 'No water detected' in status else 'Your plant is well-hydrated. No action needed.'

        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .header {{
                    background-color: {header_color};
                    color: white;
                    padding: 15px;
                    text-align: center;
                    font-size: 20px;
                    font-weight: bold;
                }}
                .content {{
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .status {{
                    font-size: 18px;
                    font-weight: bold;
                    color: {action_color};
                    margin: 10px 0;
                }}
                .action {{
                    font-style: italic;
                    color: {action_color};
                    margin-top: 10px;
                }}
                .footer {{
                    background-color: #f1f1f1;
                    padding: 10px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                }}
                .timestamp {{
                    font-size: 14px;
                    color: #555;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    Plant Moisture Status Update
                </div>
                <div class="content">
                    <p>Dear Plant Caretaker,</p>
                    <p class="timestamp">Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p class="status">Status: {status}</p>
                    <p class="action">{action_message}</p>
                </div>
                <div class="footer">
                    Sent by your Raspberry Pi Plant Moisture Sensor
                </div>
            </div>
        </body>
        </html>
        """

        # Attach plain-text and HTML parts
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)

        # Send the email
        server.send_message(msg)
        print(f"Email sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {status}")
    except Exception as e:
        print(f"Error sending email: {e}")
        messagebox.showerror("Email Error", f"Failed to send email: {e}")
    finally:
        if server is not None:
            try:
                server.quit()
                print("SMTP server connection closed")
            except:
                print("Error closing SMTP server connection")

def update_result(status):
    result_label.config(text=f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\nStatus: {status}")

def immediate_check():
    status = read_sensor()
    update_result(status)
    send_email(status)
    messagebox.showinfo("Detection result", status)

def validate_time(time_str):
    # Check if time matches HH:MM format and is valid
    pattern = r'^([01]\d|2[0-3]):([0-5]\d)$'
    return bool(re.match(pattern, time_str))

def set_schedule():
    def save_times():
        new_times = []
        for i, entry in enumerate(time_entries):
            time_str = entry.get()
            if not validate_time(time_str):
                messagebox.showerror("Invalid Input", f"Time {i+1} must be in HH:MM format (e.g., 08:00).")
                return
            new_times.append(time_str)
        for i, time_str in enumerate(new_times):
            scheduled_times[i] = time_str
        stop_scheduling()
        start_scheduling()
        messagebox.showinfo("Set up successfully", "The timing detection time has been updated.")
        update_schedule_display()
        window.destroy()

    window = tk.Toplevel(root)
    window.title("Set the timing detection time")
    time_entries = []
    for i in range(4):
        tk.Label(window, text=f"Time {i+1} (HH:MM):").grid(row=i, column=0, padx=5, pady=5)
        entry = tk.Entry(window)
        entry.insert(0, scheduled_times[i])
        entry.grid(row=i, column=1, padx=5, pady=5)
        time_entries.append(entry)
    tk.Button(window, text="Save", command=save_times).grid(row=4, column=0, columnspan=2, pady=10)

def check_and_update():
    status = read_sensor()
    update_result(status)
    send_email(status)


def update_schedule_display():
    for i, label in enumerate(schedule_labels):
        label.config(text=f"{i+1}. {scheduled_times[i]}")

# Scheduling logic using threading.Timer
timers = []
def schedule_task(time_str):
    def run_task():
        check_and_update()
        # Schedule the next run for this time tomorrow
        schedule_task(time_str)

    # Calculate seconds until the next occurrence of time_str
    now = datetime.now()
    hour, minute = map(int, time_str.split(':'))
    next_run = datetime(now.year, now.month, now.day, hour, minute)
    if next_run <= now:
        next_run += timedelta(days=1)
    seconds_until = (next_run - now).total_seconds()

    # Start a timer for this task
    timer = threading.Timer(seconds_until, run_task)
    timer.daemon = True
    timer.start()
    timers.append(timer)

def start_scheduling():
    for time_str in scheduled_times:
        schedule_task(time_str)

def stop_scheduling():
    for timer in timers:
        timer.cancel()
    timers.clear()

# GUI init
root = tk.Tk()
root.title("Soil Moisture Detection System")
root.geometry("300x400")

# Global variable
scheduled_times = ["08:00", "12:00", "16:00", "20:00"]

# Buttons
tk.Button(root, text="Immediate Detection", command=immediate_check).pack(pady=10)
tk.Button(root, text="Set Up Timed Detection", command=set_schedule).pack(pady=10)

# Detection result display
tk.Label(root, text="Recent Test Results:").pack(pady=5)
result_label = tk.Label(root, text="Time: Not detected\nStatus: Not detected")
result_label.pack(pady=5)

# Scheduled detection time display
tk.Label(root, text="Regularly Check the Time:").pack(pady=10)
schedule_labels = []
for i in range(4):
    label = tk.Label(root, text=f"{i+1}. {scheduled_times[i]}")
    label.pack()
    schedule_labels.append(label)

# Initialize scheduled tasks
start_scheduling()

# Clean GPIO
def on_closing():
    stop_scheduling()
    GPIO.cleanup()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
