"""
History Routes - Historial de transacciones
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.persistence_service import PersistenceService
from app.security import verify_api_key_and_jwt
from fastapi import HTTPException

router = APIRouter()


@router.get(
    "/transactions",
    summary="Obtener historial de transacciones",
    dependencies=[Depends(verify_api_key_and_jwt)]
)
async def get_transaction_history(
    customer_id: str = None,
    decision: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial de transacciones analizadas
    
    Query params:
    - customer_id: Filtrar por cliente (opcional)
    - decision: Filtrar por tipo de decisión: APPROVE, CHALLENGE, BLOCK, ESCALATE_TO_HUMAN (opcional)
    - limit: Número máximo de resultados (default: 100)
    """
    history = PersistenceService.get_transaction_history(
        db=db,
        customer_id=customer_id,
        decision=decision,
        limit=limit
    )
    
    return {
        "total": len(history),
        "filters": {
            "customer_id": customer_id,
            "decision": decision,
            "limit": limit
        },
        "transactions": history
    }


@router.get(
    "/statistics",
    summary="Obtener estadísticas generales",
    dependencies=[Depends(verify_api_key_and_jwt)]
)
async def get_statistics(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas generales del sistema
    """
    stats = PersistenceService.get_statistics(db=db)
    return stats

@router.get(
    "/transactions/{transaction_id}",
    summary="Obtener detalles completos de una transacción",
    dependencies=[Depends(verify_api_key_and_jwt)]
)
async def get_transaction_details(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los detalles de una transacción incluyendo logs de análisis
    
    Path params:
    - transaction_id: ID de la transacción
    
    Returns:
        Información completa de la transacción con logs
    """
    details = PersistenceService.get_transaction_details(db, transaction_id)
    
    if not details:
        raise HTTPException(
            status_code=404,
            detail=f"Transacción {transaction_id} no encontrada"
        )
    
    return details