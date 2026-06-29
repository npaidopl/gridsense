# api/routers/cache.py
from fastapi import APIRouter, HTTPException
import json
from models.schemas import TransformerStatusCache
from db.redis import db_redis

router = APIRouter(prefix="/cache", tags=["In-MemoryCache"])

@router.post("/transformer")
async def cache_transformer_status(status: TransformerStatusCache):
    try:
        redis_client = db_redis.get_client()
        
        cache_key = f"transformer:status:{status.asset_id}"
        payload = json.dumps(status.dict())
        
        # Set string value with an automatic 300-second (5-minute) expiration TTL window
        await redis_client.set(cache_key, payload, ex=300)
        return {"status": "success", "message": f"Transformer state cached with 300s TTL horizon."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transformer/{asset_id}")
async def get_cached_transformer_status(asset_id: str):
    try:
        redis_client = db_redis.get_client()
        cache_key = f"transformer:status:{asset_id}"
        
        cached_data = await redis_client.get(cache_key)
        if not cached_data:
            raise HTTPException(status_code=404, detail="Cache entry expired or non-existent.")
            
        return json.loads(cached_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))