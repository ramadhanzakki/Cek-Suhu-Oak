# main.py

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from src.sensor import TempSensor
    from src.cpu import CPU
    from src.bus import DataBus
    # TAMBAHKAN impor visualizer
    from src.visualizer import TemperatureVisualizer
    from src.logger import Logger
    import config
except ModuleNotFoundError as e:
    print(f"ERROR: Gagal import modul...")
    print(f"       {e}")
    sys.exit(1)
except ImportError as e:
    print(f"ERROR: Gagal import. Mungkin Anda lupa install Matplotlib?")
    print(f"       Coba jalankan: pip install matplotlib")
    print(f"       Error asli: {e}")
    sys.exit(1)


def main():
    print("="*50)
    print("     SISTEM MONITORING SUHU PASIEN VIRTUAL")
    print("="*50)
    print("Mulai inisialisasi komponen...")

    # --- 1. Perakitan Komponen ---
    logger = Logger()
    cpu_utama = CPU()
    bus_data = DataBus(cpu_target=cpu_utama)
    cpu_utama.attach_bus(bus_data)
    logger.setup()
    cpu_utama.attach_logger(logger)


    # TAMBAHKAN: Buat instance visualizer
    viz = TemperatureVisualizer(max_points=config.PLOT_HISTORY_LENGTH)
    
    # TAMBAHKAN: Tancapkan visualizer ke Bus
    bus_data.attach_visualizer(viz)

    print(f"Mode Sumber Data Global diatur ke: '{config.DATA_SOURCE.upper()}'")

    list_sensor = [
        TempSensor(id='Kamar-101 (File)'),
        TempSensor(id='Kamar-102 (File)')
    ]
    
    print("\nKomponen berhasil dirakit.")

    # --- 2. Menghubungkan dan Menjalankan ---
    print("Menghubungkan sensor ke bus data...")
    for sensor in list_sensor:
        bus_data.register_sensor(sensor)

    # Jalankan CPU
    cpu_utama.run()
    
    # TAMBAHKAN: Jalankan visualizer di thread-nya sendiri
    print("Memulai jendela visualisasi (grafik)...")
    viz.start_in_thread()


    print("\n" + "="*50)
    print("     SIMULASI BERJALAN")
    print(f"     Mode Sumber Data: {config.DATA_SOURCE.upper()}")
    print(f"     File log akan disimpan di: {config.OUTPUT_FILE}")
    # ... (sisanya sama) ...
    print("="*50 + "\n")

    # --- 3. Main Loop ---
    try:
        while any(s.is_active for s in list_sensor):
            time.sleep(0.5)
            
            # TAMBAHKAN: Cek apakah jendela visualizer ditutup manual
            # Jika viz.is_running jadi False (karena jendela ditutup)
            # kita bisa anggap itu sebagai sinyal stop.
            if not viz.is_running and 'viz' in locals():
                 print("\nJendela Visualizer ditutup, menghentikan simulasi...")
                 break # Keluar dari loop untuk shutdown

        
        print("\n" + "="*50)
        print("     SEMUA SENSOR TELAH BERHENTI")
        print("     Memulai proses shutdown otomatis...")

    except KeyboardInterrupt:
        print("\n\n" + "="*50)
        print("     PERINTAH SHUTDOWN (Ctrl+C) DITERIMA")
        print("     Menghentikan semua komponen...")
        
        for sensor in list_sensor:
            if sensor.is_active:
                sensor.stop_monitoring()
    
    finally:
        # --- BLOK SHUTDOWN ---
        print("\nMenghentikan semua komponen...")
        
        # TAMBAHKAN: Hentikan Visualizer
        if 'viz' in locals() and viz.is_running:
            print("Menghentikan visualizer...")
            viz.stop()
            
        print("Memberi CPU 1 detik untuk memproses sisa log...")
        time.sleep(1) 
        cpu_utama.stop()
        logger.close()
        
        print("\nSimulasi berhasil dihentikan. Selamat tinggal!")
        print("="*50)

if __name__ == "__main__":
    main()