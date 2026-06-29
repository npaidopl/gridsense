# api/routers/catalog.py
from fastapi import APIRouter, HTTPException
from models.schemas import AssetCatalogCreate
from db.mongo import db_mongo

router = APIRouter(prefix="/catalog", tags=["AssetCatalog"])

@router.post("/meter")
async def register_meter_metadata(asset: AssetCatalogCreate):
    try:
        db = db_mongo.get_db()
        collection = db["meter_specifications"]
        
        document = asset.dict()
        # Convert datetime objects to string representations safe for native BSON serialization
        document["installation_date"] = document["installation_date"].isoformat()
        
        # Upsert operation to update existing device data cleanly without duplication
        await collection.update_one(
            {"meter_id": asset.meter_id},
            {"$set": document},
            upsert=True
        )
        return {"status": "success", "message": f"Hardware metrics registered for node {asset.meter_id}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/meter/{meter_id}")
async def get_meter_metadata(meter_id: str):
    try:
        db = db_mongo.get_db()
        collection = db["meter_specifications"]
        
        asset = await collection.find_one({"meter_id": meter_id}, {"_id": 0})
        if not asset:
            raise HTTPException(status_code=404, detail="Asset profile matching id not registered.")
        return asset
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))