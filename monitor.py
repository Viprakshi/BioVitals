import serial
import time
import csv
from datetime import datetime

PORT = "COM4" 
BAUD_RATE = 9600
CSV_FILE = "patient_data.csv"

def save_to_csv(name, spo2, temp, pulse):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = False
    try:
        with open(CSV_FILE, 'r'):
            file_exists = True
    except FileNotFoundError:
        pass

    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Name", "SpO2", "Temperature", "Pulse", "DateTime"])
        writer.writerow([name, spo2, temp, pulse, timestamp])
    print(f"[✓] Data saved for {name} at {timestamp}.")

def main():
    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=2)
        time.sleep(2)
        print(f"Connected to {PORT}")

        name = input("Enter patient name: ")
        waiting_for_prompt = True
        data_buffer = []
        spo2 = temp = pulse = None

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                print(line)
                data_buffer.append(line)

                if waiting_for_prompt and "Enter Patient Name:" in line:
                    ser.write((name + "\n").encode('utf-8'))
                    waiting_for_prompt = False

                if line.startswith("SpO2:"):
                    spo2 = float(line.split()[1])
                elif line.startswith("Body Temperature:"):
                    temp = float(line.split()[2])
                elif line.startswith("Pulse Rate:"):
                    pulse = int(line.split()[2])

                if "Measurement complete" in line and spo2 and temp and pulse:
                    save_to_csv(name, spo2, temp, pulse)
                    break

    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals():
            ser.close()

if __name__ == "__main__":
    main()
