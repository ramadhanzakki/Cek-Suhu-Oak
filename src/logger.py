# src/logger.py

import csv
from datetime import datetime
from pathlib import Path
import config # Menggunakan config utama kita

class Logger: # MODIFIKASI: Nama kelas diubah ke Logger
    def __init__(self, logLocation=config.OUTPUT_FILE): # MODIFIKASI: Baca dari config
        self.location = logLocation
        self.fileHandle = None
        self.writer = None
        self.ready = False
        print(f"Logger (Sinkron) diinisialisasi. Lokasi log: {self.location}")

    def setup(self, fileMode='w') -> bool:
        try:
            Path(self.location).parent.mkdir(parents=True, exist_ok=True)
            
            # MODIFIKASI: Tambahkan encoding='utf-8'
            self.fileHandle = open(self.location, fileMode, newline='', encoding='utf-8')
            self.writer = csv.writer(self.fileHandle)

            if fileMode == 'w':
                self.writer.writerow([
                    'waktu',
                    'id',
                    'suhu',
                    'status'
                ])
            self.fileHandle.flush()
            self.ready = True
            print('SETUP Logger BERHASIL')
            return True
        except Exception as e:
            print(f"SETUP Logger GAGAL: {e}")
            return False

    def writeData(self, id_sensor, suhu, status):
        if not self.ready:
            print("GAGAL SIMPAN DATA: Logger tidak siap.")
            return False
            
        try:
            waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.writer.writerow([
                waktu,
                id_sensor,
                suhu,
                status
            ])
            self.fileHandle.flush()
            # Hapus "print("BERHASIL SIMPAN DATA")" agar tidak spam konsol
            return True
        except Exception as e:
            print(f"GAGAL SIMPAN DATA: {e}")
            return False

    # Fungsi penting untuk menutup file
    def close(self):
        if self.fileHandle:
            print("\nMenutup file log...")
            self.fileHandle.close()
            self.ready = False