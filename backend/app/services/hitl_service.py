"""
Human-in-the-Loop Service
"""
from typing import List, Dict, Optional
from datetime import datetime
from app.models.schemas import (
    Transaction, DecisionType, HITLCase, HITLStatus,
    InternalCitation, ExternalCitation
)


class HITLService:
    """Servicio para gestión de casos Human-in-the-Loop"""
    
    def __init__(self):
        """Inicializar servicio HITL (sin diccionario en memoria)"""
        pass
    
    def _get_next_case_id(self) -> str:
        """Generar el siguiente ID de caso basado en la BD"""
        from app.database.connection import get_db
        from app.database.models import HITLCaseDB
        
        db = next(get_db())
        try:
            count = db.query(HITLCaseDB).count()
            return f"HITL-{count + 1:05d}"
        finally:
            db.close()
    
    def create_case(
        self,
        transaction: Transaction,
        decision_recommendation: DecisionType,
        confidence: float,
        signals: List[str],
        citations_internal: List,
        citations_external: List,
        agent_route: str,
        created_by: str = None
    ) -> HITLCase:
        """
        Crear un nuevo caso HITL
        
        Args:
            transaction: Transacción a revisar
            decision_recommendation: Decisión recomendada
            confidence: Nivel de confianza
            signals: Señales detectadas
            citations_internal: Citaciones internas
            citations_external: Citaciones externas
            agent_route: Ruta de agentes ejecutados
            created_by: Usuario que generó la transacción (opcional)
        
        Returns:
            Caso HITL creado
        """
        case_id = self._get_next_case_id()
        
        case = HITLCase(
            case_id=case_id,
            transaction=transaction,
            decision_recommendation=decision_recommendation,
            confidence=confidence,
            signals=signals,
            citations_internal=citations_internal,
            citations_external=citations_external,
            agent_route=agent_route,
            created_by=created_by,
            created_at=datetime.now().isoformat(),
            status=HITLStatus.PENDING
        )
        
        # Persistir en base de datos
        self._persist_case(case)
        
        print(f"   ✅ Caso HITL creado: {case_id}")
        
        return case
    
    def _persist_case(self, case: HITLCase):
        """Persistir caso HITL en base de datos"""
        from app.database.connection import get_db
        from app.database.models import HITLCaseDB, DecisionTypeEnum, HITLStatusEnum
        
        db = next(get_db())
        try:
            hitl_case_db = HITLCaseDB(
                case_id=case.case_id,
                transaction_id=case.transaction.transaction_id,
                decision_recommendation=DecisionTypeEnum[case.decision_recommendation.value],
                confidence=case.confidence,
                status=HITLStatusEnum[case.status.value],
                agent_route=case.agent_route,
                created_by=case.created_by
            )
            db.add(hitl_case_db)
            db.commit()
            print(f"   💾 Caso HITL guardado en BD: {case.case_id}")
        except Exception as e:
            print(f"   ❌ Error guardando caso HITL: {e}")
            db.rollback()
        finally:
            db.close()
    
    def get_pending_cases(self) -> List[HITLCase]:
        """Obtener casos pendientes desde la BD"""
        from app.database.connection import get_db
        from app.database.models import HITLCaseDB, HITLStatusEnum, TransactionDB
        
        db = next(get_db())
        try:
            cases_db = db.query(HITLCaseDB).filter(
                HITLCaseDB.status == HITLStatusEnum.PENDING
            ).all()
            
            return self._convert_cases_to_schema(cases_db, db)
        finally:
            db.close()
    
    def get_all_cases(self, status: Optional[HITLStatus] = None) -> List[HITLCase]:
        """Obtener todos los casos (opcionalmente filtrados por estado)"""
        from app.database.connection import get_db
        from app.database.models import HITLCaseDB, HITLStatusEnum
        
        db = next(get_db())
        try:
            query = db.query(HITLCaseDB)
            
            if status:
                query = query.filter(HITLCaseDB.status == HITLStatusEnum[status.value])
            
            cases_db = query.all()
            return self._convert_cases_to_schema(cases_db, db)
        finally:
            db.close()
    
    def get_case(self, case_id: str) -> Optional[HITLCase]:
        """Obtener un caso específico desde la BD"""
        from app.database.connection import get_db
        from app.database.models import HITLCaseDB
        
        db = next(get_db())
        try:
            case_db = db.query(HITLCaseDB).filter(
                HITLCaseDB.case_id == case_id
            ).first()
            
            if not case_db:
                return None
            
            cases = self._convert_cases_to_schema([case_db], db)
            return cases[0] if cases else None
        finally:
            db.close()
    
    def review_case(
        self,
        case_id: str,
        reviewer_id: str,
        decision: DecisionType,
        notes: str = None
    ) -> HITLCase:
        """
        Revisar y resolver un caso HITL
        
        Args:
            case_id: ID del caso a revisar
            reviewer_id: ID del revisor
            decision: Decisión final del revisor
            notes: Notas de la revisión
        
        Returns:
            Caso actualizado
        """
        from app.database.connection import get_db
        from app.database.models import HITLCaseDB, DecisionTypeEnum, HITLStatusEnum
        from datetime import datetime as dt
        
        db = next(get_db())
        try:
            case_db = db.query(HITLCaseDB).filter(
                HITLCaseDB.case_id == case_id
            ).first()
            
            if not case_db:
                raise ValueError(f"Caso {case_id} no encontrado")
            
            if case_db.status != HITLStatusEnum.PENDING:
                raise ValueError(f"Caso {case_id} ya fue revisado")
            
            # Actualizar caso
            case_db.reviewer_id = reviewer_id
            case_db.reviewer_decision = DecisionTypeEnum[decision.value]
            case_db.reviewer_notes = notes
            case_db.reviewed_at = dt.now()
            
            # Determinar estado final
            if decision == DecisionType.APPROVE:
                case_db.status = HITLStatusEnum.APPROVED
            elif decision == DecisionType.BLOCK:
                case_db.status = HITLStatusEnum.REJECTED
            else:
                case_db.status = HITLStatusEnum.IN_REVIEW
            
            db.commit()
            db.refresh(case_db)
            
            print(f"   💾 Caso HITL actualizado en BD: {case_id}")
            
            # Convertir a schema
            cases = self._convert_cases_to_schema([case_db], db)
            return cases[0] if cases else None
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def _convert_cases_to_schema(self, cases_db: list, db) -> List[HITLCase]:
        """Convertir casos de BD a schema HITLCase con información completa"""
        from app.database.models import (
            TransactionDB, CustomerDB, CountryDB, 
            ChannelDB, MerchantDB, FraudDecisionDB,
            SignalDB, InternalCitationDB, ExternalCitationDB
        )
        
        result = []
        
        for case_db in cases_db:
            # Obtener transacción con JOINS
            transaction_query = db.query(
                TransactionDB,
                CustomerDB,
                CountryDB,
                ChannelDB,
                MerchantDB
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
            ).filter(
                TransactionDB.transaction_id == case_db.transaction_id
            ).first()
            
            if not transaction_query:
                continue
            
            transaction_db, customer_db, country_db, channel_db, merchant_db = transaction_query
            
            # Obtener decisión de fraude para signals y citations
            decision_db = db.query(FraudDecisionDB).filter(
                FraudDecisionDB.transaction_id == case_db.transaction_id
            ).first()
            
            signals = []
            citations_internal = []
            citations_external = []
            
            if decision_db:
                # Obtener señales
                signals_db = db.query(SignalDB).filter(
                    SignalDB.decision_id == decision_db.id
                ).all()
                signals = [s.signal_text for s in signals_db]
                
                # Obtener citaciones internas
                citations_int_db = db.query(InternalCitationDB).filter(
                    InternalCitationDB.decision_id == decision_db.id
                ).all()
                from app.models.schemas import InternalCitation
                citations_internal = [
                    InternalCitation(
                        policy_id=c.policy_id,
                        version=c.version,
                        chunk_id=c.chunk_id
                    )
                    for c in citations_int_db
                ]
                
                # Obtener citaciones externas
                citations_ext_db = db.query(ExternalCitationDB).filter(
                    ExternalCitationDB.decision_id == decision_db.id
                ).all()
                from app.models.schemas import ExternalCitation
                citations_external = [
                    ExternalCitation(
                        url=c.url,
                        summary=c.summary
                    )
                    for c in citations_ext_db
                ]
            
            # Construir Transaction con información enriquecida
            transaction = Transaction(
                transaction_id=transaction_db.transaction_id,
                customer_id=transaction_db.customer_id,
                amount=transaction_db.amount,
                currency=transaction_db.currency,
                country=transaction_db.country,
                channel=transaction_db.channel,
                device_id=transaction_db.device_id,
                timestamp=transaction_db.transaction_timestamp,
                merchant_id=transaction_db.merchant_id
            )
            
            # Construir HITLCase con toda la información
            case = HITLCase(
                case_id=case_db.case_id,
                transaction=transaction,
                decision_recommendation=DecisionType[case_db.decision_recommendation.value],
                confidence=case_db.confidence,
                signals=signals,
                citations_internal=citations_internal,
                citations_external=citations_external,
                agent_route=case_db.agent_route or "",
                created_by=case_db.created_by,
                created_at=case_db.created_at.isoformat(),
                status=HITLStatus[case_db.status.value],
                reviewer_id=case_db.reviewer_id,
                reviewer_decision=DecisionType[case_db.reviewer_decision.value] if case_db.reviewer_decision else None,
                reviewer_notes=case_db.reviewer_notes,
                reviewed_at=case_db.reviewed_at.isoformat() if case_db.reviewed_at else None
            )
            
            # AGREGAR INFORMACIÓN DE MAESTROS AL CASO
            # (Lo haremos en el endpoint directamente para no modificar el schema HITLCase)
            case._customer = {
                "customer_id": customer_db.customer_id,
                "nombre": customer_db.nombre,
                "apellido": customer_db.apellido,
                "email": customer_db.email,
                "telefono": customer_db.telefono
            }
            
            case._country = {
                "code": country_db.code,
                "name": country_db.name,
                "currency": country_db.currency
            }
            
            case._channel = {
                "code": channel_db.code,
                "name": channel_db.name,
                "description": channel_db.description
            }
            
            case._merchant = {
                "merchant_id": merchant_db.merchant_id,
                "nombre": merchant_db.nombre,
                "categoria": merchant_db.categoria,
                "pais": merchant_db.pais
            }
            
            result.append(case)
        
        return result
    
    def get_statistics(self) -> Dict:
        """Obtener estadísticas de HITL desde la BD"""
        from app.database.connection import get_db
        from app.database.models import HITLCaseDB, HITLStatusEnum
        
        db = next(get_db())
        try:
            total = db.query(HITLCaseDB).count()
            pending = db.query(HITLCaseDB).filter(
                HITLCaseDB.status == HITLStatusEnum.PENDING
            ).count()
            approved = db.query(HITLCaseDB).filter(
                HITLCaseDB.status == HITLStatusEnum.APPROVED
            ).count()
            rejected = db.query(HITLCaseDB).filter(
                HITLCaseDB.status == HITLStatusEnum.REJECTED
            ).count()
            in_review = db.query(HITLCaseDB).filter(
                HITLCaseDB.status == HITLStatusEnum.IN_REVIEW
            ).count()
            
            return {
                "total": total,
                "pending": pending,
                "approved": approved,
                "rejected": rejected,
                "in_review": in_review
            }
        finally:
            db.close()


# ============================================
# INSTANCIA GLOBAL
# ============================================

_hitl_service_instance = None


def get_hitl_service() -> HITLService:
    """Obtener instancia única del servicio HITL"""
    global _hitl_service_instance
    if _hitl_service_instance is None:
        _hitl_service_instance = HITLService()
    return _hitl_service_instance