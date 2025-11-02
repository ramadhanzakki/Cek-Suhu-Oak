# main.py

import sys
import os
import time

# --- Penyesuaian Path ---
# Tambahkan root directory (tempat main.py berada) ke sys.path
# Ini agar Python bisa menemukan folder 'src' untuk import
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    # Import komponen-komponen kita dari folder 'src'
    from src.sensor import TempSensor
    from src.cpu import CPU
    from src.bus import DataBus
    import config # Pastikan file config.py ada di root
except ModuleNotFoundError as e:
    print(f"ERROR: Gagal import modul. Pastikan struktur file benar:")
    print(f"       {e}")
    print(f"       Pastikan Anda menjalankan 'python main.py' dari root folder.")
    sys.exit(1)


def main():
    """
    Fungsi utama untuk merakit dan menjalankan simulasi.
    Ini adalah 'Motherboard' dari sistem kita.
    """
    
    print("="*50)
    print("     SISTEM MONITORING SUHU PASIEN VIRTUAL")
    print("="*50)
    print("Mulai inisialisasi komponen...")

    # --- 1. Perakitan Komponen (Instantiation) ---
    
    # a. Buat CPU terlebih dahulu
    cpu_utama = CPU()
    
    # b. Buat Bus Data, dan berikan referensi CPU kepadanya
    #    (Bus perlu tahu CPU mana yang harus di-interrupt)
    bus_data = DataBus(cpu_target=cpu_utama)
    
    # c. 'Tancapkan' Bus ke CPU
    #    (CPU perlu tahu Bus mana yang harus di-polling untuk log)
    cpu_utama.attach_bus(bus_data)
    
    # d. Buat Sensor (Perangkat I/O)
    #    Kita bisa buat lebih dari satu, masing-masing dengan ID unik
    sensor_pasien_1 = TempSensor(id='Kamar-101 (Random)', sumber_data='random')
    sensor_pasien_2 = TempSensor(id='Kamar-102 (File)', sumber_data='file')
    
    print("\nKomponen berhasil dirakit.")

    # --- 2. Menghubungkan dan Menjalankan (Power On) ---
    
    print("Menghubungkan sensor ke bus data...")
    # 'Tancapkan' sensor ke Bus.
    # Ini akan otomatis memanggil sensor.mulai_monitoring()
    # dan mengatur callback sensor ke 'bus.handle_sensor_data'
    bus_data.register_sensor(sensor_pasien_1)
    bus_data.register_sensor(sensor_pasien_2)

    # Jalankan CPU (memulai thread logging/polling)
    cpu_utama.run()

    print("\n" + "="*50)
    print("     SIMULASI BERJALAN")
    print(f"     File log akan disimpan di: {config.OUTPUT_FILE}")
    print("     Tekan Ctrl+C untuk menghentikan simulasi.")
    print("="*50 + "\n")

    # --- 3. Main Loop ---
    try:
        # Jaga agar main thread tetap hidup
        # CPU dan Sensor berjalan di daemon thread mereka sendiri
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        # Tangani jika user menekan Ctrl+C
        print("\n\n" + "="*50)
        print("     PERINTAH SHUTDOWN (Ctrl+C) DITERIMA")
        print("     Menghentikan semua komponen...")
        
        # 1. Hentikan sensor (berhenti memproduksi data)
        sensor_pasien_1.stop_monitoring()
        sensor_pasien_2.stop_monitoring()
        
        # 2. Hentikan CPU (berhenti memproses/logging)
        #    Beri jeda singkat agar CPU bisa memproses data sisa di buffer
        time.sleep(0.5) 
        cpu_utama.stop()
        
        print("\nSimulasi berhasil dihentikan. Selamat tinggal!")
        print("="*50)

# --- Entry Point ---
if __name__ == "__main__":
    main()