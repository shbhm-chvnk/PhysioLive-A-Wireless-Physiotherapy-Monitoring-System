import socket
import csv
from datetime import datetime

# ======== CONFIG ========
CSV_FILE = '../data/live_data.csv'
ESP32_IP = '192.168.4.1'
PORT = 8888
ACC_SENSITIVITY = 16384  # LSB/g for ±2g
GRAVITY = 9.81  # m/s²
GYRO_SENSITIVITY = 65.5 # LSB/°/s
# ========================

# Reference (initial) readings
ref_acc_ms2 = None
ref_gyro_dps = None

print(f"[INFO] Connecting to {ESP32_IP}:{PORT}...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ESP32_IP, PORT))

def parse_packet(packet):
    """Parse a sensor data packet into a dictionary."""
    try:
        return {k: v for k, v in (p.split('=', 1) for p in packet.split('|') if '=' in p)}
    except ValueError:
        print(f"[WARN] Malformed packet skipped: {packet}")
        return None

# ===== Get first packet instantly for reference =====
print("[INFO] Waiting for first packet as reference...")
while True:
    raw_data = s.recv(1024).decode(errors='ignore').strip()
    parts = parse_packet(raw_data)
    if parts and all(k in parts for k in ('aX', 'aY', 'aZ', 'gX', 'gY', 'gZ')):
        # Convert and store as reference
        ref_acc_ms2 = {
            'x': float(parts['aX']) / ACC_SENSITIVITY * GRAVITY,
            'y': float(parts['aY']) / ACC_SENSITIVITY * GRAVITY,
            'z': float(parts['aZ']) / ACC_SENSITIVITY * GRAVITY
        }
        ref_gyro_dps = {
            'x': float(parts['gX']) / GYRO_SENSITIVITY,
            'y': float(parts['gY']) / GYRO_SENSITIVITY,
            'z': float(parts['gZ']) / GYRO_SENSITIVITY
        }
        print("[REF] Reference values set:", ref_acc_ms2, ref_gyro_dps)
        break

# ===== CSV Setup =====
with open(CSV_FILE, 'w', newline='') as f:
    csv.writer(f).writerow(['timestamp', 'd_aX', 'd_aY', 'd_aZ', 'd_gX', 'd_gY', 'd_gZ'])

print("[INFO] Streaming real-time differences...")
buffer = ""
with open(CSV_FILE, 'a', newline='') as f:
    writer = csv.writer(f)
    try:
        while True:
            buffer += s.recv(1024).decode(errors='ignore')
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                line = line.strip()
                if not line:
                    continue

                parts = parse_packet(line)
                if not parts:
                    continue

                try:
                    # Current readings
                    aX = int(parts['aX']) / ACC_SENSITIVITY * GRAVITY
                    aY = int(parts['aY']) / ACC_SENSITIVITY * GRAVITY
                    aZ = int(parts['aZ']) / ACC_SENSITIVITY * GRAVITY
                    gX = float(parts['gX']) / GYRO_SENSITIVITY
                    gY = float(parts['gY']) / GYRO_SENSITIVITY
                    gZ = float(parts['gZ']) / GYRO_SENSITIVITY

                    # Differences from reference
                    daX = aX - ref_acc_ms2['x']
                    daY = aY - ref_acc_ms2['y']
                    daZ = aZ - ref_acc_ms2['z']
                    dgX = gX - ref_gyro_dps['x']
                    dgY = gY - ref_gyro_dps['y']
                    dgZ = gZ - ref_gyro_dps['z']

                    # Print live
                    print(f"dA=({daX:.2f}, {daY:.2f}, {daZ:.2f}) m/s² | "
                          f"dG=({dgX:.2f}, {dgY:.2f}, {dgZ:.2f}) °/s")

                    # Save to CSV
                    writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                     round(daX, 2), round(daY, 2), round(daZ, 2),
                                     round(dgX, 2), round(dgY, 2), round(dgZ, 2)])
                    f.flush()
                except (ValueError, KeyError) as e:
                    print(f"[WARN] Data conversion error: {e}")
                    continue
    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user.")
    finally:
        s.close()
