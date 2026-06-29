# api/routers/topology.py
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from models.schemas import FaultDiagnosisResponse
from db.neo4j import db_neo4j

router = APIRouter(prefix="/topology", tags=["GraphTopology"])

@router.get("/diagnose/{substation_id}", response_model=FaultDiagnosisResponse)
async def diagnose_fault(substation_id: str, max_depth: int = Query(6, ge=1, le=10)):
    driver = db_neo4j.get_driver()
    
    # Rule 3 Execution: Variable length path string interpolation safely validated via Pydantic integer limits
    cypher_query = f"""
    MATCH (s:Substation {{node_id: $substation_id}})
    OPTIONAL MATCH path = (s)-[:SUPPLIES|CONNECTS_TO*1..{max_depth}]->(downstream)
    WITH s, collect(distinct downstream) as downstream_nodes
    RETURN 
        s.node_id as origin,
        size(downstream_nodes) as impact_count,
        [n in downstream_nodes WHERE "SmartMeter" in labels(n) | n.node_id] as affected_meters,
        [n in downstream_nodes WHERE "Transformer" in labels(n) | n.node_id] as affected_assets
    """
    
    try:
        async with driver.session() as session:
            result = await session.run(cypher_query, substation_id=substation_id)
            record = await result.single()
            
            if not record:
                raise HTTPException(status_code=404, detail="Substation node not found in topology graph cluster.")
                
            return FaultDiagnosisResponse(
                fault_origin_node=record["origin"],
                impact_depth=max_depth,
                diagnosed_at=datetime.utcnow(),
                traversed_path_nodes=[str(asset) for asset in record["affected_assets"] if asset],
                downstream_meters_affected=record["affected_meters"],
                message=f"Root cause simulation across depth window {max_depth} processed successfully."
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))