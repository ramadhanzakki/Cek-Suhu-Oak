# src/visualizer.py - Real-Time Temperature Visualization
"""
Modul untuk visualisasi real-time suhu pasien menggunakan Matplotlib.
Implementasi animation dengan FuncAnimation untuk live updates.

Features:
- Real-time line plot
- Fever & Hypothermia threshold line
- Color coding (blue=hypothermia, green=normal, red=fever)
- Alert markers
- Auto-scroll window
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D
from collections import deque
from datetime import datetime
from typing import Optional, Deque
import threading

# Import config dengan fallback
try:
    import config
    FEVER_THRESHOLD = config.BATAS_DEMAM
    PLOT_UPDATE_INTERVAL = config.PLOT_UPDATE_INTERVAL
    PLOT_HISTORY_LENGTH = config.PLOT_HISTORY_LENGTH
    PLOT_WINDOW_SIZE = config.PLOT_WINDOW_SIZE
except:
    FEVER_THRESHOLD = 38.0
    PLOT_UPDATE_INTERVAL = 100  # milliseconds
    PLOT_HISTORY_LENGTH = 50
    PLOT_WINDOW_SIZE = (12, 6)


class TemperatureVisualizer:
    """
    Real-time temperature visualizer menggunakan Matplotlib.
    """

    def __init__(self, max_points: int = PLOT_HISTORY_LENGTH):
        self.max_points = max_points
        
        # Data storage
        self.times: Deque[float] = deque(maxlen=max_points)
        self.temperatures: Deque[float] = deque(maxlen=max_points)
        self.is_fever: Deque[bool] = deque(maxlen=max_points)
        
        # Alert markers
        self.alert_times: Deque[float] = deque(maxlen=max_points)
        self.alert_temps: Deque[float] = deque(maxlen=max_points)
        
        # Thread synchronization
        self._lock = threading.Lock()
        
        # Plot components
        self.fig = None
        self.ax = None
        self.line = None
        self.scatter = None
        self.threshold_line = None
        self.hypo_line = None
        self.animation = None
        
        # State
        self.is_running = False
        self.start_time = datetime.now()
        
        print("[VISUALIZER] Initialized")

    def add_data_point(self, temperature: float, is_fever: bool = False):
        """Add new temperature data point (thread-safe)."""
        with self._lock:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            self.times.append(elapsed)
            self.temperatures.append(temperature)
            self.is_fever.append(is_fever)
            
            if is_fever:
                self.alert_times.append(elapsed)
                self.alert_temps.append(temperature)

    def setup_plot(self):
        """Setup matplotlib figure dan axes."""
        self.fig, self.ax = plt.subplots(figsize=PLOT_WINDOW_SIZE)
        self.ax.set_xlabel('Time (seconds)', fontsize=12)
        self.ax.set_ylabel('Temperature (°C)', fontsize=12)
        self.ax.set_title('Real-Time Patient Temperature Monitoring',
                         fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_ylim(31, 42)

        # Garis suhu utama
        self.line, = self.ax.plot([], [], 'b-', linewidth=2, label='Temperature')

        # Marker alert
        self.scatter = self.ax.scatter([], [], c='red', s=100, 
                                       marker='X', zorder=5, label='Fever Alert')

        # Garis batas demam
        self.threshold_line = self.ax.axhline(y=FEVER_THRESHOLD, 
                                              color='red', linestyle='--', linewidth=2, alpha=0.7,
                                              label=f'Fever Threshold ({FEVER_THRESHOLD}°C)')

        # Garis batas hipotermia
        self.hypo_line = self.ax.axhline(y=35.0,
                                         color='blue', linestyle='--', linewidth=2, alpha=0.7,
                                         label='Hypothermia Threshold (35.0°C)')

        self.ax.legend(loc='upper left', fontsize=10)
        self.fig.tight_layout()
        print("[VISUALIZER] Plot setup complete")

    def _update_plot(self, frame):
        """Update function untuk FuncAnimation."""
        with self._lock:
            if len(self.times) > 0:
                times_list = list(self.times)
                temps_list = list(self.temperatures)

                self.line.set_data(times_list, temps_list)

                current_temp = temps_list[-1]

                # Tentukan status suhu
                if current_temp < 36.0:
                    status = "❄️ HYPOTHERMIA"
                    color = "blue"
                elif current_temp > 38.0:
                    status = "🔴 FEVER"
                    color = "red"
                else:
                    status = "🟢 NORMAL"
                    color = "green"

                # Update warna garis
                self.line.set_color(color)

                # Update judul grafik
                self.ax.set_title(
                    f'Real-Time Patient Temperature Monitoring | '
                    f'Current: {current_temp:.1f}°C {status}',
                    fontsize=14, fontweight='bold',
                    color=color
                )

                # Update marker alert
                if len(self.alert_times) > 0:
                    self.scatter.set_offsets(
                        list(zip(list(self.alert_times), list(self.alert_temps)))
                    )

                # Auto-scale x-axis
                if len(times_list) > 0:
                    self.ax.set_xlim(max(0, times_list[-1] - 30),
                                     times_list[-1] + 5)

        return self.line, self.scatter

    def start(self):
        """Start visualization (blocking)."""
        if self.is_running:
            print("[VISUALIZER] Already running")
            return
        self.is_running = True

        self.setup_plot()
        self.animation = animation.FuncAnimation(
            self.fig,
            self._update_plot,
            interval=PLOT_UPDATE_INTERVAL,
            blit=True,
            cache_frame_data=False
        )

        print("[VISUALIZER] Animation started")
        plt.show()

    def start_in_thread(self):
        """Start visualization di thread terpisah (non-blocking)."""
        if self.is_running:
            print("[VISUALIZER] Already running")
            return
        threading.Thread(target=self.start, daemon=True).start()
        print("[VISUALIZER] Started in background thread")

    def stop(self):
        """Stop visualization."""
        self.is_running = False
        if self.animation:
            self.animation.event_source.stop()
        plt.close(self.fig)
        print("[VISUALIZER] Stopped")


# =====================================================================
# TESTING (bisa dijalankan langsung untuk uji mandiri)
# =====================================================================
if __name__ == "__main__":
    import time, random
    print("="*70)
    print(" VISUALIZER MODULE - STANDALONE TEST ".center(70, "="))
    print("="*70)
    viz = TemperatureVisualizer(max_points=50)
    viz.start_in_thread()
    time.sleep(2)

    try:
        for i in range(100):
            temp = random.uniform(33.5, 40.5)
            is_fever = temp > 37.5
            viz.add_data_point(temp, is_fever)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[TEST] Interrupted by user")
    viz.stop()
    print("\n" + "="*70)
    print(" TEST COMPLETED ".center(70, "="))
    print("="*70)
