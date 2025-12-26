"""
Modelos de datos base con Pydantic
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============================================
# ENUMS
# ============================================

class DecisionType(str, Enum):
    """Tipos de decisión posibles"""
    APPROVE = "APPROVE"
    CHALLENGE = "CHALLENGE"
    BLOCK = "BLOCK"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"


class Channel(str, Enum):
    """Canales de transacción"""
    WEB = "web"
    MOBILE = "mobile"
    ATM = "atm"
    BRANCH = "branch"


# ============================================
# TRANSACTION MODELS
# ============================================

class Transaction(BaseModel):
    """Modelo de transacción"""
    transaction_id: str = Field(..., description="ID único de la transacción")
    customer_id: str = Field(..., description="ID del cliente")
    amount: float = Field(..., gt=0, description="Monto de la transacción")
    currency: str = Field(default="PEN", description="Moneda")
    country: str = Field(..., description="País de la transacción")
    channel: Channel = Field(..., description="Canal de la transacción")
    device_id: str = Field(..., description="ID del dispositivo")
    timestamp: datetime = Field(..., description="Fecha y hora de la transacción")
    merchant_id: str = Field(..., description="ID del comercio")
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "T-1001",
                "customer_id": "CU-001",
                "amount": 1800.00,
                "currency": "PEN",
                "country": "PE",
                "channel": "web",
                "device_id": "D-01",
                "timestamp": "2025-12-17T03:15:00",
                "merchant_id": "M-001"
            }
        }


# ============================================
# CUSTOMER MODELS
# ============================================

class CustomerBehavior(BaseModel):
    """Modelo de comportamiento del cliente"""
    customer_id: str = Field(..., description="ID del cliente")
    usual_amount_avg: float = Field(..., description="Monto promedio habitual")
    usual_hours: str = Field(..., description="Horario habitual (ej: 08-20)")
    usual_countries: str = Field(..., description="Países habituales")
    usual_devices: str = Field(..., description="Dispositivos habituales")
    
    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "CU-001",
                "usual_amount_avg": 500.00,
                "usual_hours": "08-20",
                "usual_countries": "PE",
                "usual_devices": "D-01"
            }
        }


# ============================================
# FRAUD POLICY MODELS
# ============================================

class FraudPolicy(BaseModel):
    """Modelo de política de fraude"""
    policy_id: str = Field(..., description="ID de la política")
    rule: str = Field(..., description="Descripción de la regla")
    version: str = Field(..., description="Versión de la política")
    
    class Config:
        json_schema_extra = {
            "example": {
                "policy_id": "FP-01",
                "rule": "Monto > 3x promedio habitual y horario fuera de rango → CHALLENGE",
                "version": "2025.1"
            }
        }


# ============================================
# EVIDENCE & CITATION MODELS
# ============================================

class InternalCitation(BaseModel):
    """Citación de política interna"""
    policy_id: str
    chunk_id: str
    version: str


class ExternalCitation(BaseModel):
    """Citación de fuente externa"""
    url: str
    summary: str


# ============================================
# DECISION MODELS
# ============================================

class DecisionResponse(BaseModel):
    """Respuesta de decisión del sistema"""
    transaction_id: str
    decision: DecisionType
    confidence: float = Field(..., ge=0.0, le=1.0, description="Nivel de confianza (0-1)")
    signals: List[str] = Field(default_factory=list, description="Señales detectadas")
    citations_internal: List[InternalCitation] = Field(default_factory=list)
    citations_external: List[ExternalCitation] = Field(default_factory=list)
    explanation_customer: str = Field(..., description="Explicación para el cliente")
    explanation_audit: str = Field(..., description="Explicación para auditoría")
    agent_route: Optional[str] = Field(None, description="Ruta de agentes seguida")
    processing_time_ms: Optional[float] = Field(None, description="Tiempo de procesamiento")
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "T-1002",
                "decision": "CHALLENGE",
                "confidence": 0.65,
                "signals": ["Monto fuera de rango", "Horario no habitual", "Alerta externa"],
                "citations_internal": [
                    {
                        "policy_id": "FP-01",
                        "chunk_id": "1",
                        "version": "2025.1"
                    }
                ],
                "citations_external": [
                    {
                        "url": "https://example.com/fraud-alert",
                        "summary": "Alerta de fraude reciente en el merchant"
                    }
                ],
                "explanation_customer": "La transacción requiere validación adicional por monto y horario inusual.",
                "explanation_audit": "Se aplicó la política FP-01 y se detectó alerta externa. Ruta de agentes: Context → RAG → Web → Debate → Decisión."
            }
        }


# ============================================
# REQUEST MODELS
# ============================================

class TransactionAnalysisRequest(BaseModel):
    """Request para analizar una transacción"""
    transaction: Transaction
    customer_behavior: Optional[CustomerBehavior] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction": {
                    "transaction_id": "T-1001",
                    "customer_id": "CU-001",
                    "amount": 1800.00,
                    "currency": "PEN",
                    "country": "PE",
                    "channel": "web",
                    "device_id": "D-01",
                    "timestamp": "2025-12-17T03:15:00",
                    "merchant_id": "M-001"
                },
                "customer_behavior": {
                    "customer_id": "CU-001",
                    "usual_amount_avg": 500.00,
                    "usual_hours": "08-20",
                    "usual_countries": "PE",
                    "usual_devices": "D-01"
                }
            }
        }

# ============================================
# HITL (HUMAN-IN-THE-LOOP) MODELS
# ============================================

from enum import Enum as PyEnum

class HITLStatus(str, PyEnum):
    """Estados de revisión HITL"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    IN_REVIEW = "IN_REVIEW"


