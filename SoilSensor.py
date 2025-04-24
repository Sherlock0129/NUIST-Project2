import RPi.GPIO as GPIO
import time

# GPIO SETUP
channel = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)

def callback(channel):
    if GPIO.input(channel):
        print("No Water Detected! Please water your plant.")
    else:
        print("Water Detected! Water NOT needed.")

# Detect changes in the state of GPIO pins.
GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(channel, callback)

# Infinite loop to keep the program running.
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
