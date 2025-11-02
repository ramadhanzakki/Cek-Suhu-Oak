import queue
import config
from src.visualizer import TemperatureVisualizer
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from .cpu import CPU
    from .sensor import TempSensor


class DataBus:
    def __init__(self, cpu_target: 'CPU'):
        print('Inisialisasi data bus')

        self.data_buffer = queue.Queue()
        self.cpu = cpu_target
        self.alert_threshold = config.BATAS_DEMAM
        self.visualizer: 'TemperatureVisualizer' | None = None

    def attach_visualizer(self, visualizer: 'TemperatureVisualizer'):
        print("Visualizer terhubung ke Data Bus.")
        self.visualizer = visualizer
      
    def register_sensor(self, sensor: 'TempSensor'):
        print(f"Sensor '{sensor.id}' terhubung ke Data Bus.")

        sensor.mulai_monitoring(callback_function=self.handler_sensor_data)
    
    def handler_sensor_data(self, data: Dict[str, any]):
        self.data_buffer.put(data)
        
        suhu = data.get('suhu')
        if suhu is None:
            return 
            
        is_fever = suhu > self.alert_threshold

        if self.visualizer:
            try:
                self.visualizer.add_data_point(suhu, is_fever)
            except Exception as e:
                print(f"Error mengirim data ke visualizer: {e}")
                
        if is_fever:
            self.cpu.handle_interrupt(data)

    def get_buffered_data(self):
        try:
            return self.data_buffer.get_nowait()
        except queue.Empty:
            return None