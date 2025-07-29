import bluetooth
import time

# Replace with your Bluetooth module's MAC Address
bt_address = "CD:08:00:D5:79:A1"  # Update this to your HC-05/HC-06 address
port = 1  # Standard Bluetooth serial port

def scan_devices():
    """Scan for nearby Bluetooth devices and print them."""
    print("🔍 Scanning for devices...")
    devices = bluetooth.discover_devices(duration=5, lookup_names=True)

    if devices:
        print("✅ Devices found:")
        for addr, name in devices:
            print(f"   - {name} at {addr}")
    else:
        print("❌ No devices found. Make sure Bluetooth is ON & visible.")

try:
    # Scan for devices first
    scan_devices()

    # Create a Bluetooth socket
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.settimeout(10)  # Avoid infinite blocking

    print(f"🔗 Connecting to {bt_address} on port {port}...")
    sock.connect((bt_address, port))
    print("✅ Connected to Bluetooth device!")

    # Send a message (convert string to bytes)
    message = "Hello from Pydroid 3!"
    sock.send(message.encode())  # Use encode() for Python 3
    print("📤 Sent:", message)

    # Receive data (optional)
    try:
        data = sock.recv(1024)
        print("📥 Received:", data.decode())
    except bluetooth.btcommon.BluetoothError:
        print("⚠️ No response received from the device.")

    # Close connection
    sock.close()
    print("🔴 Connection closed.")

except bluetooth.btcommon.BluetoothError as e:
    print("❌ Bluetooth Error:", e)
    print("🔁 Retrying in 5 seconds...")
    time.sleep(5)
    
    # Attempt a second connection
    try:
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((bt_address, port))
        print("✅ Connected on retry!")
        sock.close()
    except Exception as e:
        print("❌ Second attempt failed:", e)

except Exception as e:
    print("❌ Other Error:", e)
