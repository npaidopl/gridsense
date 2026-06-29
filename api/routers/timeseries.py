# api/routers/timeseries.py
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import uuid
from models.schemas import SensorReadingCreate, RelayEventCreate
from db.cassandra import db_cassandra

router = APIRouter(prefix="/timeseries", tags=["TimeSeries"])

@router.post("/reading")
async def create_sensor_reading(reading: SensorReadingCreate):
    try:
        session = db_cassandra.get_session()
        
        # 1. Insert into the main sensor-indexed table (Pattern 1)
        insert_main = session.prepare("""
            INSERT INTO sensor_readings (sensor_id, reading_time, metric_type, value, unit, quality_flag)
            VALUES (?, ?, ?, ?, ?, ?)
        """)
        session.execute(insert_main, (
            reading.sensor_id, reading.reading_time, reading.metric_type,
            reading.value, reading.unit, reading.quality_flag
        ))
        
        # 2. Insert into the minute-bucketed table (Pattern 2) to prevent scatter-gather scans
        minute_bucket = reading.reading_time.replace(second=0, microsecond=0)
        insert_bucket = session.prepare("""
            INSERT INTO sensor_readings_by_minute (minute_bucket, reading_time, sensor_id, metric_type, value, quality_flag)
            VALUES (?, ?, ?, ?, ?, ?)
        """)
        session.execute(insert_bucket, (
            minute_bucket, reading.reading_time, reading.sensor_id,
            reading.metric_type, reading.value, reading.quality_flag
        ))
        
        return {"status": "success", "message": "Telemetry written to time-series storage matrices successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sensor/{sensor_id}")
async def get_sensor_history(sensor_id: str, limit: int = Query(100, ge=1, le=1000)):
    try:
        session = db_cassandra.get_session()
        query = "SELECT * FROM sensor_readings WHERE sensor_id = %s LIMIT %s"
        rows = session.execute(query, (sensor_id, limit))
        
        results = []
        for r in rows:
            results.append({
                "sensor_id": r.sensor_id,
                "reading_time": r.reading_time,
                "metric_type": r.metric_type,
                "value": r.value,
                "unit": r.unit,
                "quality_flag": r.quality_flag
            })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/relay-event")
async def create_relay_event(event: RelayEventCreate):
    try:
        session = db_cassandra.get_session()
        # Generate a time-based UUID (Version 1 UUID) to ensure causal alignment
        event_uuid = uuid.uuid1()
        
        insert_stmt = session.prepare("""
            INSERT INTO relay_events (feeder_id, event_time, relay_id, event_type, fault_type, current_kA)
            VALUES (?, ?, ?, ?, ?, ?)
        """)
        session.execute(insert_stmt, (
            event.feeder_id, event_uuid, event.relay_id,
            event.event_type, event.fault_type, event.current_kA
        ))
        return {"status": "success", "event_id": str(event_uuid)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))