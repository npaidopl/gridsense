-- cql/init.cql
CREATE KEYSPACE IF NOT EXISTS gridsense
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

USE gridsense;

-- Table 1: Optimized for query pattern (1) - readings per sensor over time (90-day TTL)
CREATE TABLE IF NOT EXISTS sensor_readings (
    sensor_id TEXT,
    reading_time TIMESTAMP,
    metric_type TEXT, -- 'voltage', 'current', 'power_factor', 'temp'
    value FLOAT,
    unit TEXT,
    quality_flag TINYINT, -- 0=good, 1=suspect, 2=bad
    PRIMARY KEY ((sensor_id), reading_time)
) WITH CLUSTERING ORDER BY (reading_time DESC)
AND default_time_to_live = 7776000;

-- Table 2: Relay operation log — append-only, causal order preserved via TIMEUUID
CREATE TABLE IF NOT EXISTS relay_events (
    feeder_id TEXT,
    event_time TIMEUUID, -- TIMEUUID embeds causal timestamp and uniqueness
    relay_id TEXT,
    event_type TEXT, -- 'TRIP', 'RECLOSE', 'LOCKOUT'
    fault_type TEXT,
    current_kA FLOAT,
    PRIMARY KEY ((feeder_id), event_time)
) WITH CLUSTERING ORDER BY (event_time ASC);

-- Table 3: Custom table optimized for query pattern (2) - Cross-network dashboard analytics
-- This table groups all sensors by a coarse time bucket (truncated to the minute) 
-- allowing the system to fetch the entire network's performance in a single partition read.
CREATE TABLE IF NOT EXISTS sensor_readings_by_minute (
    minute_bucket TIMESTAMP, -- e.g., '2026-06-27 15:50:00'
    reading_time TIMESTAMP,
    sensor_id TEXT,
    metric_type TEXT,
    value FLOAT,
    quality_flag TINYINT,
    PRIMARY KEY ((minute_bucket), reading_time, sensor_id)
) WITH CLUSTERING ORDER BY (reading_time DESC, sensor_id ASC)
AND default_time_to_live = 7776000;
