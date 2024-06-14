# IoT Data Collection, Aggregation, Access Layer

## Introduction
This project aims to create a data engineering infrastructure for IoT domain to build a system that allows for easy access of data to Business Intelligence (BI) specialists and Data Scientists. The solution involves:
* Generating (fake, for simuluation) IoT data
* Collecting and storing data in raw format
* Aggregating  data for analysis
* API service to provide access to IoT data collected and stored in a MySQL database deployed to Azure.
* Data Catalog: Provides a catalog of datasets stored in the database, accessible via API endpoints.
* Data Quality Checks: Performs data validation checks on the datasets.

## How The System Works
1. Data is generated in using asynchronous functions.
    - Frequency of generation is 1 second.
    - There are data from 5 sensors

2. Data is aggregated (1 minute interval) in asynchronous way based on sensor_id.
    - Both types of data are inserted into MySQL databased deployed to Azure.

3. Data Access Layer is built in the form of FastAPI
   - This enables querying database and updating data
   - Validation checks are run based on API as well
   - Users can also browse data catalogs in GUI-like manner (Javascript, HTML, CSS)

<img width="1124" alt="Screenshot 2024-06-14 at 18 27 45" src="https://github.com/barto-official/axpo_challenge_1/assets/125658269/1123b1be-90a1-4de3-9eab-a977c218ee90">


## Project Structure
There are two main parts of the project: Data Generation and Access Layer. On top of that, we use MySQL database deployed on Azure.

### Data Generation Part

1. **MQTT Setup**: 
   - The application sets up an MQTT client using the `paho-mqtt` library.
   - It subscribes to a specified MQTT topic to receive sensor data.
   - The MQTT client is configured in `mqtt_handler.py`.
  
2. **Data Sources**:
   - Sensors: Defined in the sensors.json file, each sensor has attributes such as latitude, longitude, unit, type, range, and description.
   - The sensors simulate temperature data from different locations within an infrastructure (e.g., Main Entrance, Kitchen, Deposit, Assembly Floor, Offices).

3. **Data Generation**
   - generator.py: The main script that generates data from the defined sensors. It initializes the sensors and asynchronously gathers data from them. This script uses the Sensor class (from sensor.py) to create sensor objects and simulate data readings within specified ranges.
   
4. **Configuration and Settings**
   - settings.py: Contains configuration settings for the application, including Azure Event Hub connection details and general settings like logging levels and intervals for data generation.
   - sensors.json: Specifies the configuration of each sensor, including its location, measurement unit, and range.

6. **Receiving Data**: 
   - When the MQTT client receives a message, the `on_message` callback function is triggered.
   - The received message is decoded and parsed into a JSON object.

7. **Storing Raw Data**: 
   - The parsed data is inserted into the `sensor_data` table in the MySQL database using the `insert_data` method in `database.py`.

### Data Aggregation

1. **Aggregation Logic**:
   - The application maintains an in-memory store (`data_store`) to temporarily hold sensor data for aggregation.
   - The `handle_message` function stores incoming sensor data in `data_store`.

2. **Periodic Aggregation**:
   - An asynchronous task `aggregate_data` runs every minute to aggregate the stored sensor data.
   - For each sensor, the average value is calculated, and additional metadata is retained from the latest reading.

3. **Storing Aggregated Data**:
   - The aggregated data is inserted into the `aggregated_sensor_data` table in the MySQL database using the `insert_aggregated_data` method in `database.py`.

### API Part

#### Data Catalog

**Cataloging Datasets**:
   - The application provides API endpoints to list and retrieve metadata about datasets stored in the database.
   - Metadata about the datasets, including schema, data types, and descriptions, is stored in the `metadata` table.

#### Data Validation

**Validation Logic**:
   - The application uses Great Expectations to perform data validation checks on the datasets.
   - Validation checks include completeness, validity, consistency, timeliness, uniqueness, and integrity.

#### API Endpoints
- **GET `/data/`**: Retrieve sensor data with pagination.
  - **Parameters**: 
    - `skip`: Number of records to skip.
    - `limit`: Maximum number of records to return.

- **GET `/data/{sensor_id}`**: Retrieve sensor data for a specific sensor.
  - **Parameters**: 
    - `sensor_id`: ID of the sensor.
    - `skip`: Number of records to skip.
    - `limit`: Maximum number of records to return.

- **GET `/data/summary/`**: Retrieve a summary of sensor data with optional filters.
  - **Parameters**:
    - `type`: Type of sensor data (e.g., temperature).
    - `unit`: Unit of measurement.
    - `start_time`: Start time for the data query.
    - `end_time`: End time for the data query.
    - `skip`: Number of records to skip.
    - `limit`: Maximum number of records to return.

- **GET `/data/range/`**: Retrieve sensor data within a specific time range.
  - **Parameters**:
    - `start_time`: Start time for the data query.
    - `end_time`: End time for the data query.
    - `skip`: Number of records to skip.
    - `limit`: Maximum number of records to return.

- **POST `/data/`**: Create a new sensor data entry.
  - **Body**: 
    - `sensor_data`: SensorDataModel containing the sensor data to be added.

- **PUT `/data/{data_id}`**: Update an existing sensor data entry.
  - **Parameters**: 
    - `data_id`: ID of the data entry to update.
    - **Body**:
      - `sensor_data`: SensorDataModel containing the updated data.

- **DELETE `/data/{data_id}`**: Delete an existing sensor data entry.
  - **Parameters**: 
    - `data_id`: ID of the data entry to delete.

**Aggregated Data Endpoints**

- **GET `/aggregated_data/`**: Retrieve aggregated sensor data with pagination.
  - **Parameters**: 
    - `skip`: Number of records to skip.
    - `limit`: Maximum number of records to return.

- **GET `/aggregated_data/{sensor_id}`**: Retrieve aggregated sensor data for a specific sensor.
  - **Parameters**: 
    - `sensor_id`: ID of the sensor.
    - `skip`: Number of records to skip.
    - `limit`: Maximum number of records to return.

- **GET `/aggregated_data/summary/`**: Retrieve a summary of aggregated sensor data with optional filters.
  - **Parameters**:
    - `type`: Type of sensor data (e.g., temperature).
    - `unit`: Unit of measurement.
    - `start_time`: Start time for the data query.
    - `end_time`: End time for the data query.
    - `skip`: Number of records to skip.
    - `limit`: Maximum number of records to return.

- **GET `/aggregated_data/range/`**: Retrieve aggregated sensor data within a specific time range.
  - **Parameters**:
    - `start_time`: Start time for the data query.
    - `end_time`: End time for the data query.
    - `skip`: Number of records to skip.
    - `limit`: Maximum number of records to return.

**Metadata Endpoints**

- **GET `/metadata/`**: Retrieve metadata for all datasets.
  
**Data Quality Endpoint**

- **GET `/data/data-quality/`**: Perform data quality checks on the sensor data.

**Data Catalog Endpoint**

- **GET `/data/catalog/`**: Serve the data catalog page.


## Getting Started
If you want to run data generation layer:
1. Clone the repository `git clone`
2. `cd data_generation`
3. Run docker for generating data: `docker compose-build up`

If you want to run access layer (API):
1. Clone the repository `git clone`
2. `cd api`
3. Build docker: `docker build -t my_project .
4. Run Docker: `docker run -p 8000:8000 --name my_container_name my_project`

### Potential Drawbacks/Improvements:
- [ ] Create more sophisticated API: better in security, more POST methods
- [ ] Use Great Expectations for data validity
- [ ] Use professional, open-source tools for data cataloging

