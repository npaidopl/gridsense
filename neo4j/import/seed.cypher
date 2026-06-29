// neo4j/import/seed.cypher

// ── Constraints ───────────────────────────────────────────────────
CREATE CONSTRAINT substation_id IF NOT EXISTS
FOR (s:Substation) REQUIRE s.substation_id IS UNIQUE;

CREATE CONSTRAINT transformer_id IF NOT EXISTS
FOR (t:Transformer) REQUIRE t.asset_id IS UNIQUE;

CREATE CONSTRAINT meter_id IF NOT EXISTS
FOR (m:SmartMeter) REQUIRE m.meter_id IS UNIQUE;

// ── Nodes ────────────────────────────────────────────────────────
// Grid Supply Point (Top of physical distribution tree)
MERGE (g:GridSupplyPoint { gsp_id: "GSP_NORTH" })
ON CREATE SET g.name = "Northern Grid Supply Point",
              g.voltage_kV = 132,
              g.region = "North Metro";

// Substation
MERGE (s:Substation { substation_id: "SS_001" })
ON CREATE SET s.name = "Volos Primary",
              s.voltage_kV = 11,
              s.lat = 39.358,
              s.lon = 22.938,
              s.commissioned_year = 1998;

// Distribution Transformer
MERGE (t:Transformer { asset_id: "TX_001_A" })
ON CREATE SET t.rating_kVA = 400,
              t.manufacturer = "ABB",
              t.model = "ONAN-400",
              t.installed = date("2012-06-15"),
              t.last_inspection = date("2024-09-01");

// Smart Meters
MERGE (m1:SmartMeter { meter_id: "SM_00001" })
ON CREATE SET m1.premise_id = "PREM_10001",
              m1.tariff_class = "residential",
              m1.phase = "single";

MERGE (m2:SmartMeter { meter_id: "SM_00002" })
ON CREATE SET m2.premise_id = "PREM_10002",
              m2.tariff_class = "residential",
              m2.phase = "single";

MERGE (m3:SmartMeter { meter_id: "SM_00003" })
ON CREATE SET m3.premise_id = "PREM_10003",
              m3.tariff_class = "commercial",
              m3.phase = "three";

// ── Relationships ────────────────────────────────────────────────
MATCH (g:GridSupplyPoint { gsp_id: "GSP_NORTH" })
MATCH (s:Substation { substation_id: "SS_001" })
MERGE (g)-[r:FEEDS]->(s)
ON CREATE SET r.feeder_id = "F_001", r.voltage_kV = 11, r.length_km = 2.4;

MATCH (s:Substation { substation_id: "SS_001" })
MATCH (t:Transformer { asset_id: "TX_001_A" })
MERGE (s)-[r:SUPPLIES]->(t)
ON CREATE SET r.cable_id = "CB_001", r.distance_m = 320;

MATCH (t:Transformer { asset_id: "TX_001_A" })
MATCH (m1:SmartMeter { meter_id: "SM_00001" })
MERGE (t)-[:CONNECTS_TO]->(m1);

MATCH (t:Transformer { asset_id: "TX_001_A" })
MATCH (m2:SmartMeter { meter_id: "SM_00002" })
MERGE (t)-[:CONNECTS_TO]->(m2);

MATCH (t:Transformer { asset_id: "TX_001_A" })
MATCH (m3:SmartMeter { meter_id: "SM_00003" })
MERGE (t)-[:CONNECTS_TO]->(m3);
