from fastapi import FastAPI, HTTPException, Query, Depends, Request
from sqlalchemy import create_engine, Column, Integer, Float, DateTime, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import os
import pandas as pd
import urllib.parse
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import logging
from fastapi import APIRouter
from sqlalchemy.orm import Session
import pandas as pd

router = APIRouter()

# Load environment variables from .env file
load_dotenv()

# Database connection setup
USER = os.environ.get("MYSQL_USER")
PASSWORD = os.environ.get("MYSQL_PASSWORD")
DATABASE = os.environ.get("MYSQL_DATABASE")
HOST = os.environ.get("MYSQL_HOST")
PASSWORD = urllib.parse.quote_plus(PASSWORD)
DATABASE_URL = f"mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}:3306/{DATABASE}"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy model for SensorData
class SensorData(Base):
    __tablename__ = "sensor_data"
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    unit = Column(String(10), nullable=False)
    type = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)

# SQLAlchemy model for SensorData
class AggregatedData(Base):
    __tablename__ = "aggregated_sensor_data"
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    unit = Column(String(10), nullable=False)
    type = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)

class Metadata(Base):
    __tablename__ = "metadata"
    id = Column(Integer, primary_key=True, index=True)
    dataset_name = Column(String(50), nullable=False)
    schema_used = Column(String(255), nullable=False)
    data_types = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    application = Column(String(255), nullable=False)
    lineage = Column(String(255), nullable=False)

# Pydantic models for data
class SensorDataModel(BaseModel):
    id: int
    sensor_id: int
    timestamp: datetime
    value: float
    lat: float
    lng: float
    unit: str
    type: str
    description: str

    class Config:
        orm_mode = True

class AggregatedDataModel(BaseModel):
    id: int
    sensor_id: int
    timestamp: datetime
    value: float
    lat: float
    lng: float
    unit: str
    type: str
    description: str

    class Config:
        orm_mode = True

class MetadataModel(BaseModel):
    id: int
    dataset_name: str
    schema_used: str
    data_types: str
    description: str
    application: str
    lineage: str

    class Config:
        orm_mode = True

# Initialize FastAPI application
app = FastAPI()

# Dependency to get the SQLAlchemy session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates directory
templates = Jinja2Templates(directory="templates")

@app.get("/")
def read_root(request: Request):
    """
    Root endpoint to serve the home page.
    """
    return "API up and running. Query data or go to `/docs/` for documentation"


@app.get("/data/", response_model=List[SensorDataModel])
def read_data(skip: int = 0, limit: int = Query(default=100, le=1000), db: Session = Depends(get_db)):
    """
    Retrieve sensor data with pagination.
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    try:
        data = db.query(SensorData).offset(skip).limit(limit).all()
        return data
    except Exception as e:
        logger.error(f"Error retrieving data: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/aggregated_data/", response_model=List[AggregatedDataModel])
def read_data(skip: int = 0, limit: int = Query(default=100, le=1000), db: Session = Depends(get_db)):
    """
    Retrieve sensor data with pagination.
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    try:
        data = db.query(AggregatedData).offset(skip).limit(limit).all()
        return data
    except Exception as e:
        logger.error(f"Error retrieving data: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/metadata/", response_model=List[MetadataModel])
def read_metadata(db: Session = Depends(get_db)):
    """
    Retrieve metadata for all datasets.
    """
    try:
        metadata = db.query(Metadata).all()
        return metadata
    except Exception as e:
        logger.error(f"Error retrieving metadata: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/data/catalog/")
def read_data_catalog(request: Request):
    """
    Endpoint to serve the data catalog page.
    """
    return templates.TemplateResponse("catalog.html", {"request": request})


