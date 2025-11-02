# src/visualizer.py - Real-Time Temperature Visualization
"""
Modul untuk visualisasi real-time suhu pasien menggunakan Matplotlib.
Implementasi animation dengan FuncAnimation untuk live updates.

Features:
- Real-time line plot
- Fever threshold line
- Color coding (green=normal, red=fever)
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
    
    Konsep:
    - FuncAnimation untuk update plot secara periodik
    - Deque untuk sliding window data (FIFO)
    - Thread-safe data handling
    """
    
    def __init__(self, max_points: int = PLOT_HISTORY_LENGTH):
        """
        Initialize visualizer.
        
        Args:
            max_points: Maximum data points yang ditampilkan di plot
        """
        self.max_points = max_points
        
        # Data storage (thread-safe dengan deque)
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
        self.animation = None
        
        # State
        self.is_running = False
        self.start_time = datetime.now()
        
        print("[VISUALIZER] Initialized")
    
    def add_data_point(self, temperature: float, is_fever: bool = False):
        """
        Add new temperature data point (thread-safe).
        
        Args:
            temperature: Temperature value
            is_fever: Whether this reading is fever
        """
        with self._lock:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            self.times.append(elapsed)
            self.temperatures.append(temperature)
            self.is_fever.append(is_fever)
            
            # Track fever alerts for markers
            if is_fever:
                self.alert_times.append(elapsed)
                self.alert_temps.append(temperature)
    
    def setup_plot(self):
        """Setup matplotlib figure dan axes."""
        # Create figure
        self.fig, self.ax = plt.subplots(figsize=PLOT_WINDOW_SIZE)
        
        # Configure plot
        self.ax.set_xlabel('Time (seconds)', fontsize=12)
        self.ax.set_ylabel('Temperature (°C)', fontsize=12)
        self.ax.set_title('Real-Time Patient Temperature Monitoring', 
                         fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        
        # Set y-axis limits
        self.ax.set_ylim(35, 42)
        
        # Initialize empty line
        self.line, = self.ax.plot([], [], 'b-', linewidth=2, label='Temperature')
        
        # Initialize scatter for alerts
        self.scatter = self.ax.scatter([], [], c='red', s=100, 
                                       marker='X', zorder=5, 
                                       label='Fever Alert')
        
        # Threshold line
        self.threshold_line = self.ax.axhline(y=FEVER_THRESHOLD, 
                                              color='red', 
                                              linestyle='--', 
                                              linewidth=2, 
                                              alpha=0.7,
                                              label=f'Fever Threshold ({FEVER_THRESHOLD}°C)')
        
        # Legend
        self.ax.legend(loc='upper left', fontsize=10)
        
        # Tight layout
        self.fig.tight_layout()
        
        print("[VISUALIZER] Plot setup complete")
    
    def _update_plot(self, frame):
        """
        Update function untuk FuncAnimation.
        Dipanggil secara periodik untuk update plot.
        
        Args:
            frame: Frame number (dari FuncAnimation)
        """
        with self._lock:
            if len(self.times) > 0:
                # Convert deque to list untuk plotting
                times_list = list(self.times)
                temps_list = list(self.temperatures)
                
                # Update line data
                self.line.set_data(times_list, temps_list)
                
                # Color code: green for normal, red for fever
                colors = ['red' if fever else 'green' 
                         for fever in self.is_fever]
                
                # Update line color berdasarkan data terakhir
                if self.is_fever[-1]:
                    self.line.set_color('red')
                else:
                    self.line.set_color('green')
                
                # Update alert markers
                if len(self.alert_times) > 0:
                    alert_times_list = list(self.alert_times)
                    alert_temps_list = list(self.alert_temps)
                    self.scatter.set_offsets(
                        list(zip(alert_times_list, alert_temps_list))
                    )
                
                # Auto-scale x-axis
                if len(times_list) > 0:
                    self.ax.set_xlim(max(0, times_list[-1] - 30), 
                                    times_list[-1] + 5)
                
                # Update title dengan current temp
                current_temp = temps_list[-1]
                status = "🔴 FEVER" if self.is_fever[-1] else "🟢 NORMAL"
                self.ax.set_title(
                    f'Real-Time Patient Temperature Monitoring | '
                    f'Current: {current_temp:.1f}°C {status}',
                    fontsize=14, fontweight='bold'
                )
        
        return self.line, self.scatter
    
    def start(self):
        """Start visualization (non-blocking)."""
        if self.is_running:
            print("[VISUALIZER] Already running")
            return
        
        self.is_running = True
        
        # Setup plot
        self.setup_plot()
        
        # Create animation
        self.animation = animation.FuncAnimation(
            self.fig,
            self._update_plot,
            interval=PLOT_UPDATE_INTERVAL,  # Update setiap 100ms
            blit=True,
            cache_frame_data=False
        )
        
        print("[VISUALIZER] Animation started")
        print(f"[VISUALIZER] Update interval: {PLOT_UPDATE_INTERVAL}ms")
        
        # Show plot (blocking call)
        # NOTE: plt.show() akan block thread ini
        # Untuk non-blocking, run di thread terpisah
        plt.show()
    
    def start_in_thread(self):
        """Start visualization di thread terpisah (non-blocking)."""
        if self.is_running:
            print("[VISUALIZER] Already running")
            return
        
        # Run visualization di thread terpisah
        viz_thread = threading.Thread(target=self.start, daemon=True)
        viz_thread.start()
        
        print("[VISUALIZER] Started in background thread")
    
    def stop(self):
        """Stop visualization."""
        self.is_running = False
        if self.animation:
            self.animation.event_source.stop()
        plt.close(self.fig)
        print("[VISUALIZER] Stopped")


# ============================================================================
# TESTING CODE
# ============================================================================

if __name__ == "__main__":
    """
    Test visualizer standalone dengan simulated data.
    """
    import time
    import random
    
    print("="*70)
    print(" VISUALIZER MODULE - STANDALONE TEST ".center(70, "="))
    print("="*70)
    print()
    
    print("Creating visualizer...")
    viz = TemperatureVisualizer(max_points=50)
    
    print("Starting visualization in background thread...")
    viz.start_in_thread()
    
    # Wait for plot window to open
    time.sleep(2)
    
    print("\nGenerating simulated temperature data...")
    print("Watch the plot window for real-time updates!")
    print("Close the plot window to exit.\n")
    
    try:
        # Simulate temperature readings
        for i in range(100):
            # Generate random temperature (mostly normal, sometimes fever)
            if random.random() < 0.2:  # 20% chance fever
                temp = random.uniform(38.0, 40.5)
                is_fever = True
            else:
                temp = random.uniform(35.5, 37.8)
                is_fever = False
            
            # Add to visualizer
            viz.add_data_point(temp, is_fever)
            
            # Print status
            status = "🔴 FEVER" if is_fever else "🟢 NORMAL"
            print(f"[{i+1:3d}] {temp:.1f}°C {status}")
            
            # Sleep to simulate real-time data (2 seconds per reading)
            time.sleep(0.5)  # Faster untuk testing
            
    except KeyboardInterrupt:
        print("\n[TEST] Interrupted by user")
    
    print("\n[TEST] Stopping visualizer...")
    viz.stop()
    
    print("\n" + "="*70)
    print(" TEST COMPLETED ".center(70, "="))
    print("="*70)