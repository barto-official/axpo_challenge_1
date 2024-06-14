import json
import asyncio
import logging
from paho.mqtt.client import Client
from database import Database
from settings import get_settings
from collections import defaultdict

settings = get_settings()
database = Database()

# Dictionary to hold aggregated data
data_store = defaultdict(list)
lock = asyncio.Lock()
loop = asyncio.get_event_loop()

# MQTT Callback functions
def on_message(client, userdata, message):
    """
    Callback function for when a message is received from the MQTT server.

    Args:
        client (paho.mqtt.client.Client): The MQTT client instance.
        userdata: The private user data.
        message (paho.mqtt.client.MQTTMessage): The message received from the server.
    """
    data = json.loads(message.payload.decode())
    database.insert_data(data)
    asyncio.run_coroutine_threadsafe(handle_message(data), loop)

def on_connect(client, userdata, flags, rc):
    """
    Callback function for when the client receives a CONNACK response from the MQTT server.

    Args:
        client (paho.mqtt.client.Client): The MQTT client instance.
        userdata: The private user data.
        flags (dict): Response flags sent by the broker.
        rc (int): The connection result.
    """
    logging.info(f"Connected with result code {rc}")
    client.subscribe(settings.mqtt.topic)

async def handle_message(payload):
    """
    Handle incoming MQTT messages by storing them in the data store.

    Args:
        payload (dict): The payload of the MQTT message.
    """
    async with lock:
        sensor_id = int(payload.get('sensor_id'))
        data_store[sensor_id].append(payload)

async def aggregate_data():
    """
    Aggregate sensor data every 1 minute and insert the aggregated data into the database.
    """
    while True:
        await asyncio.sleep(60)  # Wait for 1 minute
        async with lock:
            for sensor_id, readings in data_store.items():
                if readings:
                    avg_value = sum([r['value'] for r in readings]) / len(readings)
                    # Use the most recent reading for the additional fields
                    last_reading = readings[-1]
                    await insert_aggregated_data(sensor_id, avg_value, last_reading)
            data_store.clear()

async def insert_aggregated_data(sensor_id, avg_value, last_reading):
    """
    Insert aggregated sensor data into the MySQL database.

    Args:
        sensor_id (int): The sensor ID.
        avg_value (float): The average value of the sensor readings.
        last_reading (dict): The last reading from the sensor.
    """
    logging.info(f"Inserting aggregated data for sensor_id {sensor_id}: avg_value={avg_value}, last_reading={last_reading}")
    database.insert_aggregated_data(sensor_id, avg_value, last_reading)

# MQTT setup
def setup_mqtt():
    """
    Set up the MQTT client and start the loop.

    Returns:
        paho.mqtt.client.Client: Configured MQTT client.
    """
    mqtt_client = Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(settings.mqtt.host, settings.mqtt.port, 60)
    mqtt_client.subscribe(settings.mqtt.topic)
    mqtt_client.loop_start()
    return mqtt_client
