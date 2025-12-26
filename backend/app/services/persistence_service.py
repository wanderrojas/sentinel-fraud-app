"""
Persistence Service - Guardar decisiones en base de datos
"""
from sqlalchemy.orm import Session
from app.database.models import (
    TransactionDB, FraudDecisionDB, SignalDB,
    InternalCitationDB, ExternalCitationDB, HITLCaseDB,
    DecisionTypeEnum, HITLStatusEnum,
    CustomerDB, CountryDB, ChannelDB, MerchantDB
)
from app.models.schemas import (
    Transaction, DecisionType, InternalCitation, ExternalCitation
)
from typing import List, Dict
from datetime import datetime


class PersistenceService:
    """Servicio para persistir datos en base de datos"""
    
    @staticmethod
    def _ensure_customer_exists(db: Session, customer_id: str):
        """Verificar que el cliente exista, si no, crear temporal"""
        customer = db.query(CustomerDB).filter(
            CustomerDB.customer_id == customer_id
        ).first()
        
        if not customer:
            print(f"   ⚠️  Cliente {customer_id} no existe, creando temporal...")
            customer = CustomerDB(
                customer_id=customer_id,
                nombre="Cliente",
                apellido=customer_id,
                email=f"{customer_id}@temporal.com"
            )
            db.add(customer)
            db.flush()
        
        return customer
    
    @staticmethod
    def _ensure_country_exists(db: Session, country_code: str):
        """Verificar que el país exista, si no, crear temporal"""
        country = db.query(CountryDB).filter(
            CountryDB.code == country_code
        ).first()
        
        if not country:
            print(f"   ⚠️  País {country_code} no existe, creando temporal...")
            country = CountryDB(
                code=country_code,
                name=f"País {country_code}",
                currency="USD"
            )
            db.add(country)
            db.flush()
        
        return country
    
    @staticmethod
    def _ensure_channel_exists(db: Session, channel_code: str):
        """Verificar que el canal exista, si no, crear temporal"""
        channel = db.query(ChannelDB).filter(
            ChannelDB.code == channel_code
        ).first()
        
        if not channel:
            print(f"   ⚠️  Canal {channel_code} no existe, creando temporal...")
            channel = ChannelDB(
                code=channel_code,
                name=f"Canal {channel_code}",
                description=f"Canal {channel_code} temporal"
            )
            db.add(channel)
            db.flush()
        
        return channel
    
    @staticmethod
    def _ensure_merchant_exists(db: Session, merchant_id: str, country_code: str = None):
        """Verificar que el comercio exista, si no, crear temporal"""
        merchant = db.query(MerchantDB).filter(
            MerchantDB.merchant_id == merchant_id
        ).first()
        
        if not merchant:
            print(f"   ⚠️  Comercio {merchant_id} no existe, creando temporal...")
            merchant = MerchantDB(
                merchant_id=merchant_id,
                nombre=f"Comercio {merchant_id}",
                categoria="Desconocido",
                pais=country_code
            )
            db.add(merchant)
            db.flush()
        
        return merchant
    
    @staticmethod
    def save_transaction_analysis(
        db: Session,
        transaction: Transaction,
        decision: DecisionType,
        confidence: float,
        risk_score: float,
        signals: List[str],
        citations_internal: List[InternalCitation],
        citations_external: List,
        explanation_customer: str,
        explanation_audit: str,
        agent_route: str,
        processing_time_ms: float
    ) -> FraudDecisionDB:
        """
        Guardar análisis completo de transacción
        
        Returns:
            FraudDecisionDB: Decisión guardada con ID
        """
        
        # 1. Verificar/crear maestros necesarios
        PersistenceService._ensure_customer_exists(db, transaction.customer_id)
        PersistenceService._ensure_country_exists(db, transaction.country)
        PersistenceService._ensure_channel_exists(db, transaction.channel)
        PersistenceService._ensure_merchant_exists(db, transaction.merchant_id, transaction.country)
        
        # 2. Guardar o actualizar transacción
        transaction_db = db.query(TransactionDB).filter(
            TransactionDB.transaction_id == transaction.transaction_id
        ).first()
        
        if not transaction_db:
            transaction_db = TransactionDB(
                transaction_id=transaction.transaction_id,
                customer_id=transaction.customer_id,
                amount=transaction.amount,
                currency=transaction.currency,
                country=transaction.country,
                channel=transaction.channel,
                device_id=transaction.device_id,
                merchant_id=transaction.merchant_id,
                transaction_timestamp=transaction.timestamp,
            )
            db.add(transaction_db)
            db.flush()  # Para obtener el ID
        
        # 3. Guardar decisión
        decision_db = FraudDecisionDB(
            transaction_id=transaction.transaction_id,
            decision=DecisionTypeEnum(decision.value),
            confidence=confidence,
            risk_score=risk_score,
            agent_route=agent_route,
            processing_time_ms=processing_time_ms,
            explanation_customer=explanation_customer,
            explanation_audit=explanation_audit,
        )
        db.add(decision_db)
        db.flush()  # Para obtener el ID
        
        # 4. Guardar señales
        for signal_text in signals:
            signal_db = SignalDB(
                decision_id=decision_db.id,
                signal_text=signal_text,
            )
            db.add(signal_db)
        
        # 5. Guardar citaciones internas
        for citation in citations_internal:
            citation_db = InternalCitationDB(
                decision_id=decision_db.id,
                policy_id=citation.policy_id,
                version=citation.version,
                chunk_id=citation.chunk_id,
            )
            db.add(citation_db)
        
        # 6. Guardar citaciones externas
        for citation in citations_external:
            citation_db = ExternalCitationDB(
                decision_id=decision_db.id,
                url=citation.url,
                summary=citation.summary,
            )
            db.add(citation_db)
        
        # Commit
        db.commit()
        db.refresh(decision_db)
        
        print(f"   💾 Análisis guardado en BD - Decision ID: {decision_db.id}")
        
        return decision_db
    
    @staticmethod
    def save_hitl_case(
        db: Session,
        case_id: str,
        transaction_id: str,
        decision_recommendation: DecisionType,
        confidence: float,
        agent_route: str
    ) -> HITLCaseDB:
        """Guardar caso HITL en base de datos"""
        
        hitl_case_db = HITLCaseDB(
            case_id=case_id,
            transaction_id=transaction_id,
            decision_recommendation=DecisionTypeEnum(decision_recommendation.value),
            confidence=confidence,
            status=HITLStatusEnum.PENDING,
            agent_route=agent_route,
        )
        db.add(hitl_case_db)
        db.commit()
        db.refresh(hitl_case_db)
        
        print(f"   💾 Caso HITL guardado en BD: {case_id}")
        
        return hitl_case_db
    
    @staticmethod
    def get_transaction_history(
        db: Session,
        customer_id: str = None,
        decision: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Obtener historial de transacciones con información completa
        
        Args:
            db: Sesión de base de datos
            customer_id: Filtrar por ID de cliente (opcional)
            decision: Filtrar por tipo de decisión (opcional)
            limit: Límite de resultados
        
        Returns:
            Lista de transacciones con información completa
        """
        
        query = db.query(
            FraudDecisionDB,
            TransactionDB,
            CustomerDB,
            CountryDB,
            ChannelDB,
            MerchantDB
        ).join(
            TransactionDB,
            FraudDecisionDB.transaction_id == TransactionDB.transaction_id
        ).join(
            CustomerDB,
            TransactionDB.customer_id == CustomerDB.customer_id
        ).join(
            CountryDB,
            TransactionDB.country == CountryDB.code
        ).join(
            ChannelDB,
            TransactionDB.channel == ChannelDB.code
        ).join(
            MerchantDB,
            TransactionDB.merchant_id == MerchantDB.merchant_id
        )
        
        # Filtrar por customer_id si se proporciona
        if customer_id:
            query = query.filter(TransactionDB.customer_id == customer_id)
        
        # Filtrar por decision si se proporciona
        if decision:
            try:
                decision_enum = DecisionTypeEnum[decision.upper()]
                query = query.filter(FraudDecisionDB.decision == decision_enum)
            except KeyError:
                # Si la decisión no es válida, no aplicar filtro
                pass
        
        results = query.order_by(FraudDecisionDB.created_at.desc()).limit(limit).all()
        
        transactions = []
        for decision_obj, transaction, customer, country, channel, merchant in results:
            transactions.append({
                "transaction_id": transaction.transaction_id,
                "decision": decision_obj.decision.value,
                "confidence": decision_obj.confidence,
                "risk_score": decision_obj.risk_score,
                "processing_time_ms": decision_obj.processing_time_ms,
                "created_at": decision_obj.created_at.isoformat(),
                # Información extendida
                "customer": {
                    "customer_id": customer.customer_id,
                    "nombre": customer.nombre,
                    "apellido": customer.apellido
                },
                "amount": transaction.amount,
                "currency": transaction.currency,
                "country": {
                    "code": country.code,
                    "name": country.name
                },
                "channel": {
                    "code": channel.code,
                    "name": channel.name
                },
                "merchant": {
                    "merchant_id": merchant.merchant_id,
                    "nombre": merchant.nombre,
                    "categoria": merchant.categoria
                },
                "transaction_timestamp": transaction.transaction_timestamp.isoformat()
            })
        
        return transactions
    
    @staticmethod
    def get_statistics(db: Session) -> Dict:
        """Obtener estadísticas generales"""
        
        total_transactions = db.query(TransactionDB).count()
        total_decisions = db.query(FraudDecisionDB).count()
        total_customers = db.query(CustomerDB).count()
        total_merchants = db.query(MerchantDB).count()
        
        # Contar por tipo de decisión
        approve_count = db.query(FraudDecisionDB).filter(
            FraudDecisionDB.decision == DecisionTypeEnum.APPROVE
        ).count()
        
        challenge_count = db.query(FraudDecisionDB).filter(
            FraudDecisionDB.decision == DecisionTypeEnum.CHALLENGE
        ).count()
        
        block_count = db.query(FraudDecisionDB).filter(
            FraudDecisionDB.decision == DecisionTypeEnum.BLOCK
        ).count()
        
        escalate_count = db.query(FraudDecisionDB).filter(
            FraudDecisionDB.decision == DecisionTypeEnum.ESCALATE_TO_HUMAN
        ).count()
        
        # HITL stats
        hitl_pending = db.query(HITLCaseDB).filter(
            HITLCaseDB.status == HITLStatusEnum.PENDING
        ).count()
        
        hitl_approved = db.query(HITLCaseDB).filter(
            HITLCaseDB.status == HITLStatusEnum.APPROVED
        ).count()
        
        hitl_rejected = db.query(HITLCaseDB).filter(
            HITLCaseDB.status == HITLStatusEnum.REJECTED
        ).count()
        
        return {
            "total_transactions": total_transactions,
            "total_decisions": total_decisions,
            "total_customers": total_customers,
            "total_merchants": total_merchants,
            "decisions_by_type": {
                "APPROVE": approve_count,
                "CHALLENGE": challenge_count,
                "BLOCK": block_count,
                "ESCALATE_TO_HUMAN": escalate_count,
            },
            "hitl_cases": {
                "pending": hitl_pending,
                "approved": hitl_approved,
                "rejected": hitl_rejected,
                "total": hitl_pending + hitl_approved + hitl_rejected,
            }
        }
    
    @staticmethod
    def save_analysis_log(
        db: Session,
        decision_id: int,
        event_type: str,
        message: str,
        phase: str = None,
        agent: str = None,
        event_data: dict = None
    ):
        """Guardar log de análisis"""
        import json
        from app.database.models import AnalysisLogDB
        
        log_db = AnalysisLogDB(
            decision_id=decision_id,
            event_type=event_type,
            phase=phase,
            agent=agent,
            message=message,
            event_data=json.dumps(event_data) if event_data else None
        )
        db.add(log_db)
        db.flush()
        
        return log_db
    
    @staticmethod
    def get_transaction_details(db: Session, transaction_id: str) -> Dict:
        """
        Obtener detalles completos de una transacción incluyendo logs
        
        Args:
            db: Sesión de base de datos
            transaction_id: ID de la transacción
        
        Returns:
            Dict con toda la información de la transacción
        """
        import json
        from app.database.models import (
            FraudDecisionDB, TransactionDB, CustomerDB,
            CountryDB, ChannelDB, MerchantDB, AnalysisLogDB,
            SignalDB, InternalCitationDB, ExternalCitationDB
        )
        
        # Obtener decisión con todas las relaciones
        decision = db.query(FraudDecisionDB).filter(
            FraudDecisionDB.transaction_id == transaction_id
        ).first()
        
        if not decision:
            return None
        
        # Obtener transacción con relaciones
        transaction = db.query(TransactionDB).filter(
            TransactionDB.transaction_id == transaction_id
        ).first()
        
        if not transaction:
            return None
        
        # Obtener maestros
        customer = db.query(CustomerDB).filter(
            CustomerDB.customer_id == transaction.customer_id
        ).first()
        
        country = db.query(CountryDB).filter(
            CountryDB.code == transaction.country
        ).first()
        
        channel = db.query(ChannelDB).filter(
            ChannelDB.code == transaction.channel
        ).first()
        
        merchant = db.query(MerchantDB).filter(
            MerchantDB.merchant_id == transaction.merchant_id
        ).first()
        
        # Obtener señales
        signals = db.query(SignalDB).filter(
            SignalDB.decision_id == decision.id
        ).all()
        
        # Obtener citaciones internas
        citations_internal = db.query(InternalCitationDB).filter(
            InternalCitationDB.decision_id == decision.id
        ).all()
        
        # Obtener citaciones externas
        citations_external = db.query(ExternalCitationDB).filter(
            ExternalCitationDB.decision_id == decision.id
        ).all()
        
        # Obtener logs de análisis (NUEVO)
        logs = db.query(AnalysisLogDB).filter(
            AnalysisLogDB.decision_id == decision.id
        ).order_by(AnalysisLogDB.created_at.asc()).all()
        
        # Construir respuesta completa
        result = {
            # Información básica
            "transaction_id": transaction.transaction_id,
            "decision": decision.decision.value,
            "confidence": decision.confidence,
            "risk_score": decision.risk_score,
            "processing_time_ms": decision.processing_time_ms,
            "created_at": decision.created_at.isoformat(),
            
            # Ruta de agentes (como array)
            "agent_route": decision.agent_route.split(" → ") if decision.agent_route else [],
            
            # Transacción
            "transaction": {
                "transaction_id": transaction.transaction_id,
                "amount": transaction.amount,
                "currency": transaction.currency,
                "device_id": transaction.device_id,
                "transaction_timestamp": transaction.transaction_timestamp.isoformat()
            },
            
            # Cliente
            "customer": {
                "customer_id": customer.customer_id,
                "nombre": customer.nombre,
                "apellido": customer.apellido,
                "email": customer.email,
                "telefono": customer.telefono
            } if customer else None,
            
            # País
            "country": {
                "code": country.code,
                "name": country.name,
                "currency": country.currency
            } if country else None,
            
            # Canal
            "channel": {
                "code": channel.code,
                "name": channel.name,
                "description": channel.description
            } if channel else None,
            
            # Comercio
            "merchant": {
                "merchant_id": merchant.merchant_id,
                "nombre": merchant.nombre,
                "categoria": merchant.categoria,
                "pais": merchant.pais
            } if merchant else None,
            
            # Señales
            "signals": [signal.signal_text for signal in signals],
            
            # Citaciones internas
            "citations_internal": [
                {
                    "policy_id": citation.policy_id,
                    "version": citation.version,
                    "chunk_id": citation.chunk_id
                }
                for citation in citations_internal
            ],
            
            # Citaciones externas
            "citations_external": [
                {
                    "url": citation.url,
                    "summary": citation.summary
                }
                for citation in citations_external
            ],
            
            # Explicaciones
            "explanation_customer": decision.explanation_customer,
            "explanation_audit": decision.explanation_audit,
            
            # LOGS DE ANÁLISIS (NUEVO)
            "analysis_logs": [
                {
                    "event_type": log.event_type,
                    "phase": log.phase,
                    "agent": log.agent,
                    "message": log.message,
                    "data": json.loads(log.event_data) if log.event_data else None,
                    "timestamp": log.created_at.isoformat()
                }
                for log in logs
            ]
        }
        
        return result