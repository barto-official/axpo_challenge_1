import json
import datetime
import random
import asyncio
import logging
import paho.mqtt.client as mqtt

class Sensor:
    def __init__(self, id: str, config: dict, interval_ms: int):
        self.id = id
        self.lat = config["lat"]
        self.lng = config["lng"]
        self.unit = config["unit"]
        self.type = config["type"]
        self.range = config["range"]
        self.description = config["description"]
        self.interval_ms = interval_ms

    async def generate(self, mqtt_client: mqtt.Client, topic: str):
        while True:
            data = {
                "sensor_id": self.id,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "value": random.randint(*self.range),
                "metadata": {
                    "location": {
                        "lat": self.lat,
                        "lng": self.lng
                    },
                    "unit": self.unit,
                    "type": self.type,
                    "description": self.description
                }
            }

            payload = json.dumps(data, default=str)

            logging.info(f"{topic}: {payload}")

            mqtt_client.publish(topic, payload)
            await asyncio.sleep(self.interval_ms / 1000)
