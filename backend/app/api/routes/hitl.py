"""
HITL Routes - Human-in-the-Loop
Endpoints para gestionar la cola de revisión manual
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    HITLCase,
    HITLCaseResponse,
    HITLReviewRequest,
    HITLStatus, 
    DecisionType,
    HITLReviewResponse
)
from app.services.hitl_service import get_hitl_service
from typing import List
from fastapi import Depends
from app.security import verify_api_key_and_jwt, get_current_user


router = APIRouter()
hitl_service = get_hitl_service()


@router.get(
    "/pending",
    summary="Obtener casos pendientes de revisión",
    dependencies=[Depends(verify_api_key_and_jwt)]
)
async def get_pending_cases():
    """
    Obtener todos los casos HITL pendientes de revisión con información completa
    """
    try:
        hitl_service = get_hitl_service()
        cases = hitl_service.get_pending_cases()
        
        # Enriquecer cada caso con información de maestros
        enriched_cases = []
        for case in cases:
            case_data = _enrich_case_summary(case)
            enriched_cases.append(case_data)
        
        return enriched_cases
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener casos pendientes: {str(e)}")


@router.get(
    "/cases",
    summary="Obtener todos los casos HITL",
    dependencies=[Depends(verify_api_key_and_jwt)]
)
async def get_all_cases(status: HITLStatus = None):
    """
    Obtener todos los casos HITL, opcionalmente filtrados por estado
    
    Query params:
    - status: PENDING, APPROVED, REJECTED, IN_REVIEW (opcional)
    """
    try:
        hitl_service = get_hitl_service()
        cases = hitl_service.get_all_cases(status)
        
        # Enriquecer cada caso con información de maestros
        enriched_cases = []
        for case in cases:
            case_data = _enrich_case_summary(case)
            enriched_cases.append(case_data)
        
        return enriched_cases
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener casos: {str(e)}")


@router.get(
    "/cases/{case_id}",
    summary="Obtener un caso específico (completo)",
    dependencies=[Depends(verify_api_key_and_jwt)]
)
async def get_case(case_id: str):
    """
    Obtener detalles COMPLETOS de un caso HITL específico
    """
    try:
        hitl_service = get_hitl_service()
        case = hitl_service.get_case(case_id)
        
        if not case:
            raise HTTPException(status_code=404, detail=f"Caso {case_id} no encontrado")
        
        # Retornar versión completa (detallada)
        return _enrich_case_full(case)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener caso: {str(e)}")


@router.post(
    "/cases/{case_id}/review",
    summary="Revisar y resolver un caso",
    dependencies=[Depends(verify_api_key_and_jwt)]
)
async def review_case(
    case_id: str,
    review: HITLReviewRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Revisar un caso HITL y tomar una decisión final
    """
    try:
        hitl_service = get_hitl_service()
        
        # Usar el username del usuario autenticado
        case = hitl_service.review_case(
            case_id=case_id,
            reviewer_id=current_user["username"],
            decision=DecisionType[review.decision],
            notes=review.notes
        )
        
        if not case:
            raise HTTPException(status_code=404, detail=f"Caso {case_id} no encontrado")
        
        return {
            "case_id": case.case_id,
            "status": case.status.value,
            "reviewer_id": case.reviewer_id,
            "reviewer_decision": case.reviewer_decision.value if case.reviewer_decision else None,
            "reviewer_notes": case.reviewer_notes,
            "reviewed_at": case.reviewed_at,
            "success": True,
            "message": f"Caso {case_id} revisado exitosamente por {current_user['nombre_usuario']}"
        }
    
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al revisar caso: {str(e)}")


@router.get(
    "/statistics",
    summary="Obtener estadísticas de la cola HITL",
        dependencies=[Depends(verify_api_key_and_jwt)]  # ← API KEY + JWT 
)
async def get_statistics():
    """
    Obtiene estadísticas sobre la cola de revisión manual
    """
    stats = hitl_service.get_statistics()
    return stats



def _enrich_case_full(case) -> dict:
    """
    Detalles completos del caso (para vista individual)
    
    Args:
        case: HITLCase object
    
    Returns:
        Dict con información completa del caso
    """
    return {
        # DATOS DEL CASO (RAÍZ)
        "case_id": case.case_id,
        "decision_recommendation": case.decision_recommendation.value,
        "confidence": case.confidence,
        "status": case.status.value,
        "created_at": case.created_at,
        "created_by": case.created_by,
        "reviewer_id": case.reviewer_id,
        "reviewer_decision": case.reviewer_decision.value if case.reviewer_decision else None,
        "reviewer_notes": case.reviewer_notes,
        "reviewed_at": case.reviewed_at,
        
        # DATOS DE LA TRANSACCIÓN (OBJETO COMPLETO)
        "transaction": {
            # Datos básicos de la transacción
            "transaction_id": case.transaction.transaction_id,
            "amount": case.transaction.amount,
            "currency": case.transaction.currency,
            "device_id": case.transaction.device_id,
            "timestamp": case.transaction.timestamp.isoformat() if hasattr(case.transaction.timestamp, 'isoformat') else case.transaction.timestamp,
            
            # Información del cliente (completa)
            "customer": case._customer if hasattr(case, '_customer') else {
                "customer_id": case.transaction.customer_id
            },
            
            # Información del país
            "country": case._country if hasattr(case, '_country') else {
                "code": case.transaction.country
            },
            
            # Información del canal
            "channel": case._channel if hasattr(case, '_channel') else {
                "code": case.transaction.channel
            },
            
            # Información del comercio
            "merchant": case._merchant if hasattr(case, '_merchant') else {
                "merchant_id": case.transaction.merchant_id
            },
            
            # Señales detectadas
            "signals": case.signals,
            
            # Citaciones internas (políticas)
            "citations_internal": [
                {
                    "policy_id": c.policy_id,
                    "version": c.version,
                    "chunk_id": c.chunk_id
                }
                for c in case.citations_internal
            ],
            
            # Citaciones externas (fuentes)
            "citations_external": [
                {
                    "url": c.url,
                    "summary": c.summary
                }
                for c in case.citations_external
            ],
            
            # Ruta de agentes
            "agent_route": case.agent_route
        }
    }

def _enrich_case_summary(case) -> dict:
    """
    Resumen ligero del caso para listas (solo info esencial)
    
    Args:
        case: HITLCase object
    
    Returns:
        Dict con información resumida del caso
    """
    return {
        # Datos del caso
        "case_id": case.case_id,
        "decision_recommendation": case.decision_recommendation.value,
        "confidence": case.confidence,
        "status": case.status.value,
        "created_at": case.created_at,
        "created_by": case.created_by,

        "reviewer_id": case.reviewer_id,
        "reviewer_notes": case.reviewer_notes,
        "reviewer_decision": case.reviewer_decision.value if case.reviewer_decision else None,
        "reviewed_at": case.reviewed_at,
        
        # Datos básicos de la transacción
        "transaction": {
            "transaction_id": case.transaction.transaction_id,
            "amount": case.transaction.amount,
            "currency": case.transaction.currency,
            "timestamp": case.transaction.timestamp.isoformat() if hasattr(case.transaction.timestamp, 'isoformat') else case.transaction.timestamp,
            
            # Solo info del cliente (para identificar)
            "customer": case._customer if hasattr(case, '_customer') else {
                "customer_id": case.transaction.customer_id
            }
        }
    }