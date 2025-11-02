import threading
import queue
import os
import config
from typing import Dict, Any

class Logger:
    """
    Komponen khusus untuk menangani logging ke file CSV.
    Berjalan di thread-nya sendiri dengan antrian (queue) 
    untuk penulisan yang aman dan non-blocking.
    """
    def __init__(self):
        print("Inisialisasi Logger...")
        self.log_queue = queue.Queue()
        self.is_running = False
        self._thread = None
        self.log_lock = threading.Lock() # Lock untuk file write

        # Tentukan path file log dari root proyek
        dir_utama = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.log_file_path = os.path.join(dir_utama, config.OUTPUT_FILE)
        
        # Siapkan file log
        self._setup_log_file()

    def _setup_log_file(self):
        """Membuat file log dan menulis header-nya."""
        try:
            os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
            with self.log_lock:
                with open(self.log_file_path, 'w', encoding='utf-8') as f:
                    f.write("waktu,id_sensor,suhu,status\n")
            print(f"File log disiapkan di {self.log_file_path}")
        except Exception as e:
            print(f"ERROR: Gagal membuat file log di {self.log_file_path}: {e}")

    def _write_to_file(self, data: Dict[str, Any]):
        """
        Fungsi internal untuk memproses dan menulis satu baris data ke file.
        Fungsi ini dipanggil oleh _processing_loop.
        """
        try:
            suhu = data['suhu']
            
            # Tentukan status berdasarkan suhu
            if suhu > config.BATAS_DEMAM:
                status = "ALERT"
            elif suhu < config.BATAS_HIPO:
                status = "HIPOTERMIA"
            else:
                status = "NORMAL"
            
            timestamp = data['waktu'].isoformat()
            line = f"{timestamp},{data['id']},{data['suhu']},{status}\n"
            
            # Tulis ke file (mode 'a' = append) secara thread-safe
            with self.log_lock:
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    f.write(line)
                    
            # Cetak ke konsol juga (opsional, tapi bagus untuk debug)
            if status == "NORMAL":
                print(f"[Logger]: Data normal dari {data['id']}: {suhu}°C")
                
        except Exception as e:
            print(f"ERROR: Gagal menulis log: {e}")

    def log_data(self, data: Dict[str, Any]):
        """
        API publik: Fungsi ini yang dipanggil oleh komponen lain (CPU)
        untuk menambahkan data ke antrian log.
        """
        if self.is_running:
            self.log_queue.put(data)

    def _processing_loop(self):
        """Loop internal yang berjalan di thread Logger."""
        print("Logger 'processing loop' dimulai...")
        while self.is_running:
            try:
                # Ambil data dari antrian, blokir sampai ada data
                # Timeout 1 detik agar loop bisa cek 'self.is_running'
                data = self.log_queue.get(timeout=1)
                
                if data is None: # Sentinel untuk berhenti
                    break
                    
                self._write_to_file(data)
                self.log_queue.task_done()
                
            except queue.Empty:
                # Ini wajar terjadi jika tidak ada data log baru
                continue
                
        print("Logger 'processing loop' dihentikan.")

    def run(self):
        """Menjalankan thread Logger."""
        if self.is_running:
            return
        self.is_running = True
        self._thread = threading.Thread(target=self._processing_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Menghentikan thread Logger dengan rapi."""
        print("\nPerintah menghentikan Logger diterima...")
        self.is_running = False
        
        # Kirim sinyal 'None' untuk 'membangunkan' queue.get()
        self.log_queue.put(None) 
        
        if self._thread:
            self._thread.join(timeout=2.0)
        print("Logger dihentikan.")