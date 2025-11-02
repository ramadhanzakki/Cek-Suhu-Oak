import random
import time
import threading
import config
from datetime import datetime


class TempSensor:

    def __init__(self, sumber_data: str = 'random'):
        self.sumber_data = sumber_data
        self.jumlah_data = 0
        self._thread = None
        self.suhu = 37.1
        self.is_active = False

    def baca_temperatur(self):
        self.jumlah_data += 1

        if self.sumber_data == 'random':
            self.suhu = self.buat_temperatur_acak()
        elif self.sumber_data == 'file':
            self.suhu = self.baca_dari_file()

        return {
            'timestamp': datetime.now(),
            'temperature': self.suhu,
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


    def baca_dari_file(self):
        return self.suhu
    

    def looping(self):
        print('\n======Monitoring Started======')

        while self.is_active:
            data = self.baca_temperatur()

            time.sleep(config.JEDA)

        print('\n======Monitoring Stopped======')

    
    def mulai_monitoring(self):
        if self.is_active:
            print('Sensor already active')
            return
        
        self.is_active = True

        self._thread = threading.Thread(target=self.looping, daemon=True) 
        self._thread.start()

    
    def stop_monitoring(self):
        self.is_active = False
        if self._thread:
            self._thread.join(timeout=1.0)