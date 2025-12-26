"""
Database Models - SQLAlchemy ORM
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum
from sqlalchemy import Enum


Base = declarative_base()


class DecisionTypeEnum(str, enum.Enum):
    """Enum para tipos de decisión"""
    APPROVE = "APPROVE"
    CHALLENGE = "CHALLENGE"
    BLOCK = "BLOCK"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"


class HITLStatusEnum(str, enum.Enum):
    """Enum para estados HITL"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    IN_REVIEW = "IN_REVIEW"


class TransactionDB(Base):
    """Tabla de transacciones"""
    __tablename__ = "transactions"
    
    transaction_id = Column(String(50), primary_key=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False, index=True)  # ← ACTUALIZAR
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False)
    country = Column(String(10), ForeignKey("countries.code"), nullable=False)  # ← ACTUALIZAR
    channel = Column(String(20), ForeignKey("channels.code"), nullable=False)  # ← ACTUALIZAR
    device_id = Column(String(50), nullable=False)
    merchant_id = Column(String(50), ForeignKey("merchants.merchant_id"), nullable=False)  # ← ACTUALIZAR
    transaction_timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    customer = relationship("CustomerDB", back_populates="transactions")  # ← AGREGAR
    decisions = relationship("FraudDecisionDB", back_populates="transaction")


class FraudDecisionDB(Base):
    """Tabla de decisiones de fraude"""
    __tablename__ = "fraud_decisions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(50), ForeignKey("transactions.transaction_id"), nullable=False, index=True)
    decision = Column(SQLEnum(DecisionTypeEnum), nullable=False)
    confidence = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=True)
    agent_route = Column(Text, nullable=False)
    processing_time_ms = Column(Float, nullable=False)
    explanation_customer = Column(Text, nullable=True)
    explanation_audit = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relaciones
    transaction = relationship("TransactionDB", back_populates="decisions")
    signals = relationship("SignalDB", back_populates="decision", cascade="all, delete-orphan")
    citations_internal = relationship("InternalCitationDB", back_populates="decision", cascade="all, delete-orphan")
    citations_external = relationship("ExternalCitationDB", back_populates="decision", cascade="all, delete-orphan")
    logs = relationship("AnalysisLogDB", back_populates="decision", cascade="all, delete-orphan")



class SignalDB(Base):
    """Tabla de señales detectadas"""
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    decision_id = Column(Integer, ForeignKey("fraud_decisions.id"), nullable=False)
    signal_text = Column(Text, nullable=False)
    source_agent = Column(String(100), nullable=True)
    
    # Relaciones
    decision = relationship("FraudDecisionDB", back_populates="signals")


class InternalCitationDB(Base):
    """Tabla de citaciones internas (políticas)"""
    __tablename__ = "citations_internal"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    decision_id = Column(Integer, ForeignKey("fraud_decisions.id"), nullable=False)
    policy_id = Column(String(50), nullable=False)
    version = Column(String(20), nullable=False)
    chunk_id = Column(String(10), nullable=True)
    
    # Relaciones
    decision = relationship("FraudDecisionDB", back_populates="citations_internal")


class ExternalCitationDB(Base):
    """Tabla de citaciones externas (web)"""
    __tablename__ = "citations_external"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    decision_id = Column(Integer, ForeignKey("fraud_decisions.id"), nullable=False)
    url = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    
    # Relaciones
    decision = relationship("FraudDecisionDB", back_populates="citations_external")


class HITLCaseDB(Base):
    """Tabla de casos Human-in-the-Loop"""
    __tablename__ = "hitl_cases"
    
    case_id = Column(String(50), primary_key=True)
    transaction_id = Column(String(50), ForeignKey("transactions.transaction_id"), nullable=False, index=True)
    decision_recommendation = Column(SQLEnum(DecisionTypeEnum), nullable=False)
    confidence = Column(Float, nullable=False)
    status = Column(SQLEnum(HITLStatusEnum), default=HITLStatusEnum.PENDING, index=True)
    agent_route = Column(Text, nullable=False)
   # reviewer_id = Column(String(50), nullable=True)
    #reviewer_decision = Column(SQLEnum(DecisionTypeEnum), nullable=True)
    #reviewer_notes = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    #reviewed_at = Column(DateTime, nullable=True)

    # Información de revisión
    reviewer_id = Column(String(100), nullable=True)
    reviewer_decision = Column(Enum(DecisionTypeEnum), nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    # Relaciones
    transaction = relationship("TransactionDB")

class CustomerDB(Base):
    """Tabla de clientes"""
    __tablename__ = "customers"
    
    customer_id = Column(String(50), primary_key=True)
    nombre = Column(String(200), nullable=False)
    apellido = Column(String(200), nullable=False)
    email = Column(String(200), nullable=True)
    telefono = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    transactions = relationship("TransactionDB", back_populates="customer")


class CountryDB(Base):
    """Tabla de países"""
    __tablename__ = "countries"
    
    code = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False)
    currency = Column(String(10), nullable=False)


class ChannelDB(Base):
    """Tabla de canales"""
    __tablename__ = "channels"
    
    code = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(200), nullable=True)


class MerchantDB(Base):
    """Tabla de comercios"""
    __tablename__ = "merchants"
    
    merchant_id = Column(String(50), primary_key=True)
    nombre = Column(String(200), nullable=False)
    categoria = Column(String(100), nullable=True)
    pais = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AnalysisLogDB(Base):
    """Tabla de logs de análisis"""
    __tablename__ = "analysis_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("fraud_decisions.id"), nullable=False, index=True)
    event_type = Column(String(20), nullable=False)  # phase, agent, success, info, error, complete
    phase = Column(String(50), nullable=True)
    agent = Column(String(100), nullable=True)
    message = Column(Text, nullable=False)
    event_data = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relación
    decision = relationship("FraudDecisionDB", back_populates="logs")