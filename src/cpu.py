import threading
import time
import os
import config
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from .bus import DataBus
    from .logger import Logger


class CPU:
    def __init__(self):
        print('Inisialisasi CPU')
        self.bus : 'DataBus' | None = None
        self.is_running = False
        self._thread = None

        dir_utama = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def attach_bus(self, bus: 'DataBus'):
        print('CPU terhububg ke Data Bus')
        self.bus = bus

    def attach_logger(self, logger:'Logger'):
        print('CPU terhubung ke logger.')
        self.logger = logger    

    def handle_interrupt(self, alert_data: Dict[str, Any]):
        print("\n" + "="*40)
        print(f"!!! INTERRUPT DITERIMA (CPU) !!!")
        print(f"    ALERT: Demam terdeteksi!")
        print(f"    SENSOR: {alert_data['id']}")
        print(f"    SUHU:   {alert_data['suhu']}°C")
        print("="*40 + "\n")

    # Di dalam file src/cpu.py

    def _processing_loop(self):
        """
        Mensimulasikan siklus proses (clock cycle) CPU.
        MODIFIKASI: CPU sekarang juga menentukan status log.
        """
        print("CPU 'processing loop' (Logging Sinkron) dimulai...")
        while self.is_running:
            if not self.bus or not self.logger:
                print("CPU: Menunggu bus dan logger ditancapkan...")
                time.sleep(1)
                continue
                
            # 1. CPU 'polling' data dari buffer bus
            data = self.bus.get_buffered_data()
            
            if data:
                # --- LOGIKA PINDAH KE SINI ---
                try:
                    suhu = data['suhu']
                    id_sensor = data['id']
                    
                    # 2. CPU menentukan status
                    if suhu > config.BATAS_DEMAM:
                        status = "ALERT"
                    elif suhu < config.BATAS_HIPO:
                        status = "HIPOTERMIA"
                    else:
                        status = "NORMAL"

                    # 3. CPU memanggil logger sinkron
                    #    (Ini akan menulis 'HIPOTERMIA' ke file CSV)
                    self.logger.writeData(id_sensor, suhu, status)
                    
                    # 4. Cetak ke konsol (MODIFIKASI)
                    if status == "NORMAL":
                        print(f"[CPU->Log]: Data normal dari {id_sensor}: {suhu}°C")
                    
                    elif status == "HIPOTERMIA":
                        # --- INI BLOK BARU ANDA ---
                        # Cetak blok peringatan agar "rame"
                        print("\n" + "="*40)
                        print(f"!!! PERINGATAN (CPU-LOG) !!!") # Kita sebut CPU-LOG
                        print(f"    ALERT: Hipotermia terdeteksi!")
                        print(f"    SENSOR: {id_sensor}")
                        print(f"    SUHU:   {suhu}°C")
                        print("="*40 + "\n")
                    
                    # (Status "ALERT" untuk DEMAM tidak perlu dicetak di sini,
                    # karena itu sudah ditangani oleh handle_interrupt)
                        
                except Exception as e:
                    print(f"ERROR: CPU gagal memproses log: {e}")
                # --- AKHIR LOGIKA ---
            else:
                # 3. Tidak ada data di bus, CPU bisa 'idle'
                time.sleep(0.1) 

        print("CPU 'processing loop' dihentikan.")

    def run(self):
        if self.is_running:
            print("CPU sudah berjalan.")
            return
        
        self.is_running = True
        self._thread = threading.Thread(target=self._processing_loop, daemon=True)
        self._thread.start()

    def stop(self):
        print("\nPerintah menghentikan CPU diterima...")
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        print("CPU dihentikan.")