class HITLCase(BaseModel):
    """Caso en cola HITL"""
    case_id: str = Field(..., description="ID único del caso")
    transaction: Transaction
    decision_recommendation: DecisionType
    confidence: float
    signals: List[str]
    citations_internal: List[InternalCitation] = Field(default_factory=list)
    citations_external: List[ExternalCitation] = Field(default_factory=list)
    agent_route: str
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = None 
    status: HITLStatus = Field(default=HITLStatus.PENDING)
    reviewer_id: Optional[str] = None
    reviewer_decision: Optional[DecisionType] = None
    reviewer_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "case_id": "HITL-001",
                "transaction": {
                    "transaction_id": "T-1002",
                    "customer_id": "CU-002",
                    "amount": 9500.00,
                    "currency": "PEN",
                    "country": "PE",
                    "channel": "mobile",
                    "device_id": "D-02",
                    "timestamp": "2025-12-17T23:45:00",
                    "merchant_id": "M-002"
                },
                "decision_recommendation": "ESCALATE_TO_HUMAN",
                "confidence": 0.65,
                "signals": ["Monto alto", "Horario atípico"],
                "status": "PENDING"
            }
        }


class HITLReviewRequest(BaseModel):
    """Request para revisar un caso HITL"""
    reviewer_id: str = Field(..., description="ID del revisor")
    decision: DecisionType = Field(..., description="Decisión del revisor")
    notes: Optional[str] = Field(None, description="Notas del revisor")
    
    class Config:
        json_schema_extra = {
            "example": {
                "reviewer_id": "analyst-001",
                "decision": "APPROVE",
                "notes": "Cliente verificado por teléfono. Compra legítima."
            }
        }

""" 
class HITLCaseResponse(BaseModel):
    
    case_id: str
    transaction_id: str
    status: HITLStatus
    decision_recommendation: DecisionType
    confidence: float
    created_by: Optional[str] = None  # ← AGREGAR
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewer_decision: Optional[DecisionType] = None
 """

class HITLCaseResponse(BaseModel):
    """Response de operación HITL"""
    case_id: str
    status: str
    reviewer_id: Optional[str] = None
    reviewer_decision: Optional[str] = None
    reviewer_notes: Optional[str] = None
    reviewed_at: Optional[str] = None
    message: str
    success: bool


class HITLReviewResponse(BaseModel):
    """Respuesta con información del caso HITL REVISADO"""
    case_id: str
    status: HITLStatus
    reviewer_decision: Optional[DecisionType] = None
    reviewed_at: Optional[datetime] = None
    message: str