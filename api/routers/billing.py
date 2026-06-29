# api/routers/billing.py
from fastapi import APIRouter, HTTPException
from models.schemas import BillingRecordCreate
from db.postgres import db_postgres

router = APIRouter(prefix="/billing", tags=["RelationalBilling"])

@router.post("/record")
async def emit_billing_record(record: BillingRecordCreate):
    try:
        pool = db_postgres.get_pool()
        
        # Open a secure database connection from our pre-allocated asyncpg pool
        async with pool.acquire() as connection:
            # Use a strict transaction block to guarantee atomic consistency
            async with connection.transaction():
                query = """
                    INSERT INTO consumer_billing (premise_id, billing_period_start, billing_period_end, total_kwh_consumed, tariff_rate_applied, total_amount_due)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """
                await connection.execute(
                    query,
                    record.premise_id,
                    record.billing_period_start,
                    record.billing_period_end,
                    record.total_kwh_consumed,
                    record.tariff_rate_applied,
                    record.total_amount_due
                )
        return {"status": "success", "message": "ACID transactional billing record logged seamlessly."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/premise/{premise_id}")
async def get_premise_history(premise_id: str):
    try:
        pool = db_postgres.get_pool()
        async with pool.acquire() as connection:
            query = "SELECT * FROM consumer_billing WHERE premise_id = $1 ORDER BY billing_period_end DESC"
            rows = await connection.fetch(query, premise_id)
            
            return [dict(r) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))