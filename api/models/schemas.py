# api/models/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# ??? CASSANDRA: TIME-SERIES READINGS & RELAY EVENTS ???????????????????

class SensorReadingCreate(BaseModel):
    sensor_id: str = Field(..., description="Unique alphanumeric identifier of the smart sensor")
    reading_time: datetime = Field(..., description="Timestamp of the physical telemetry capture")
    metric_type: str = Field(..., description="Type of metric being recorded (voltage, current, power_factor, temp)")
    value: float = Field(..., description="Float value of the metric reading")
    unit: str = Field(..., description="Measurement units (e.g., V, A, kW)")
    quality_flag: int = Field(..., ge=0, le=2, description="Data validation quality: 0=good, 1=suspect, 2=bad")

class RelayEventCreate(BaseModel):
    feeder_id: str = Field(..., description="Identifier for the circuit feeder segment")
    relay_id: str = Field(..., description="Unique protection relay machine ID")
    event_type: str = Field(..., description="Type of action triggered: TRIP, RECLOSE, LOCKOUT")
    fault_type: str = Field(..., description="Fault nature: Overcurrent, Earth Fault, Phase Lock")
    current_kA: float = Field(..., description="Fault current recorded in kilo-amperes")

# ??? NEO4J: GRAPH TOPOLOGY & FAULT DIAGNOSIS ?????????????????????????

class TopologyPathStep(BaseModel):
    node_id: str
    node_label: str
    properties: Dict[str, Any]

class FaultDiagnosisResponse(BaseModel):
    fault_origin_node: str
    impact_depth: int
    diagnosed_at: datetime
    traversed_path_nodes: List[str] = Field(default_factory=list)
    downstream_meters_affected: List[str] = Field(default_factory=list)
    message: str

# ??? MONGODB: SMART METER ASSET CATALOG ??????????????????????????????

class HardwareSpecifications(BaseModel):
    firmware_version: str
    hardware_revision: str
    mac_address: str
    communication_protocol: str  # Zigbee, Cellular, NB-IoT

class AssetCatalogCreate(BaseModel):
    meter_id: str = Field(..., description="Unique alphanumeric identifier matching the topology node")
    manufacturer: str
    model_number: str
    installation_date: datetime
    specifications: HardwareSpecifications
    custom_metadata: Dict[str, Any] = Field(default_factory=dict, description="Flexible schema-agnostic custom attributes")

# ??? REDIS: VOLATILE CACHE MODELS ????????????????????????????????????

class TransformerStatusCache(BaseModel):
    asset_id: str
    current_load_percentage: float
    temperature_celsius: float
    status: str  # NORMAL, WARNING, CRITICAL
    updated_at: str

# ??? POSTGRESQL: CONSUMER BILLING ????????????????????????????????????

class BillingRecordCreate(BaseModel):
    premise_id: str = Field(..., description="Unique premise location reference link")
    billing_period_start: datetime
    billing_period_end: datetime
    total_kwh_consumed: float
    tariff_rate_applied: float
    total_amount_due: float