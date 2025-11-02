# main.py

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from src.sensor import TempSensor
    from src.cpu import CPU
    from src.bus import DataBus
    import config
except ModuleNotFoundError as e:
    print(f"ERROR: Gagal import modul. Pastikan struktur file benar:")
    print(f"       {e}")
    print(f"       Pastikan Anda menjalankan 'python main.py' dari root folder.")
    sys.exit(1)


def main():
    print("="*50)
    print("     SISTEM MONITORING SUHU PASIEN VIRTUAL")
    print("="*50)
    print("Mulai inisialisasi komponen...")

    # --- 1. Perakitan Komponen ---
    cpu_utama = CPU()
    bus_data = DataBus(cpu_target=cpu_utama)
    cpu_utama.attach_bus(bus_data)

    # PERUBAHAN: Buat daftar sensor agar kita bisa memeriksanya
    list_sensor = [
        TempSensor(id='Kamar-101 (Random)', sumber_data='random'),
        TempSensor(id='Kamar-102 (File)', sumber_data='file')
        # Anda bisa menambah sensor lagi di sini
    ]
    
    print("\nKomponen berhasil dirakit.")

    # --- 2. Menghubungkan dan Menjalankan ---
    print("Menghubungkan sensor ke bus data...")
    for sensor in list_sensor:
        bus_data.register_sensor(sensor)

    cpu_utama.run()

    print("\n" + "="*50)
    print("     SIMULASI BERJALAN")
    print(f"     File log akan disimpan di: {config.OUTPUT_FILE}")
    print(f"     Sensor random akan berhenti setelah {config.JUMLAH_MAKSIMAL_RANDOM} data.")
    print("     Sensor file akan berhenti di akhir file.")
    print("     Tekan Ctrl+C untuk menghentikan lebih awal.")
    print("="*50 + "\n")

    # --- 3. Main Loop (DIRUBAH) ---
    try:
        # PERUBAHAN: Loop akan terus berjalan HANYA JIKA
        # masih ada sensor yang 'is_active'
        while any(s.is_active for s in list_sensor):
            # Kita tetap sleep agar loop ini tidak memakan CPU
            time.sleep(0.5)
        
        print("\n" + "="*50)
        print("     SEMUA SENSOR TELAH BERHENTI")
        print("     Memulai proses shutdown otomatis...")

    except KeyboardInterrupt:
        # Tangani jika user menekan Ctrl+C
        print("\n\n" + "="*50)
        print("     PERINTAH SHUTDOWN (Ctrl+C) DITERIMA")
        print("     Menghentikan semua komponen...")
        
        # 1. Hentikan sensor (jika ada yang masih jalan)
        for sensor in list_sensor:
            if sensor.is_active:
                sensor.stop_monitoring()
    
    finally:
        # --- BLOK SHUTDOWN (SEKARANG OTOMATIS) ---
        
        # 2. Hentikan CPU 
        #    Beri jeda singkat agar CPU bisa memproses data sisa di buffer
        print("Memberi CPU 1 detik untuk memproses sisa log...")
        time.sleep(1) 
        cpu_utama.stop()
        
        print("\nSimulasi berhasil dihentikan. Selamat tinggal!")
        print("="*50)

# --- Entry Point ---
if __name__ == "__main__":
    main()