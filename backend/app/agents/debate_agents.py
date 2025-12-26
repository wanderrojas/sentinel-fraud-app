"""
Debate Agents
Pro-Fraud Agent vs Pro-Customer Agent
"""
from app.services.llm_service import get_llm
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, List


class DebateAgents:
    """
    Sistema de debate: Pro-Fraud vs Pro-Customer
    """
    
    def __init__(self):
        self.llm = get_llm(temperature=0.5)
        self.name = "Debate Agents"
    
    def analyze(
        self,
        transaction_id: str,
        all_signals: List[str],
        aggregated_risk_score: float,
        citations_internal: List,
        citations_external: List
    ) -> Dict:
        """
        Ejecutar debate entre agentes Pro-Fraud y Pro-Customer
        y decidir acción final mediante Decision Arbiter
        
        Returns:
            Dict con argumentos de debate, decisión final y explicaciones
        """
        
        print(f"\n🤖 {self.name} iniciando debate...")
        
        # ============================================
        # PASO 1: CONSTRUIR CONTEXTO
        # ============================================
        
        context = f"""
TRANSACCIÓN: {transaction_id}
RISK SCORE: {aggregated_risk_score:.2f}

SEÑALES DETECTADAS ({len(all_signals)}):
{chr(10).join(f'- {signal}' for signal in all_signals[:10])}

POLÍTICAS CITADAS: {len(citations_internal)}
ALERTAS EXTERNAS: {len(citations_external)}
"""
        
        # ============================================
        # PASO 2: GENERAR ARGUMENTOS DE DEBATE
        # ============================================
        
        debate_prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un sistema de análisis de fraude que presenta AMBOS lados del argumento.

Genera DOS argumentos balanceados y objetivos:

1. PRO-FRAUD (Por qué ES fraude):
Argumenta fuertemente que esta transacción ES fraudulenta, basándote en las señales detectadas.
Sé específico con los datos (montos, porcentajes, etc.)

2. PRO-CUSTOMER (Por qué NO es fraude):
Argumenta fuertemente que esta transacción es LEGÍTIMA, buscando explicaciones razonables.
Considera escenarios normales que podrían explicar las anomalías.

Formato:
PRO-FRAUD: [2-3 líneas]

PRO-CUSTOMER: [2-3 líneas]"""),
            ("user", "{context}")
        ])
        
        print("   📡 Generando argumentos de debate...")
        debate_response = self.llm.invoke(debate_prompt.format_messages(context=context))
        
        # Parsear argumentos
        content = debate_response.content
        pro_fraud_arg = ""
        pro_customer_arg = ""
        
        if "PRO-FRAUD" in content and "PRO-CUSTOMER" in content:
            parts = content.split("PRO-CUSTOMER")
            pro_fraud_part = parts[0].replace("PRO-FRAUD", "").replace("1.", "").strip()
            pro_customer_part = parts[1].replace("2.", "").strip()
            
            # Limpiar
            pro_fraud_arg = pro_fraud_part.strip(": ").strip()
            pro_customer_arg = pro_customer_part.strip(": ").strip()
        
        print(f"   ✅ Debate completado")
        
        # ============================================
        # PASO 3: DECISION ARBITER (IA DECIDE)
        # ============================================
        
        print("   ⚖️  Decision Arbiter evaluando...")
        
        final_decision = self._decision_arbiter(
            aggregated_risk_score=aggregated_risk_score,
            pro_fraud_argument=pro_fraud_arg,
            pro_customer_argument=pro_customer_arg,
            signals=all_signals,
            policies=citations_internal,
            threats=citations_external
        )
        
        print(f"   ✅ Decisión final: {final_decision}")
        
        # ============================================
        # PASO 4: GENERAR EXPLICACIONES
        # ============================================
        
        print("   📝 Generando explicaciones...")
        
        # Generar explicación para el cliente
        customer_explanation = self._generate_customer_explanation(
            final_decision, aggregated_risk_score, all_signals
        )
        
        # Generar explicación para auditoría
        audit_explanation = self._generate_audit_explanation(
            transaction_id, final_decision, aggregated_risk_score, all_signals,
            citations_internal, citations_external
        )
        
        print("   ✅ Explicaciones generadas")
        
        # ============================================
        # RETORNO COMPLETO
        # ============================================
        
        return {
            "agent": self.name,
            "debate_summary": debate_response.content,
            "pro_fraud_argument": pro_fraud_arg,
            "pro_customer_argument": pro_customer_arg,
            "decision_recommendation": final_decision,  # ← DECISIÓN DE IA
            "explanation_customer": customer_explanation,
            "explanation_audit": audit_explanation
        }
    
    def _decision_arbiter(
        self,
        aggregated_risk_score: float,
        pro_fraud_argument: str,
        pro_customer_argument: str,
        signals: List[str],
        policies: List,
        threats: List
    ) -> str:
        """
        Decision Arbiter: La IA toma la decisión final basándose en el debate
        """
        
        # Preparar contexto para el Arbiter
        context = f"""
