"""
Punto de entrada principal de la aplicación FastAPI
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.models.schemas import (
    TransactionAnalysisRequest,
    DecisionResponse,
    DecisionType,
)
import json
from pathlib import Path
from datetime import datetime
from fastapi import Depends
from app.database.connection import init_db, get_db
from app.services.persistence_service import PersistenceService
from sqlalchemy.orm import Session
from app.security import verify_api_key_and_jwt, get_current_user
from app.api.routes import hitl, history, auth, masters
from fastapi.responses import StreamingResponse
from app.services.streaming_service import StreamingService
from dotenv import load_dotenv
import os


env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


# Obtener configuración
settings = get_settings()

# Crear instancia de FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Sistema Multi-Agente para Detección de Fraude en Transacciones Financieras",
    docs_url="/docs",
    redoc_url="/redoc",

)

# ============================================
# REGISTRAR RUTAS
# ============================================

# Auth (sin protección de API Key)
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Authentication"]
)


app.include_router(
    hitl.router,
    prefix=f"{settings.API_V1_PREFIX}/hitl",
    tags=["Human-in-the-Loop"]
)

app.include_router(
    masters.router,
    prefix=f"{settings.API_V1_PREFIX}/masters",
    tags=["Master Data"]
)

app.include_router(
    history.router,
    prefix=f"{settings.API_V1_PREFIX}/history",
    tags=["History & Statistics"]
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# HELPERS
# ============================================

def load_customer_behavior(customer_id: str):
    """Cargar comportamiento del cliente desde JSON"""
    data_path = Path("data/customer_behavior.json")
    if data_path.exists():
        with open(data_path, "r", encoding="utf-8") as f:
            behaviors = json.load(f)
            return behaviors.get(customer_id)
    return None


def _generate_customer_explanation(decision: DecisionType, signals: list) -> str:
    """Generar explicación para el cliente"""
    if decision == DecisionType.APPROVE:
        return "Su transacción ha sido aprobada exitosamente."
    elif decision == DecisionType.CHALLENGE:
        return f"Su transacción requiere validación adicional. Motivos: {', '.join(signals[:2])}"
    elif decision == DecisionType.BLOCK:
        return "Su transacción ha sido bloqueada por seguridad. Contacte a su banco."
    else:  # ESCALATE_TO_HUMAN
        return "Su transacción está en revisión manual. Le contactaremos pronto."


# ============================================
# ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Fraud Detection Multi-Agent System API",
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "llm_config": "/config/llm",
            "analyze_transaction": "/api/v1/transactions/analyze"
        }
    }


@app.get("/health")
async def health_check():
    """Verificar que la API está funcionando (sin autenticación)"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "timestamp": datetime.now().isoformat(),
        "env": settings.ENVIRONMENT,
        "debug": settings.DEBUG
    
    }


@app.get(
    "/config/llm",
    dependencies=[Depends(verify_api_key_and_jwt)]  # ← API KEY + JWT
)
async def get_llm_config():
    """Ver configuración del LLM (requiere autenticación)"""
    from app.services.llm_service import get_provider_info
    
    info = get_provider_info()
    return {
        "llm_provider": settings.LLM_PROVIDER,
        "details": info,
        "temperature": settings.LLM_TEMPERATURE,
        "max_tokens": settings.MAX_TOKENS,
    }


