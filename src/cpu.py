import threading
import time
import os
import config
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from .bus import DataBus


class CPU:
    def __init__(self):
        print('Inisialisasi CPU')
        self.bus = 'DataBus' | None = None
        self.is_running = False
        self._thread = None

        self.log_lock = threading.Lock()

        dir_utama = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.log_file_path = os.path.join(dir_utama, config.OUTPUT_FILE)

        self._setup_log_file()

    def attach_bus(self, bus: 'DataBus'):
        print('CPU terhububg ke Data Bus')
        self.bus = bus

    def _set_up_log_file(self):
        try:
            os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)

            with self.log_lock:
                with open(self.log_file_path, 'w', encoding='utf-8') as f:
                    f.write("waktu,id_sensor,suhu,status\n")

            print(f"File log disiapkan di {self.log_file_path}")
        
        except Exception as e:
            print(f"ERROR: Gagal membuat file log di {self.log_file_path}: {e}")

    def _log_data(self, data: Dict[str, Any]):
        try:
            suhu = data['suhu']
            
            if suhu > config.BATAS_DEMAM:
                status = "ALERT"
            elif suhu < config.BATAS_HIPO:
                status = "HIPOTERMIA"
            else:
                status = "NORMAL"
            
            timestamp = data['waktu'].isoformat()
            line = f"{timestamp},{data['id']},{data['suhu']},{status}\n"

            with self.log_lock:
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    f.write(line)

            if status == "NORMAL":
                print(f"[CPU Log]: Data normal dari {data['id']}: {suhu}°C")

        except Exception as e:
            print(f"ERROR: Gagal menulis log: {e}")

    def handle_interrupt(self, alert_data: Dict[str, Any]):
        print("\n" + "="*40)
        print(f"!!! INTERRUPT DITERIMA (CPU) !!!")
        print(f"    ALERT: Demam terdeteksi!")
        print(f"    SENSOR: {alert_data['id']}")
        print(f"    SUHU:   {alert_data['suhu']}°C")
        print("="*40 + "\n")

    def _processing_loop(self):
        print("CPU 'processing loop' (logging) dimulai...")
        while self.is_running:
            if not self.bus:
                print("CPU: Menunggu bus ditancapkan...")
                time.sleep(1)
                continue
            
            data = self.bus.get_buffered_data()
            
            if data:
                self._log_data(data)
            else:
                time.sleep(0.1)

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