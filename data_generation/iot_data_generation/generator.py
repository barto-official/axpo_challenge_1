import json
import asyncio
import logging
import paho.mqtt.client as mqtt
from sensor import Sensor
from settings import get_settings

class Generator:
    def __init__(self):
        self.settings = get_settings()
        self.mqtt_client = mqtt.Client()

        with open("sensors.json") as sensors_json:
            _sensors = json.load(sensors_json)
            self.sensors = [
                Sensor(k, v, self.settings.interval_ms)
                for k, v in _sensors.items()
            ]

    async def generate(self):
        logging.basicConfig(level=self.settings.logging_level)

        self.mqtt_client.connect(self.settings.mqtt.host, self.settings.mqtt.port)

        tasks = [
            s.generate(self.mqtt_client, self.settings.mqtt.topic) for s in self.sensors
        ]

        await asyncio.gather(*tasks)
