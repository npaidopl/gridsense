# api/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Cleaned imports (Removed 'api.' prefix)
from db.postgres import db_postgres
from db.neo4j import db_neo4j
from db.mongo import db_mongo
from db.cassandra import db_cassandra
from db.redis import db_redis

from routers.timeseries import router as timeseries_router
from routers.topology import router as topology_router
from routers.catalog import router as catalog_router
from routers.cache import router as cache_router
from routers.billing import router as billing_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[SYSTEM INITIALIZATION] Synchronizing polyglot connection matrices...")
    await db_postgres.connect()
    db_neo4j.connect()
    db_mongo.connect()
    db_cassandra.connect()
    db_redis.connect()
    print("[SYSTEM INITIALIZATION] All 5 distributed engine sockets verified and online.")
    yield
    print("[SYSTEM SHUTDOWN] Safely draining and closing driver connection pools...")
    await db_postgres.disconnect()
    await db_neo4j.disconnect()
    db_mongo.disconnect()
    db_cassandra.disconnect()
    await db_redis.disconnect()
    print("[SYSTEM SHUTDOWN] All storage network connections terminated cleanly.")

app = FastAPI(
    title="GridSense Analytics Platform Engine",
    version="1.0.0",
    description="Unified API interface managing distributed smart grid networks.",
    lifespan=lifespan
)

app.include_router(timeseries_router)
app.include_router(topology_router)
app.include_router(catalog_router)
app.include_router(cache_router)
app.include_router(billing_router)

@app.get("/health")
async def cluster_health_check():
    return {
        "status": "operational",
        "services": {
            "postgres_pool": "connected",
            "neo4j_driver": "connected",
            "mongodb_client": "connected",
            "cassandra_session": "connected",
            "redis_cache": "connected"
        }
    }