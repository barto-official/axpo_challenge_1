import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class MqttSettings():
    host: str = os.getenv('MQTT_HOST')
    port: int = int(os.getenv('MQTT_PORT'))
    topic: str = os.getenv('MQTT_TOPIC')

class MySQLSettings():
    user: str = os.getenv('MYSQL_USER')
    password: str = os.getenv('MYSQL_PASSWORD')
    host: str = os.getenv('MYSQL_HOST')
    database: str = os.getenv('MYSQL_DATABASE')

class Settings():
    mqtt: MqttSettings = MqttSettings()
    mysql: MySQLSettings = MySQLSettings()
    interval_ms: int = int(os.getenv('INTERVAL_MS', '1000'))
    logging_level: int = int(os.getenv('LOGGING_LEVEL', '30'))

def get_settings() -> Settings:
    return Settings()