@app.post(
    f"{settings.API_V1_PREFIX}/transactions/analyze",
    response_model=DecisionResponse,
    summary="Analizar transacción para detectar fraude",
    dependencies=[Depends(verify_api_key_and_jwt)]  # ← API KEY + JWT
)
async def analyze_transaction(request: TransactionAnalysisRequest, current_user: dict = Depends(get_current_user)):
    """
    Analiza una transacción usando MÚLTIPLES AGENTES con IA.
    """
    import time
    
    start_time = time.time()
    
    transaction = request.transaction
    customer_behavior = request.customer_behavior
    
    print("\n" + "="*60)
    print(f"🔍 Analizando transacción: {transaction.transaction_id}")
    print("="*60)
    
    # Si no se proporciona comportamiento, intentar cargarlo
    if not customer_behavior:
        behavior_data = load_customer_behavior(transaction.customer_id)
        if behavior_data:
            from app.models.schemas import CustomerBehavior
            customer_behavior = CustomerBehavior(**behavior_data)
            print(f"   📊 Comportamiento del cliente cargado")
        else:
            print(f"   ⚠️  No se encontró comportamiento del cliente")
    
    # ============================================
    # SISTEMA MULTI-AGENTE COMPLETO (7 AGENTES)
    # ============================================
    try:
        from app.agents.transaction_context_agent import TransactionContextAgent
        from app.agents.behavioral_pattern_agent import BehavioralPatternAgent
        from app.agents.policy_rag_agent import PolicyRAGAgent
        from app.agents.threat_intel_agent import ThreatIntelAgent
        from app.agents.evidence_aggregation_agent import EvidenceAggregationAgent
        from app.agents.debate_agents import DebateAgents
        
        agent_route = []
        citations_internal = []
        citations_external = []
        
        # ============================================
        # AGENTE 1: TRANSACTION CONTEXT
        # ============================================
        print("\n📍 FASE 1: Análisis de Contexto")
        context_agent = TransactionContextAgent()
        context_result = context_agent.analyze(transaction, customer_behavior)
        agent_route.append(context_result.get("agent"))
        
        print(f"   ✅ Riesgo: {context_result.get('risk_level')}")
        
        # ============================================
        # AGENTE 2: BEHAVIORAL PATTERN
        # ============================================
        print("\n📍 FASE 2: Análisis de Patrones")
        behavioral_agent = BehavioralPatternAgent()
        behavioral_result = behavioral_agent.analyze(
            transaction, customer_behavior,
            context_signals=context_result.get("signals", [])
        )
        agent_route.append(behavioral_result.get("agent"))
        
        print(f"   ✅ Score: {behavioral_result.get('behavioral_score', 0):.2f}")
        
        # ============================================
        # AGENTE 3: POLICY RAG
        # ============================================
        print("\n📍 FASE 3: Consulta de Políticas (RAG)")
        policy_agent = PolicyRAGAgent()
        policy_result = policy_agent.analyze(
            transaction, customer_behavior,
            context_signals=context_result.get("signals", []),
            behavioral_anomalies=behavioral_result.get("anomalies", [])
        )
        agent_route.append(policy_result.get("agent"))
        
        # Agregar citaciones internas
        for policy in policy_result.get("applicable_policies", []):
            from app.models.schemas import InternalCitation
            citations_internal.append(InternalCitation(
                policy_id=policy["policy_id"],
                chunk_id=policy.get("chunk_id", "1"),
                version=policy["version"]
            ))
        
        print(f"   ✅ Políticas: {len(policy_result.get('applicable_policies', []))}")
        
        # ============================================
        # AGENTE 4: THREAT INTEL
        # ============================================
        print("\n📍 FASE 4: Inteligencia de Amenazas")
        threat_agent = ThreatIntelAgent()
        threat_result = threat_agent.analyze(
            transaction,
            context_signals=context_result.get("signals", [])
        )
        agent_route.append(threat_result.get("agent"))
        
        # Agregar citaciones externas
        for source in threat_result.get("sources", []):
            from app.models.schemas import ExternalCitation
            citations_external.append(ExternalCitation(
                url=source["url"],
                summary=source["summary"]
            ))
        
        print(f"   ✅ Amenazas: {len(threat_result.get('threats_found', []))}")
        
        # ============================================
        # AGENTE 5: EVIDENCE AGGREGATION
        # ============================================
        print("\n📍 FASE 5: Agregación de Evidencias")
        evidence_agent = EvidenceAggregationAgent()
        evidence_result = evidence_agent.analyze(
            context_result, behavioral_result,
            policy_result, threat_result
        )
        agent_route.append(evidence_result.get("agent"))
        
        all_signals = evidence_result.get("all_signals", [])
        aggregated_risk = evidence_result.get("aggregated_risk_score", 0.5)
        
        print(f"   ✅ Risk Score: {aggregated_risk:.2f}")
        
        # ============================================
        # AGENTE 6-7: DEBATE AGENTS
        # ============================================
        print("\n📍 FASE 6: Debate Pro-Fraud vs Pro-Customer")
        debate_agents = DebateAgents()
        debate_result = debate_agents.analyze(
            transaction.transaction_id,
            all_signals,
            aggregated_risk,
            citations_internal,
            citations_external
        )
        agent_route.append(debate_result.get("agent"))
        
        # ============================================
        # FASE 7: DECISION ARBITER (Decisión Final)
        # ============================================
        print("\n📍 FASE 7: Decisión Final (Arbiter)")
        
        # Lógica de decisión basada en evidencia agregada
        if aggregated_risk >= 0.8:
            decision = DecisionType.BLOCK
            confidence = 0.95
        elif aggregated_risk >= 0.6:
            decision = DecisionType.ESCALATE_TO_HUMAN
            confidence = 0.75
        elif aggregated_risk >= 0.4:
            decision = DecisionType.CHALLENGE
            confidence = 0.70
        else:
            decision = DecisionType.APPROVE
            confidence = 0.90
        
        # ============================================
        # FASE 8: VERIFICAR SI REQUIERE HITL
        # ============================================
        # Condiciones para escalar a HITL:
        # 1. Decisión explícita de escalar
        # 2. BLOCK con baja confianza
        # 3. BLOCK con múltiples señales conflictivas
        # 4. CHALLENGE con alto riesgo
        
        should_escalate_to_hitl = (
            decision == DecisionType.ESCALATE_TO_HUMAN or
            (decision == DecisionType.BLOCK and confidence < 0.95) or  # Más permisivo
            (decision == DecisionType.CHALLENGE and aggregated_risk > 0.5) or
            (len(citations_external) > 0 and aggregated_risk > 0.7)  # Si hay alertas externas
        )
        
        if should_escalate_to_hitl:
            from app.services.hitl_service import get_hitl_service
            
            print("\n📍 FASE 8: Escalando a Human-in-the-Loop")
            print(f"   📋 Razón: decision={decision}, confidence={confidence}, risk={aggregated_risk:.2f}")
            
            hitl_service = get_hitl_service()
            hitl_case = hitl_service.create_case(
                transaction=transaction,
                decision_recommendation=decision,
                confidence=confidence,
                signals=all_signals[:10],
                citations_internal=citations_internal,
                citations_external=citations_external,
                agent_route=" → ".join(agent_route),
                created_by=current_user["username"]
            )
            
            print(f"   ✅ Caso HITL creado: {hitl_case.case_id}")
            
            # Actualizar explicación para el cliente
            explanation_customer = (
                f"Su transacción está en revisión manual (Caso: {hitl_case.case_id}). "
                f"Un analista la revisará y le contactaremos pronto."
            )
        else:
            # Explicación normal sin HITL
            explanation_customer = _generate_customer_explanation(decision, all_signals)
        
        # ============================================
        # FASE 9: EXPLAINABILITY (Generar explicación de auditoría)
        # ============================================
        explanation_audit = (
            f"Sistema Multi-Agente (7 fases): "
            f"Risk Score Agregado: {aggregated_risk:.2f}. "
            f"{context_result.get('summary', '')} "
            f"{behavioral_result.get('summary', '')} "
            f"{policy_result.get('summary', '')} "
            f"{threat_result.get('summary', '')} "
            f"Debate: Pro-Fraud argumenta {debate_result.get('pro_fraud_argument', '')[:50]}... "
            f"Pro-Customer argumenta {debate_result.get('pro_customer_argument', '')[:50]}... "
            f"Ruta: {' → '.join(agent_route)}"
        )
        
        # Calcular tiempo
        processing_time = (time.time() - start_time) * 1000
        
        print(f"\n   🎯 Decisión: {decision.value}")
        print(f"   💯 Confianza: {confidence}")
        print(f"   📊 Risk Score: {aggregated_risk:.2f}")
        print(f"   🔗 Agentes: {len(agent_route)}")
        print(f"   ⏱️  Tiempo: {processing_time:.2f}ms")
        print("="*60 + "\n")

        # ============================================
        # PERSISTIR EN BASE DE DATOS
        # ============================================
        db = next(get_db())
        try:
            PersistenceService.save_transaction_analysis(
                db=db,
                transaction=transaction,
                decision=decision,
                confidence=confidence,
                risk_score=aggregated_risk,
                signals=all_signals[:10],
                citations_internal=citations_internal,
                citations_external=citations_external,
                explanation_customer=explanation_customer,
                explanation_audit=explanation_audit,
                agent_route=" → ".join(agent_route),
                processing_time_ms=processing_time
            )
        finally:
            db.close()
        
        response = DecisionResponse(
            transaction_id=transaction.transaction_id,
            decision=decision,
            confidence=confidence,
            signals=all_signals[:10],  # Limitar a 10 señales
            citations_internal=citations_internal,
            citations_external=citations_external,
            explanation_customer=explanation_customer,
            explanation_audit=explanation_audit,
            agent_route=" → ".join(agent_route),
            processing_time_ms=processing_time
        )
        
        return response
        
    except Exception as e:
        print(f"\n   ❌ ERROR en el sistema multi-agente: {str(e)}")
        import traceback
        print("\n   📋 Traceback completo:")
        traceback.print_exc()
        
        # Retornar respuesta de error
        processing_time = (time.time() - start_time) * 1000
        
        return DecisionResponse(
            transaction_id=transaction.transaction_id,
            decision=DecisionType.ESCALATE_TO_HUMAN,
            confidence=0.0,
            signals=[f"Error en análisis multi-agente: {str(e)}"],
            citations_internal=[],
            citations_external=[],
            explanation_customer="Su transacción está en revisión manual debido a un error técnico.",
            explanation_audit=f"Error al procesar: {str(e)}",
            agent_route="Error Handler",
            processing_time_ms=processing_time
        )

