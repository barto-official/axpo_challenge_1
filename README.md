# IoT Data Collection, Aggregation, Access Layer

## Introduction
This project aims to create a data engineering infrastructure for IoT domain to build a system that allows for an easy access of data to Business Intelligence (BI) specialists and Data Scientists. The solution involves:
* generating (fake, for simuluation) IoT data
* collecting and storing data in raw format
* aggregating  data for analysis
* API service to provide access to IoT data collected and stored in a SQLite database.
* Data Catalog
* Data Quality Checks.


## Project Structure
The project contains the following components:
* generator.py: Generates IoT data based on the configurations provided in sensors.json.
* sensors.json: Configuration file that defines the sensors, their types, locations, and other details.
* run.py: Collects raw IoT data and stores it in a MySQL database.
* aggregate.py: Aggregates the collected data to compute mean values for each sensor every minute.
* settings.py: Configuration settings for MQTT broker and MySQL database.
* Dockerfile: Instructions to build the Docker image.
* requirements.txt: List of Python dependencies.
* sensor.py: Script related to sensor data handling.
* mosquitto.conf: configuration file for mqtt mosquitto broker

## Getting Started
### Prerequisites
* Docker
* Docker Compose

### Installation
1. Clone the repository:
`git clone axpo_challenge_1`
`cd axpo_challenge_1`
2. Build and run the Docker containers:
`docker-compose up --build -d`

## Services
The project is set up using Docker Compose and includes the following services:

1. IoT Data Generator:
* Generates IoT data and sends it to an MQTT broker (interval = 1s)

2. MQTT Broker:
* Facilitates the communication between the data generator and the data collection services.

3. Raw Data Inserter (run.py):
* Collects raw IoT data from the MQTT broker and inserts it into a MySQL database.

4. Data Aggregator (aggregate.py):
* Aggregates the raw data to compute mean values for each sensor every minute and stores the aggregated data in MySQL.

3. Data Catalog Service:
* Provides a REST API to query the data catalog.
* Script: data_catalog_service.py

4. Data Quality Indicator Service:
* Provides a REST API to query data quality metrics.
* Script: data_quality_service.py

5. Configuration
* Configuration settings are managed in settings.py and environment variables. Ensure to update the settings in settings.py as per your environment.

## Usage
1. Generate IoT Data:
* The generator.py script generates IoT data based on sensors.json.

2. Insert Raw Data:
* The run.py script subscribes to the MQTT broker, receives the IoT data, and inserts it into the sensor_data table in MySQL.

3. Aggregate Data:
* The aggregate.py script subscribes to the MQTT broker, receives the IoT data, aggregates it, and inserts the aggregated data into the aggregated_data table in MySQL.

4. Data Catalog Service:
* The data_catalog_service.py script provides a REST API endpoint (/catalog) to query the data catalog.
* Access it at http://localhost:5000/catalog.

5. Data Quality Indicator Service:
* The data_quality_service.py script provides a REST API endpoint (/quality) to query data quality metrics.
* Access it at http://localhost:5001/quality.

## Sensors

Sensors are manually created to mimic the real-world scenario. You will find more information about each of 5 sensors in `sensors.json`.
