import serial  # Bluetooth communication
import threading  # Background serial read
from flask import Flask, request, jsonify
import hashlib
import time
import os

app = Flask(__name__)

# Bluetooth Serial Port (Ensure this is correct)
SERIAL_PORT = "COM4"  # Change if different (Check in Device Manager)
BAUD_RATE = 9600

bt_serial = None  # Initialize Bluetooth serial connection

# ✅ Setup Bluetooth Connection
def setup_bluetooth():
    global bt_serial
    while bt_serial is None:
        try:
            bt_serial = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            print(f"✅ Connected to Bluetooth on {SERIAL_PORT}")
        except Exception as e:
            print(f"❌ Bluetooth Connection Error: {e}")
            time.sleep(3)  # Retry after 3 seconds

# Start Bluetooth setup in a background thread
threading.Thread(target=setup_bluetooth, daemon=True).start()

# ✅ Secure PIN
SECURE_PIN = os.getenv("SECURE_PIN", "1234").strip()

# ✅ Blockchain
blockchain = []

def create_block(pin, access_granted):
    previous_hash = blockchain[-1]['hash'] if blockchain else "0"

    block = {
        'index': len(blockchain) + 1,
        'timestamp': time.time(),
        'pin_hash': hashlib.sha256(pin.encode()).hexdigest(),  # Store only hashed PIN
        'access_granted': access_granted,
        'previous_hash': previous_hash
    }

    block['hash'] = hashlib.sha256(str(block).encode()).hexdigest()
    blockchain.append(block)
    return block

# ✅ Route: Validate PIN (Arduino Sends Here)
@app.route('/validate', methods=['POST'])
def validate():
    data = request.get_json()
    print("📥 Received Data:", data)  # Debugging: Check if Arduino is sending JSON

    if not data or 'pin' not in data:
        return jsonify({'error': 'PIN is required'}), 400

    pin = data['pin'].strip()  # Extract only PIN and trim spaces
    print(f"\nReceived PIN: '{pin}'")  # Debugging

    access_granted = (pin == SECURE_PIN)
    block = create_block(pin, access_granted)

    response = {
        'message': 'Access Granted' if access_granted else 'Access Denied',
        'block': block
    }
    print(f"📤 Sent Response: {response['message']}")
    return jsonify(response)

# ✅ Route: Fetch Blockchain
@app.route('/blockchain', methods=['GET'])
def get_blockchain():
    return jsonify({'blockchain': blockchain, 'length': len(blockchain)})

# ✅ Background Thread: Read from Bluetooth
def read_bluetooth():
    global bt_serial
    buffer = ""  # Buffer to store entered PIN
    while True:
        try:
            if bt_serial and bt_serial.in_waiting > 0:
                char = bt_serial.read().decode('utf-8')  # Read one character
                if char == '#':  # Stop when '#' is received
                    pin = buffer.strip().split("\n")[-1].strip()  # Extract only the latest entered PIN and trim spaces
                    print(f"\nReceived PIN: '{pin}'\n")
                    
                    if pin == SECURE_PIN:
                        print("Access Granted")
                        bt_serial.write(b'Access Granted\n')
                    else:
                        print("Access Denied")
                        bt_serial.write(b'Access Denied\n')
                    
                    create_block(pin, pin == SECURE_PIN)
                    buffer = ""  # Reset buffer after processing
                else:
                    buffer += char  # Build the PIN string
        except Exception as e:
            print(f"Bluetooth Read Error: {e}")
            time.sleep(2)  # Retry after 2 seconds

# Start Bluetooth reading thread
threading.Thread(target=read_bluetooth, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Run Flask on all IPs