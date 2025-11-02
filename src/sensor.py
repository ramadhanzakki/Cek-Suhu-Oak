import random
import time
import threading
import csv
import os
import config
from datetime import datetime


class TempSensor:

    def __init__(self,id: str, sumber_data: str = 'random'):
        self.sumber_data = sumber_data
        self.jumlah_data = 0
        self._thread = None
        self.suhu = 37.1
        self.on_data_callback = None
        self.index_file = 0
        self.id = id
        self.is_active = False

        dir_utama = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.file_path = os.path.join(dir_utama, 'data', 'input', 'input.csv')
        self.data_suhu_dari_file = []

        if self.sumber_data == 'file':
            self._muat_data_dari_file()
            if not self.data_suhu_dari_file:
                print(f"PERINGATAN: Gagal memuat data file, sensor '{self.id}' akan beralih ke mode 'random'.")
                self.sumber_data = 'random'


    def baca_temperatur(self):
        self.jumlah_data += 1

        if self.sumber_data == 'random':
            self.suhu = self.buat_temperatur_acak()
        elif self.sumber_data == 'file':
            self.suhu = self.baca_suhu_dari_file()

        return {
            'waktu': datetime.now(),
            'id' : self.id,
            'suhu': self.suhu,
            'reading_number': self.jumlah_data
        }

    def buat_temperatur_acak(self):
        rand = random.random()

        if rand < 0.25:
            return round(random.uniform(config.TEMPERATURE_MIN, config.BATAS_HIPO - 0.1), 1)

        elif rand < 0.50:
            return round(random.uniform(config.BATAS_DEMAM, config.TEMPERATURE_MAX), 1)

        else:
            return round(random.uniform(config.BATAS_HIPO, config.BATAS_DEMAM - 0.1), 1)

    def _muat_data_dari_file(self):
        try:
            with open(self.file_path, 'r') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    try:
                        self.data_suhu_dari_file.append(float(row['suhu']))
                    except (ValueError, KeyError):
                        pass

            if not self.data_suhu_dari_file:
                print(f"PERINGATAN: Tidak ada data di {self.file_path}")
            else:
                print(
                    f"Berhasil memuat {len(self.data_suhu_dari_file)} data dari file.")

        except FileNotFoundError:
            print(f"ERROR: File CSV tidak ditemukan di {self.file_path}")
            self.data_suhu_dari_file = []

    def baca_suhu_dari_file(self):
        if not self.data_suhu_dari_file:
            print("Peringatan: Meminta data file, tapi buffer kosong.")
            return self.suhu
        nilai_suhu = self.data_suhu_dari_file[self.index_file]
        self.index_file += 1

        if self.index_file >= len(self.data_suhu_dari_file):
            self.index_file = 0

        return nilai_suhu
    

    def looping(self):
        print('\n======Monitoring Started======')

        while self.is_active:
            data = self.baca_temperatur()

            if self.on_data_callback:
                try:
                    self.on_data_callback(data)
                except Exception as e:
                    print(f"Error saat menjalankan callback: {e}")

            start_sleep = time.time()
            while time.time() - start_sleep < config.JEDA:
                if not self.is_active:
                    break
                time.sleep(0.1)

        print('\n======Monitoring Stopped======')

    def mulai_monitoring(self, callback_function):
        if self.is_active:
            print('Sensor already active')
            return

        self.on_data_callback = callback_function
        self.is_active = True
        self._thread = threading.Thread(target=self.looping, daemon=True)
        self._thread.start()

    def stop_monitoring(self):
        self.is_active = False
        if self._thread:
            self._thread.join(timeout=1.0)
