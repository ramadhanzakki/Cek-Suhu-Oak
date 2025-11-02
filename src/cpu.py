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

    def _processing_loop(self):
        print("CPU 'processing loop' (logging) dimulai...")
        while self.is_running:
            if not self.bus or not self.logger:
                print("CPU: Menunggu bus ditancapkan...")
                time.sleep(1)
                continue
            
            data = self.bus.get_buffered_data()
            
            if data:
                self.logger.log_data(data)
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