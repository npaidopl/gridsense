# api/scripts/seed.py
import os
import sys
import asyncio
from datetime import datetime

# Adjust module path lookup for Docker runtime execution context
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.postgres import db_postgres
from db.neo4j import db_neo4j
from db.mongo import db_mongo

async def seed_postgres():
    print("[SEEDER] Checking Relational Billing Database...")
    await db_postgres.connect()
    pool = db_postgres.get_pool()
    async with pool.acquire() as conn:
        # Idempotently create the table structure if it didn't provision
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS consumer_billing (
                id SERIAL PRIMARY KEY,
                premise_id VARCHAR(50) NOT NULL,
                billing_period_start TIMESTAMP NOT NULL,
                billing_period_end TIMESTAMP NOT NULL,
                total_kwh_consumed NOT NULL,
                tariff_rate_applied FLOAT NOT NULL,
                total_amount_due FLOAT NOT NULL
            );
        """)
        # Ensure it's idempotent by checking counts before pushing duplicates
        count = await conn.fetchval("SELECT COUNT(*) FROM consumer_billing;")
        if count == 0:
            await conn.execute("""
                INSERT INTO consumer_billing (premise_id, billing_period_start, billing_period_end, total_kwh_consumed, tariff_rate_applied, total_amount_due)
                VALUES ('PREM_10001', '2026-05-01', '2026-05-31', 350.5, 0.15, 52.58);
            """)
            print("[SEEDER] Postgres billing records seeded.")
    await db_postgres.disconnect()

async def seed_neo4j():
    print("[SEEDER] Connecting to Graph Network Topologies...")
    db_neo4j.connect()
    driver = db_neo4j.get_driver()
    
    # Updated to follow Rule 2: common node_id applied everywhere uniform
    cypher_script = """
    CREATE CONSTRAINT node_id_unq IF NOT EXISTS FOR (n:Substation) REQUIRE n.node_id IS UNIQUE;
    CREATE CONSTRAINT trans_id_unq IF NOT EXISTS FOR (t:Transformer) REQUIRE t.node_id IS UNIQUE;
    CREATE CONSTRAINT meter_id_unq IF NOT EXISTS FOR (m:SmartMeter) REQUIRE m.node_id IS UNIQUE;

    MERGE (s:Substation {node_id: "SS_001", substation_id: "SS_001"})
    ON CREATE SET s.name = "Volos Primary", s.voltage_kV = 11;

    MERGE (t:Transformer {node_id: "TX_001_A", asset_id: "TX_001_A"})
    ON CREATE SET t.rating_kVA = 400;

    MERGE (m1:SmartMeter {node_id: "SM_00001", meter_id: "SM_00001"})
    ON CREATE SET m1.premise_id = "PREM_10001";
    MERGE (m2:SmartMeter {node_id: "SM_00002", meter_id: "SM_00002"})
    ON CREATE SET m2.premise_id = "PREM_10002";

    MATCH (s:Substation {node_id: "SS_001"}), (t:Transformer {node_id: "TX_001_A"})
    MERGE (s)-[:SUPPLIES]->(t);

    MATCH (t:Transformer {node_id: "TX_001_A"}), (m1:SmartMeter {node_id: "SM_00001"})
    MERGE (t)-[:CONNECTS_TO]->(m1);

    MATCH (t:Transformer {node_id: "TX_001_A"}), (m2:SmartMeter {node_id: "SM_00002"})
    MERGE (t)-[:CONNECTS_TO]->(m2);
    """
    async with driver.session() as session:
        # Run statements sequentially
        for statement in [s.strip() for s in cypher_script.split(";") if s.strip()]:
            await session.run(statement)
    print("[SEEDER] Neo4j structural network elements seeded securely.")
    await db_neo4j.disconnect()

async def seed_mongodb():
    print("[SEEDER] Initializing Mongo Document Catalog Assets...")
    db_mongo.connect()
    db = db_mongo.get_db()
    collection = db["meter_specifications"]
    
    # Rule 2 separation: high flexibility metadata goes directly to MongoDB
    mock_catalog = [
        {
            "meter_id": "SM_00001",
            "manufacturer": "ABB Grid Corp",
            "model_number": "Alpha-X1",
            "installation_date": datetime.utcnow().isoformat(),
            "specifications": {
                "firmware_version": "v4.12",
                "hardware_revision": "revB",
                "mac_address": "00:25:96:FF:FE:12:34:56",
                "communication_protocol": "NB-IoT"
            },
            "custom_metadata": {"feeder_zone": "Alpha-North", "transformer_coupling": "TX_001_A"}
        }
    ]
    for asset in mock_catalog:
        await collection.update_one({"meter_id": asset["meter_id"]}, {"$set": asset}, upsert=True)
    print("[SEEDER] MongoDB asset document tracking online.")
    db_mongo.disconnect()

async def main():
    print("[SEEDER ENGINE STARTING] Executing unified environment orchestration mapping...")
    await seed_postgres()
    await seed_neo4j()
    await seed_mongodb()
    print("[SEEDER ENGINE FINISHED] Pipeline complete. Exiting clean.")

if __name__ == "__main__":
    asyncio.run(main())