import csv
import os
import threading
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# Mutex Lock untuk sekat Race Condition (Ciri Utama OS)
csv_lock = threading.Lock()
CSV_FILE = "runners.csv"

@app.route('/checkin', methods=['POST'])
def checkin():
    data = request.get_json()
    if not data or 'uid' not in data:
        return jsonify({"status": "Error", "message": "Payload tidak sah!"}), 400
    
    uid = data['uid'].strip().upper()
    updated = False
    runner_name = ""
    
    # Guna Mutex Lock (Synchronization)
    with csv_lock:
        all_rows = []
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    all_rows.append(row)
        
        # Cari baris data pelari (Baris yang bermula dengan UID sebenar)
        # Kita skip baris tajuk, baris kosong, dan baris header
        for row in all_rows:
            if len(row) > 0 and row[0].strip().upper() == uid:
                runner_name = row[1]
                if row[2] == "Selesai Check-In":
                    return jsonify({"status": "Warning", "message": f"{runner_name} sudah pun check-in!"}), 200
                
                # Kemas kini Status dan Masa Semasa (OS System Time)
                row[2] = "Selesai Check-In"
                row[3] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                updated = True
                break
        
        if updated:
            # Tulis semula keseluruhan fail CSV termasuk tajuk asal (Persistent Storage I/O)
            with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(all_rows)
            
            print(f"\n[OS STORAGE] SUCCESS: {runner_name} ({uid}) disimpan pada {datetime.now().strftime('%H:%M:%S')}!")
            return jsonify({"status": "Success", "message": f"{runner_name} berjaya didaftarkan!"}), 200
        else:
            print(f"\n[OS ERROR] UNKNOWN: Tag UID {uid} tidak wujud dalam fail CSV!")
            return jsonify({"status": "Error", "message": "Kad RFID tidak dikenali dalam sistem!"}), 404

if __name__ == '__main__':
    print("\n==================================================================")
    print("[OS SERVER] Mengaktifkan Smart Registration Server (CSV Storage)...")
    print("==================================================================")
    app.run(host='0.0.0.0', port=5000, debug=True)