@app.post(
    f"{settings.API_V1_PREFIX}/transactions/analyze-stream",
    summary="Analizar transacción con streaming en tiempo real",
    dependencies=[Depends(verify_api_key_and_jwt)]
)
async def analyze_transaction_stream(
    request: TransactionAnalysisRequest,     
    current_user: dict = Depends(get_current_user)  
):
    """
    Analiza una transacción con streaming de logs en tiempo real (SSE)
    """
    
    async def event_generator():
        """Generador de eventos SSE"""
        import time
        
        start_time = time.time()
        
        transaction = request.transaction
        customer_behavior = request.customer_behavior

        # Variable para almacenar logs
        analysis_logs = []  # ← AGREGAR ESTO
        
        # Header
        log_event = {
                "event_type": "phase",
                "phase": "INICIO",
                "message": f"Analizando transacción: {transaction.transaction_id}"
            }
        analysis_logs.append(log_event)
        yield await StreamingService.emit_phase("INICIO", log_event["message"])

        """ yield await StreamingService.emit_phase(
            "INICIO",
            f"🔍 Analizando transacción: {transaction.transaction_id}"
        ) """
        
        # Cargar comportamiento del cliente
        if not customer_behavior:
            behavior_data = load_customer_behavior(transaction.customer_id)
            if behavior_data:
                from app.models.schemas import CustomerBehavior
                customer_behavior = CustomerBehavior(**behavior_data)
                yield await StreamingService.emit_info("Comportamiento del cliente cargado")
        
        try:
            from app.agents.transaction_context_agent import TransactionContextAgent
            from app.agents.behavioral_pattern_agent import BehavioralPatternAgent
            from app.agents.policy_rag_agent import PolicyRAGAgent
            from app.agents.threat_intel_agent import ThreatIntelAgent
            from app.agents.evidence_aggregation_agent import EvidenceAggregationAgent
            from app.agents.debate_agents import DebateAgents
            
            agent_route = []
            citations_internal = []
            citations_external = []
            
            # Helper para log + yield
            async def log_and_emit(event_type, message, phase=None, agent=None, data=None):
                analysis_logs.append({
                    "event_type": event_type,
                    "phase": phase,
                    "agent": agent,
                    "message": message,
                    "data": data
                })
                
                if event_type == "phase":
                    return await StreamingService.emit_phase(phase, message)
                elif event_type == "agent":
                    return await StreamingService.emit_agent(agent, message, data)
                elif event_type == "success":
                    return await StreamingService.emit_success(message, data)
                elif event_type == "info":
                    return await StreamingService.emit_info(message)
                elif event_type == "complete":
                    return await StreamingService.emit_complete(message, data)
            
            # FASE 1
            yield await log_and_emit("phase", "FASE 1: Análisis de Contexto", phase="FASE_1")
            context_agent = TransactionContextAgent()
            context_result = context_agent.analyze(transaction, customer_behavior)
            agent_route.append(context_result.get("agent"))
            yield await log_and_emit(
                "success",
                f"Riesgo: {context_result.get('risk_level')}",
                data={"risk_level": context_result.get('risk_level')}
            )
            
            # FASE 2
            yield await log_and_emit("phase", "FASE 2: Análisis de Patrones", phase="FASE_2")
            behavioral_agent = BehavioralPatternAgent()
            behavioral_result = behavioral_agent.analyze(
                transaction, customer_behavior,
                context_signals=context_result.get("signals", [])
            )
            agent_route.append(behavioral_result.get("agent"))
            yield await log_and_emit(
                "success",
                f"Score: {behavioral_result.get('behavioral_score', 0):.2f}",
                data={"behavioral_score": behavioral_result.get('behavioral_score', 0)}
            )
            
            # FASE 3
            yield await log_and_emit("phase", "FASE 3: Consulta de Políticas", phase="FASE_3")
            policy_agent = PolicyRAGAgent()
            policy_result = policy_agent.analyze(
                transaction, customer_behavior,
                context_signals=context_result.get("signals", []),
                behavioral_anomalies=behavioral_result.get("anomalies", [])
            )
            agent_route.append(policy_result.get("agent"))
            
            for policy in policy_result.get("applicable_policies", []):
                from app.models.schemas import InternalCitation
                citations_internal.append(InternalCitation(
                    policy_id=policy["policy_id"],
                    chunk_id=policy.get("chunk_id", "1"),
                    version=policy["version"]
                ))
            
            yield await log_and_emit(
                "success",
                f"Políticas aplicables: {len(policy_result.get('applicable_policies', []))}",
                data={"policies_count": len(policy_result.get('applicable_policies', []))}
            )
            
            # FASE 4
            yield await log_and_emit("phase", "FASE 4: Inteligencia de Amenazas", phase="FASE_4")
            threat_agent = ThreatIntelAgent()
            threat_result = threat_agent.analyze(
                transaction,
                context_signals=context_result.get("signals", [])
            )
            agent_route.append(threat_result.get("agent"))
            
            for source in threat_result.get("sources", []):
                from app.models.schemas import ExternalCitation
                citations_external.append(ExternalCitation(
                    url=source["url"],
                    summary=source["summary"]
                ))
            
            yield await log_and_emit(
                "success",
                f"Amenazas encontradas: {len(threat_result.get('threats_found', []))}",
                data={"threats_count": len(threat_result.get('threats_found', []))}
            )
            
            # FASE 5
            yield await log_and_emit("phase", "FASE 5: Agregación de Evidencias", phase="FASE_5")
            evidence_agent = EvidenceAggregationAgent()
            evidence_result = evidence_agent.analyze(
                context_result, behavioral_result,
                policy_result, threat_result
            )
            agent_route.append(evidence_result.get("agent"))
            
            all_signals = evidence_result.get("all_signals", [])
            aggregated_risk = evidence_result.get("aggregated_risk_score", 0.5)
            yield await log_and_emit(
                "success",
                f"Risk Score: {aggregated_risk:.2f}",
                data={"risk_score": aggregated_risk, "signals_count": len(all_signals)}
            )
            
            # FASE 6: Debate y Decisión
            yield await log_and_emit("phase", "FASE 6: Debate y Decisión", phase="FASE_6")
            debate_agents = DebateAgents()
            debate_result = debate_agents.analyze(
                transaction.transaction_id,
                all_signals,
                aggregated_risk,
                citations_internal,
                citations_external
            )
            agent_route.append(debate_result.get("agent"))
            yield await log_and_emit("success", "Debate y decisión completados")

            # Obtener decisión y explicaciones del debate
            decision_str = debate_result.get("decision_recommendation", "APPROVE")
            decision = DecisionType[decision_str]  # Convertir string a enum

            explanation_customer = debate_result.get("explanation_customer", "...")
            explanation_audit = debate_result.get("explanation_audit", "...")

            # Calcular confianza basada en risk score
            if aggregated_risk >= 0.75:
                confidence = 0.95
            elif aggregated_risk >= 0.55:
                confidence = 0.75
            elif aggregated_risk >= 0.35:
                confidence = 0.70
            else:
                confidence = 0.90
            
            # FASE 7: Log de decisión final
            yield await log_and_emit(
                "phase", 
                f"FASE 7: Decisión Final - {decision.value}", 
                phase="FASE_7"
            )
            
            # Calcular tiempo de procesamiento
            processing_time = (time.time() - start_time) * 1000
            
            # HITL
            should_escalate_to_hitl = (
                decision == DecisionType.ESCALATE_TO_HUMAN or
                (decision == DecisionType.BLOCK and confidence < 0.95) or
                (decision == DecisionType.CHALLENGE and aggregated_risk > 0.5) or
                (len(citations_external) > 0 and aggregated_risk > 0.7)
            )
            
            if should_escalate_to_hitl:
                yield await log_and_emit("phase", "FASE 8: Escalando a HITL", phase="FASE_8")
                from app.services.hitl_service import get_hitl_service
                hitl_service = get_hitl_service()
                hitl_case = hitl_service.create_case(
                    transaction=transaction,
                    decision_recommendation=decision,
                    confidence=confidence,
                    signals=all_signals[:10],
                    citations_internal=citations_internal,
                    citations_external=citations_external,
                    agent_route=" → ".join(agent_route),
                    created_by=current_user["username"]
                )
                yield await log_and_emit("info", f"Caso HITL creado: {hitl_case.case_id}")
                
                # Agregar referencia al caso en la explicación del cliente
                explanation_customer += f" Caso: {hitl_case.case_id}"
            
            # Agregar tiempo de procesamiento a la explicación de auditoría
            explanation_audit += f" | Tiempo: {processing_time:.0f}ms"
            
            # Persistir
            db = next(get_db())
            try:
                # Guardar análisis
                decision_db = PersistenceService.save_transaction_analysis(
                    db=db, transaction=transaction, decision=decision,
                    confidence=confidence, risk_score=aggregated_risk,
                    signals=all_signals[:10], citations_internal=citations_internal,
                    citations_external=citations_external,
                    explanation_customer=explanation_customer,
                    explanation_audit=explanation_audit,
                    agent_route=" → ".join(agent_route),
                    processing_time_ms=processing_time
                )
                
                # Guardar logs de análisis
                for log in analysis_logs:
                    PersistenceService.save_analysis_log(
                        db=db,
                        decision_id=decision_db.id,
                        event_type=log["event_type"],
                        message=log["message"],
                        phase=log.get("phase"),
                        agent=log.get("agent"),
                        event_data=log.get("data")
                    )
                
                db.commit()
                
            finally:
                db.close()
            
            # Resultado final
            response_data = {
                "transaction_id": transaction.transaction_id,
                "decision": decision.value,
                "confidence": confidence,
                "signals": all_signals[:10],
                "citations_internal": [
                    {"policy_id": c.policy_id, "version": c.version, "chunk_id": c.chunk_id}
                    for c in citations_internal
                ],
                "citations_external": [
                    {"url": c.url, "summary": c.summary}
                    for c in citations_external
                ],
                "risk_score": aggregated_risk,
                "processing_time_ms": processing_time,
                "agent_route": agent_route
            }
            
            yield await log_and_emit(
                "complete",
                f"Análisis completado - Decisión: {decision.value}",
                data=response_data
            )
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            
            print(f"\n❌ ERROR en análisis: {str(e)}")
            print(f"   Traceback:\n{error_detail}")
            
            yield await StreamingService.emit_error(
                f"Error en análisis: {str(e)}"
            )
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# ============================================
# EVENTOS
# ============================================

@app.on_event("startup")
async def startup_event():
    """Ejecutar al iniciar la aplicación"""
    print("=" * 60)
    print(f"🚀 {settings.PROJECT_NAME}")
    print(f"📌 Version: {settings.VERSION}")
    print(f"🤖 LLM Provider: {settings.LLM_PROVIDER.upper()}")
    print(f"🌐 API docs: http://localhost:8000/docs")
    print(f"📚 ReDoc: http://localhost:8000/redoc")
    print("=" * 60)

    # Inicializar base de datos
    init_db()

    

@app.on_event("shutdown")
async def shutdown_event():
    """Ejecutar al apagar la aplicación"""
    print("👋 Cerrando aplicación...")