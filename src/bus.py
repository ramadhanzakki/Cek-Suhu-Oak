import queue
import config
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from .cpu import CPU
    from .sensor import TempSensor


class DataStatus:
    def __init__(self, cpu_target: 'CPU'):
        print('Inisialisasi data bus')

        self.data_buffer = queue.Queue()
        self.cpu = cpu_target
        self.alert_threshold = config.BATAS_DEMAM
      
    def register_sensor(self, sensor: 'TempSensor'):
        print(f"Sensor '{sensor.id}' terhubung ke Data Bus.")

        sensor.mulai_monitoring(callback_function=self.handler_sensor_data)
    
    def handler_sensor_data(self, data: Dict[str, any]):
        self.data_buffer.put(data)
        suhu = data.get('suhu')

        if suhu is not None and suhu > self.alert_threshold:
            self.cpu.handle_interrupt(data)

    def get_buffered_data(self):
        try:
            return self.data_buffer.get_nowait()
        except queue.Empty:
            return None