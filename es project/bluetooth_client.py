import serial
import requests

# Connect to HC-05 Bluetooth (adjust COM port accordingly)
bt = serial.Serial("COM4", 9600, timeout=1)

flask_url = "http://127.0.0.1:5000/validate"

while True:
    if bt.in_waiting > 0:
        pin = bt.readline().decode().strip()
        print(f"Received PIN: {pin}")

        response = requests.post(flask_url, json={"pin": pin})
        print(f"Server Response: {response.json()}")