@app.get("/data/{sensor_id}", response_model=List[SensorDataModel])
def read_data_by_sensor(sensor_id: int, skip: int = 0, limit: int = Query(default=100, le=1000),
                        db: Session = Depends(get_db)):
    """
    Retrieve sensor data for a specific sensor with pagination.
    - **sensor_id**: ID of the sensor
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    try:
        data = db.query(SensorData).filter(SensorData.sensor_id == sensor_id).offset(skip).limit(limit).all()
        return data
    except Exception as e:
        logger.error(f"Error retrieving data by sensor_id: {sensor_id}, error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/data/summary/", response_model=List[SensorDataModel])
def read_data_summary(
        type: Optional[str] = None,
        unit: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        skip: int = 0,
        limit: int = Query(default=100, le=1000),
        db: Session = Depends(get_db)
):
    """
    Retrieve a summary of sensor data with optional filters.
    - **type**: Type of sensor data (e.g., temperature)
    - **unit**: Unit of measurement
    - **start_time**: Start time for the data query
    - **end_time**: End time for the data query
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    query = db.query(SensorData)

    if type:
        query = query.filter(SensorData.type == type)
    if unit:
        query = query.filter(SensorData.unit == unit)
    if start_time:
        query = query.filter(SensorData.timestamp >= start_time)
    if end_time:
        query = query.filter(SensorData.timestamp <= end_time)

    try:
        data = query.offset(skip).limit(limit).all()
        return data
    except Exception as e:
        logger.error(f"Error retrieving data summary: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/data/range/", response_model=List[SensorDataModel])
def read_data_by_timestamp(
        start_time: datetime,
        end_time: datetime,
        skip: int = 0,
        limit: int = Query(default=100, le=1000),
        db: Session = Depends(get_db)
):
    """
    Retrieve sensor data within a specific time range.
    - **start_time**: Start time for the data query
    - **end_time**: End time for the data query
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    try:
        data = db.query(SensorData).filter(SensorData.timestamp >= start_time, SensorData.timestamp <= end_time).offset(skip).limit(limit).all()
        return data
    except Exception as e:
        logger.error(f"Error retrieving data by timestamp range: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/aggregated_data/{sensor_id}", response_model=List[AggregatedDataModel])
def read_data_by_sensor(sensor_id: int, skip: int = 0, limit: int = Query(default=100, le=1000),
                        db: Session = Depends(get_db)):
    """
    Retrieve sensor data for a specific sensor with pagination.
    - **sensor_id**: ID of the sensor
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    try:
        data = db.query(AggregatedData).filter(AggregatedData.sensor_id == sensor_id).offset(skip).limit(limit).all()
        return data
    except Exception as e:
        logger.error(f"Error retrieving data by sensor_id: {sensor_id}, error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/aggregated_data/summary/", response_model=List[AggregatedDataModel])
def read_data_summary(
        type: Optional[str] = None,
        unit: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        skip: int = 0,
        limit: int = Query(default=100, le=1000),
        db: Session = Depends(get_db)
):
    """
    Retrieve a summary of sensor data with optional filters.
    - **type**: Type of sensor data (e.g., temperature)
    - **unit**: Unit of measurement
    - **start_time**: Start time for the data query
    - **end_time**: End time for the data query
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    query = db.query(AggregatedData)

    if type:
        query = query.filter(AggregatedData.type == type)
    if unit:
        query = query.filter(AggregatedData.unit == unit)
    if start_time:
        query = query.filter(AggregatedData.timestamp >= start_time)
    if end_time:
        query = query.filter(AggregatedData.timestamp <= end_time)

    try:
        data = query.offset(skip).limit(limit).all()
        return data
    except Exception as e:
        logger.error(f"Error retrieving data summary: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/aggregated_data/range/", response_model=List[AggregatedDataModel])
def read_data_by_timestamp(
        start_time: datetime,
        end_time: datetime,
        skip: int = 0,
        limit: int = Query(default=100, le=1000),
        db: Session = Depends(get_db)
):
    """
    Retrieve sensor data within a specific time range.
    - **start_time**: Start time for the data query
    - **end_time**: End time for the data query
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    try:
        data = db.query(AggregatedData).filter(AggregatedData.timestamp >= start_time, AggregatedData.timestamp <= end_time).offset(skip).limit(limit).all()
        return data
    except Exception as e:
        logger.error(f"Error retrieving data by timestamp range: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/data/", response_model=SensorDataModel)
