import mysql.connector
from mysql.connector import Error
import os
import threading
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class Database:
    """
    A class to manage MySQL database operations for sensor data.
    """
    def __init__(self):
        """
        Initialize the database connection and create the tables if they don't exist.
        """
        self.lock = threading.Lock()
        self.create_sensor_data_table()
        self.create_aggregated_data_table()

    def create_connection(self):
        """
        Create a database connection to the MySQL database.

        Returns:
            mysql.connector.connection.MySQLConnection: Database connection object.
        """
        conn = None
        try:
            conn = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST'),
                user=os.getenv('MYSQL_USER'),
                password=os.getenv('MYSQL_PASSWORD'),
                database=os.getenv('MYSQL_DB')
            )
        except Error as e:
            print(e)
        return conn

    def create_sensor_data_table(self):
        """
        Create the sensor_data table if it doesn't exist.
        """
        conn = self.create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sensor_id INT,
                    timestamp DATETIME,
                    value FLOAT,
                    lat FLOAT,
                    lng FLOAT,
                    unit VARCHAR(255),
                    type VARCHAR(255),
                    description TEXT
                )
                """)
                conn.commit()
            finally:
                conn.close()
        else:
            print("Error! cannot create the database connection.")

    def create_aggregated_data_table(self):
        """
        Create the aggregated_sensor_data table if it doesn't exist.
        """
        conn = self.create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS aggregated_sensor_data (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sensor_id INT,
                    timestamp DATETIME,
                    value FLOAT,
                    lat FLOAT,
                    lng FLOAT,
                    unit VARCHAR(255),
                    type VARCHAR(255),
                    description TEXT
                )
                """)
                conn.commit()
            finally:
                conn.close()
        else:
            print("Error! cannot create the database connection.")

    def insert_data(self, data):
        """
        Insert sensor data into the sensor_data table.

        Args:
            data (dict): The sensor data to insert.
        """
        with self.lock:
            conn = self.create_connection()
            if conn is not None:
                try:
                    cursor = conn.cursor()
                    query = """
                    INSERT INTO sensor_data (sensor_id, timestamp, value, lat, lng, unit, type, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    # Convert timestamp to datetime object
                    timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")
                    cursor.execute(query, (
                        int(data['sensor_id']), timestamp, data['value'],
                        data['metadata']['location']['lat'], data['metadata']['location']['lng'],
                        data['metadata']['unit'], data['metadata']['type'], data['metadata']['description']
                    ))
                    conn.commit()
                except Error as e:
                    print(f"Error inserting data: {e}")
                finally:
                    conn.close()
            else:
                print("Error! cannot create the database connection.")

    def insert_aggregated_data(self, sensor_id, avg_value, last_reading):
        """
        Insert aggregated sensor data into the aggregated_sensor_data table.

        Args:
            sensor_id (int): The sensor ID.
            avg_value (float): The average value of the sensor readings.
            last_reading (dict): The last reading from the sensor.
        """
        conn = self.create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                query = """
                INSERT INTO aggregated_sensor_data (sensor_id, timestamp, value, lat, lng, unit, type, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                data_values = (
                    int(sensor_id), datetime.now(), avg_value,
                    last_reading["metadata"]["location"]['lat'], last_reading["metadata"]["location"]['lng'],
                    last_reading["metadata"]['unit'], last_reading["metadata"]['type'], last_reading["metadata"]['description']
                )
                cursor.execute(query, data_values)
                conn.commit()
                print(f"Inserted aggregated data successfully: {data_values}")
            except Error as e:
                print(f"Error inserting aggregated data: {e}")
            finally:
                conn.close()
        else:
            print("Error! cannot create the database connection.")