RISK SCORE CALCULADO: {aggregated_risk_score:.2f} (0.0 = sin riesgo, 1.0 = muy alto riesgo)

ARGUMENTO PRO-FRAUD (por qué podría SER fraude):
{pro_fraud_argument}

ARGUMENTO PRO-CUSTOMER (por qué podría ser LEGÍTIMO):
{pro_customer_argument}

INFORMACIÓN ADICIONAL:
- Total de señales detectadas: {len(signals)}
- Políticas internas aplicadas: {len(policies)}
- Alertas de amenazas externas: {len(threats)}

POLÍTICAS APLICADAS:
{chr(10).join(f"- {p.policy_id if hasattr(p, 'policy_id') else p.get('policy_id')}" for p in policies) if policies else "- Ninguna"}
"""
        
        # Prompt para el Decision Arbiter
        arbiter_prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres el Decision Arbiter del Sistema de Detección de Fraude del BCP.

Tu responsabilidad es tomar la DECISIÓN FINAL sobre cada transacción.

CONTEXTO IMPORTANTE:
- El sistema ya calculó un risk score (0.0 = sin riesgo, 1.0 = alto riesgo)
- Ya analizó 6 agentes especializados
- Ya aplicó todas las políticas bancarias
- Ya consultó amenazas externas

Tu trabajo es CONFIRMAR o AJUSTAR esa evaluación basándote en el contexto completo.

OPCIONES DE DECISIÓN:

**APPROVE**
- Usar cuando la transacción es claramente legítima
- EJEMPLOS DE CUÁNDO APROBAR:
  * Risk score < 0.20
  * Behavioral score >= 0.95
  * Sin políticas aplicadas
  * Sin amenazas externas
  * Monto dentro de ±50% del promedio
  * Dispositivo conocido, país habitual, horario normal

**CHALLENGE**
- Usar cuando hay dudas razonables
- EJEMPLOS DE CUÁNDO DESAFIAR:
  * Risk score 0.35-0.60
  * 2+ anomalías moderadas juntas
  * Monto muy alto (3x+) aunque todo lo demás sea normal
  * Horario muy inusual (madrugada) aunque solo eso sea raro

**BLOCK**
- Usar cuando hay alto riesgo de fraude
- EJEMPLOS DE CUÁNDO BLOQUEAR:
  * Risk score > 0.70
  * Monto alto + país diferente + dispositivo nuevo
  * Comercio en lista negra + múltiples anomalías

**ESCALATE_TO_HUMAN**
- Usar para casos complejos
- EJEMPLOS DE CUÁNDO ESCALAR:
  * Risk score 0.60-0.80 con señales contradictorias
  * Múltiples políticas aplicadas
  * Amenazas críticas + otras señales

REGLAS ABSOLUTAS (NUNCA VIOLAR):

1. **Si risk score = 0.0 y behavioral score = 1.0 → SIEMPRE APPROVE**
   - Esto significa: TODO está perfecto
   - No importa si hay señales de "monitoreo" o "seguimiento"
   - Esas son sugerencias generales, no alarmas

2. **Si risk score < 0.20 y behavioral score >= 0.90 → APPROVE**
   - A menos que haya políticas críticas aplicadas
   - O amenazas externas confirmadas

3. **MONTO BAJO (-30% o más) NUNCA es crítico por sí solo**
   - Cliente puede comprar algo pequeño
   - No usar CHALLENGE solo por monto bajo

4. **Ignora frases genéricas como:**
   - "Monitorear la transacción..."
   - "Realizar seguimiento..."
   - "Confirmar legitimidad..."
   - Estas son recomendaciones pasivas, NO alarmas

5. **Solo considera SEÑALES CRÍTICAS:**
   - Monto > 3x promedio
   - País diferente al habitual
   - Dispositivo completamente nuevo
   - Horario de madrugada (2-5 AM)
   - Comercio en lista negra
   - Políticas bancarias violadas

6. **Balance costo-beneficio:**
   - APPROVE cuando hay > 90% confianza de legitimidad
   - CHALLENGE solo cuando hay > 30% probabilidad de fraude
   - BLOCK solo cuando hay > 70% probabilidad de fraude

7. **Confía en los agentes anteriores:**
   - Si calcularon risk = 0.0, es porque analizaron TODO
   - No "inventes" riesgos que los agentes no detectaron

PROCESO DE DECISIÓN:

Paso 1: ¿Risk score < 0.20 Y behavioral score >= 0.90?
  → SÍ: APPROVE (salvo políticas/amenazas críticas)
  → NO: Continuar

Paso 2: ¿Hay políticas bancarias aplicadas?
  → SÍ: Seguir esas políticas
  → NO: Continuar

Paso 3: ¿Cuántas señales CRÍTICAS hay?
  → 0-1: APPROVE
  → 2: CHALLENGE
  → 3+: ESCALATE o BLOCK

RESPONDE SOLO CON UNA PALABRA:
APPROVE
CHALLENGE
BLOCK
ESCALATE_TO_HUMAN

NO agregues explicaciones."""),
            ("user", "{context}")
        ])
        
        # Invocar IA para decidir
        response = self.llm.invoke(arbiter_prompt.format_messages(context=context))
        decision_text = response.content.strip().upper()
        
        # Validar respuesta
        valid_decisions = ["APPROVE", "CHALLENGE", "BLOCK", "ESCALATE_TO_HUMAN"]
        
        if decision_text in valid_decisions:
            return decision_text
        
        # Fallback
        print(f"   ⚠️  Respuesta inesperada del Arbiter: '{decision_text}'. Usando fallback.")
        
        if aggregated_risk_score >= 0.75:
            return "BLOCK"
        elif aggregated_risk_score >= 0.55:
            return "ESCALATE_TO_HUMAN"
        elif aggregated_risk_score >= 0.35:
            return "CHALLENGE"
        else:
            return "APPROVE"
    
    
    def _generate_customer_explanation(
        self,
        decision: str,
        risk_score: float,
        signals: List[str]
    ) -> str:
        """Generar explicación para el cliente"""
        
        context = f"""
DECISIÓN: {decision}
RISK SCORE: {risk_score * 100:.0f}%

SEÑALES PRINCIPALES:
{chr(10).join(f'- {signal}' for signal in signals[:3])}
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un asistente del BCP que explica decisiones de seguridad al cliente.

Habla directamente al cliente sobre SU transacción. Máximo 2-3 líneas (40-60 palabras).

APPROVE: "Su transacción ha sido aprobada exitosamente. Gracias por confiar en BCP."

CHALLENGE: "Por su seguridad, confirme esta operación. Le enviaremos un código por SMS debido a [motivo principal breve]."

BLOCK: "Bloqueamos esta transacción por su seguridad debido a [motivo principal]. Si fue usted, llámenos al 0800-100-2000."

ESCALATE_TO_HUMAN: "Su transacción está en revisión por seguridad debido a [motivo principal]. La validaremos en 5-10 minutos."

NO uses términos técnicos como "IA", "risk score", "algoritmos". Sé claro, empático y conciso."""),
            ("user", "{context}")
        ])
        
        response = self.llm.invoke(prompt.format_messages(context=context))
        return response.content.strip()
    
    def _generate_audit_explanation(
        self,
        transaction_id: str,
        decision: str,
        risk_score: float,
        signals: List[str],
        policies: List,
        threats: List
    ) -> str:
        """Generar explicación técnica para auditoría"""
        
        policy_ids = [
            p.policy_id if hasattr(p, 'policy_id') else p.get('policy_id')
            for p in policies
        ] if policies else []
        
        # Identificar factores clave automáticamente
        key_factors = []
        signals_text = " ".join(signals).lower()
        
        if "monto" in signals_text and ("alto" in signals_text or "inusual" in signals_text or "elevado" in signals_text):
            key_factors.append("Monto elevado")
        if "horario" in signals_text and "atípico" in signals_text:
            key_factors.append("Horario atípico")
        if "dispositivo" in signals_text and ("nuevo" in signals_text or "desconocido" in signals_text):
            key_factors.append("Dispositivo no reconocido")
        if "país" in signals_text and ("diferente" in signals_text or "internacional" in signals_text):
            key_factors.append("Ubicación inusual")
        
        factors_text = ", ".join(key_factors) if key_factors else "Múltiples factores"
        policies_text = ", ".join(policy_ids) if policy_ids else "Ninguna"
        threats_text = f"{len(threats)}" if threats else "0"
        
        return (
            f"Decisión: {decision} (Risk Score: {risk_score * 100:.0f}%) | "
            f"Factores: {factors_text} | "
            f"Políticas: {policies_text} | "
            f"Alertas externas: {threats_text} | "
            f"Total señales: {len(signals)}"
        )