def create_sensor_data(sensor_data: SensorDataModel, db: Session = Depends(get_db)):
    """
    Create a new sensor data entry.
    - **sensor_data**: SensorDataModel containing the sensor data to be added
    """
    db_data = SensorData(**sensor_data.dict())
    try:
        db.add(db_data)
        db.commit()
        db.refresh(db_data)
        logger.info(f"Created new sensor data entry with ID: {db_data.id}")
        return db_data
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating sensor data: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.put("/data/{data_id}", response_model=SensorDataModel)
def update_sensor_data(data_id: int, sensor_data: SensorDataModel, db: Session = Depends(get_db)):
    """
    Update an existing sensor data entry.
    - **data_id**: ID of the data entry to update
    - **sensor_data**: SensorDataModel containing the updated data
    """
    db_data = db.query(SensorData).filter(SensorData.id == data_id).first()
    if db_data is None:
        logger.warning(f"Data with ID: {data_id} not found for update")
        raise HTTPException(status_code=404, detail="Data not found")

    for key, value in sensor_data.dict().items():
        setattr(db_data, key, value)

    try:
        db.commit()
        db.refresh(db_data)
        logger.info(f"Updated sensor data entry with ID: {data_id}")
        return db_data
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating sensor data with ID: {data_id}, error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/data/{data_id}", response_model=SensorDataModel)
def delete_sensor_data(data_id: int, db: Session = Depends(get_db)):
    """
    Delete an existing sensor data entry.
    - **data_id**: ID of the data entry to delete
    """
    db_data = db.query(SensorData).filter(SensorData.id == data_id).first()
    if db_data is None:
        logger.warning(f"Data with ID: {data_id} not found for deletion")
        raise HTTPException(status_code=404, detail="Data not found")

    try:
        db.delete(db_data)
        db.commit()
        logger.info(f"Deleted sensor data entry with ID: {data_id}")
        return db_data
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting sensor data with ID: {data_id}, error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Data quality check functions
def check_completeness(df: pd.DataFrame) -> float:
    total_entries = df.size
    non_null_entries = df.count().sum()
    completeness = (non_null_entries / total_entries) * 100
    return completeness

def check_validity(df: pd.DataFrame) -> float:
    try:
        pd.to_datetime(df['timestamp'])
        return 100.0
    except ValueError:
        return 0.0

def check_accuracy(df: pd.DataFrame) -> float:
    return 100.0

def check_consistency(df: pd.DataFrame) -> float:
    consistent = df['timestamp'].apply(lambda x: isinstance(x, pd.Timestamp)).all()
    return 100.0 if consistent else 0.0

def check_timeliness(df: pd.DataFrame, update_frequency: str) -> float:
    latest_entry = df['timestamp'].max()
    now = pd.Timestamp.now()
    if update_frequency == "daily":
        return 100.0 if (now - latest_entry).days <= 1 else 0.0
    return 0.0

def check_uniqueness(df: pd.DataFrame) -> float:
    total_rows = len(df)
    unique_rows = len(df.drop_duplicates())
    uniqueness = (unique_rows / total_rows) * 100
    return uniqueness

# Data quality check endpoint
@app.get("/data/data-quality/")
def data_quality_check(db: Session = Depends(get_db)):
    try:
        sensor_data_df = get_dataframe_from_table(db, SensorData)
        #aggregated_sensor_data_df = get_dataframe_from_table(db, AggregatedSensorData)

        results = {
            "sensor_data": {
                "completeness": check_completeness(sensor_data_df),
                "validity": check_validity(sensor_data_df),
                "accuracy": check_accuracy(sensor_data_df),
                "consistency": check_consistency(sensor_data_df),
                "timeliness": check_timeliness(sensor_data_df, "daily"),
                "uniqueness": check_uniqueness(sensor_data_df),
            }
        }

        return {"status": "Check completed", "results": results}
    except Exception as e:
        logger.error(f"Error performing data quality checks: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

from sqlalchemy import text

def get_dataframe_from_table(db: Session, table):
    query = text(f"SELECT * FROM {table.__tablename__}")
    df = pd.read_sql(query, db.bind)
    return df


app.include_router(router)