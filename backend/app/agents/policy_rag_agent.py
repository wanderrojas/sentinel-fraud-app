"""
Policy RAG Agent
Consulta políticas internas usando búsqueda vectorial (RAG)
"""
from app.models.schemas import Transaction, CustomerBehavior
from app.services.llm_service import get_llm
from app.services.rag_service import get_rag_service
#from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, List


class PolicyRAGAgent:
    """
    Agente que consulta políticas internas mediante RAG
    y determina qué políticas aplican a la transacción
    """
    
    def __init__(self):
        self.llm = get_llm(temperature=0.1)  # Muy baja para precisión
        self.name = "Policy RAG Agent"
        self.rag_service = get_rag_service()

    
    def _validate_policy_application(
        self,
        policy: Dict,
        transaction: Transaction,
        customer_behavior: CustomerBehavior
    ) -> bool:
        """
        Validar si una política realmente aplica según sus reglas específicas
        
        Args:
            policy: Política a validar
            transaction: Transacción actual
            customer_behavior: Comportamiento del cliente
        
        Returns:
            True si la política aplica, False si no
        """
        if not customer_behavior:
            return False
        
        policy_id = policy.get("policy_id")
        
        # FP-01: Monto > 3x promedio habitual Y horario fuera de rango → CHALLENGE
        if policy_id == "FP-01":
            amount_ratio = transaction.amount / customer_behavior.usual_amount_avg
            usual_hours = customer_behavior.usual_hours.split("-")
            start_hour = int(usual_hours[0])
            end_hour = int(usual_hours[1])
            current_hour = transaction.timestamp.hour
            
            is_high_amount = amount_ratio > 3.0
            is_unusual_time = not (start_hour <= current_hour <= end_hour)
            
            # Requiere AMBAS condiciones
            applies = is_high_amount and is_unusual_time
            
            if applies:
                print(f"   ✅ FP-01 validada: Monto {amount_ratio:.1f}x + horario {current_hour}h (fuera de {start_hour}-{end_hour})")
            else:
                print(f"   ❌ FP-01 rechazada: Monto {amount_ratio:.1f}x, horario {current_hour}h ({'OK' if not is_unusual_time else 'atípico'})")
            
            return applies
        
        # FP-02: Transacción internacional Y dispositivo nuevo → ESCALATE_TO_HUMAN
        elif policy_id == "FP-02":
            is_international = transaction.country not in customer_behavior.usual_countries
            is_new_device = transaction.device_id not in customer_behavior.usual_devices
            
            # Requiere AMBAS condiciones
            applies = is_international and is_new_device
            
            if applies:
                print(f"   ✅ FP-02 validada: País {transaction.country} (internacional) + dispositivo {transaction.device_id} (nuevo)")
            else:
                if not is_international:
                    print(f"   ❌ FP-02 rechazada: País {transaction.country} NO es internacional (habitual: {customer_behavior.usual_countries})")
                elif not is_new_device:
                    print(f"   ❌ FP-02 rechazada: Dispositivo {transaction.device_id} es conocido")
                else:
                    print(f"   ❌ FP-02 rechazada: No cumple ambas condiciones")
            
            return applies
        
        # Por defecto, aceptar políticas no conocidas
        return True

    def analyze(
        self,
        transaction: Transaction,
        customer_behavior: CustomerBehavior,
        context_signals: List[str] = None,
        behavioral_anomalies: List[str] = None
    ) -> Dict:
        """
        Consultar políticas relevantes y determinar aplicabilidad
        
        Args:
            transaction: Datos de la transacción
            customer_behavior: Comportamiento habitual del cliente
            context_signals: Señales del Context Agent
            behavioral_anomalies: Anomalías del Behavioral Agent
        
        Returns:
            Dict con políticas aplicables y recomendaciones
        """
        
        print(f"\n🤖 {self.name} iniciando análisis...")
        
        # Construir query para búsqueda vectorial
        search_query = self._build_search_query(
            transaction,
            customer_behavior,
            context_signals,
            behavioral_anomalies
        )
        
        print(f"   🔍 Query RAG: '{search_query}'")
        
        # Buscar políticas relevantes
        print("   📡 Buscando en base vectorial...")
        relevant_policies = self.rag_service.search_policies(
            query=search_query,
            n_results=3
        )
        
        print(f"   ✅ {len(relevant_policies)} políticas encontradas")
        
        if not relevant_policies:
            return {
                "agent": self.name,
                "policies_found": [],
                "applicable_policies": [],
                "recommendations": ["No se encontraron políticas aplicables"],
                "summary": "No se encontraron políticas relevantes en la base de conocimiento"
            }
        
        # Analizar aplicabilidad con LLM
        context = self._build_context(
            transaction,
            customer_behavior,
            relevant_policies,
            context_signals,
            behavioral_anomalies
        )
        
        prompt = self._create_prompt(context)
        
        print("   📡 Consultando al LLM para aplicabilidad de políticas...")
        response = self.llm.invoke(prompt)
        
        # Parsear respuesta
        analysis = self._parse_response(response.content, relevant_policies)
        
        # ============================================
        # VALIDACIÓN: Verificar que las políticas realmente apliquen
        # ============================================
        print("   🔍 Validando políticas aplicables...")
        
        validated_policies = []
        for policy in analysis["applicable_policies"]:
            is_valid = self._validate_policy_application(
                policy,
                transaction,
                customer_behavior
            )
            
            if is_valid:
                validated_policies.append(policy)
        
        # Actualizar con solo las políticas validadas
        analysis["applicable_policies"] = validated_policies
        
        print(f"   ✅ Políticas validadas: {len(validated_policies)}/{len(analysis['applicable_policies'])}")
        
        return {
            "agent": self.name,
            "policies_found": relevant_policies,
            "applicable_policies": validated_policies,  # ← Solo las validadas
            "recommendations": analysis["recommendations"],
            "summary": analysis["summary"],
            "raw_response": response.content
        }
    
    def _build_search_query(
        self,
        transaction: Transaction,
        customer_behavior: CustomerBehavior,
        context_signals: List[str] = None,
        behavioral_anomalies: List[str] = None
    ) -> str:
        """Construir query de búsqueda para ChromaDB"""
        
        # Calcular métricas básicas
        if customer_behavior:
            amount_ratio = transaction.amount / customer_behavior.usual_amount_avg
            hour = transaction.timestamp.hour
            usual_hours = customer_behavior.usual_hours.split("-")
            start_hour = int(usual_hours[0])
            end_hour = int(usual_hours[1])
            out_of_hours = not (start_hour <= hour <= end_hour)
        else:
            amount_ratio = 1.0
            out_of_hours = False
        
        # Construir query semántica
        query_parts = []
        
        if amount_ratio > 3:
            query_parts.append(f"monto {amount_ratio:.1f}x mayor al promedio")
        
        if out_of_hours:
            query_parts.append("horario fuera de rango habitual")
        
        if transaction.device_id not in (customer_behavior.usual_devices if customer_behavior else ""):
            query_parts.append("dispositivo nuevo")
        
        if transaction.country not in (customer_behavior.usual_countries if customer_behavior else ""):
            query_parts.append("país diferente")
        
        # Si no hay anomalías claras, usar señales previas
        if not query_parts and context_signals:
            query_parts.append(context_signals[0])
        
        if not query_parts:
            query_parts.append("transacción inusual")
        
        return " y ".join(query_parts)
    
    def _build_context(
        self,
        transaction: Transaction,
        customer_behavior: CustomerBehavior,
        policies: List[Dict],
        context_signals: List[str] = None,
        behavioral_anomalies: List[str] = None
    ) -> str:
        """Construir contexto para el prompt"""
        
        context = f"""
TRANSACCIÓN:
- ID: {transaction.transaction_id}
- Monto: {transaction.amount} {transaction.currency}
- Hora: {transaction.timestamp.strftime('%H:%M')}
- Dispositivo: {transaction.device_id}
- País: {transaction.country}
"""
        
        if customer_behavior:
            amount_ratio = transaction.amount / customer_behavior.usual_amount_avg
            context += f"""
COMPORTAMIENTO DEL CLIENTE:
- Monto promedio: {customer_behavior.usual_amount_avg} {transaction.currency}
- Ratio actual/promedio: {amount_ratio:.2f}x
- Horario habitual: {customer_behavior.usual_hours}
- Dispositivos habituales: {customer_behavior.usual_devices}
"""
        
        if context_signals:
            context += f"""
SEÑALES DE CONTEXTO:
{chr(10).join(f'- {signal}' for signal in context_signals)}
"""
        
        if behavioral_anomalies:
            context += f"""
ANOMALÍAS DE COMPORTAMIENTO:
{chr(10).join(f'- {anomaly}' for anomaly in behavioral_anomalies)}
"""
        
        context += f"""
POLÍTICAS INTERNAS ENCONTRADAS (de más a menos relevante):
"""
        
        for i, policy in enumerate(policies, 1):
            context += f"""
{i}. Política {policy['policy_id']} (v{policy['version']}) - Relevancia: {policy['relevance_score']:.2f}
   Regla: {policy['rule']}
"""
        
        return context
    
    def _create_prompt(self, context: str) -> str:
        """Crear prompt para el LLM"""
        
        template = ChatPromptTemplate.from_messages([
            ("system", """Eres un experto en políticas de fraude del BCP.
Tu tarea es determinar qué políticas internas aplican a una transacción específica.

Analiza cuidadosamente:
1. La transacción y el comportamiento del cliente
2. Las señales y anomalías detectadas
3. Las políticas encontradas en la base de conocimiento

Para cada política, determina:
- ¿Aplica a esta transacción?
- ¿Por qué sí o por qué no?
- ¿Qué acción recomienda?

Responde EXACTAMENTE en este formato:

POLÍTICAS APLICABLES:
- [Policy_ID]: [Explicación de por qué aplica y qué recomienda]
(Si ninguna aplica, escribe "Ninguna política aplica directamente")

RECOMENDACIONES:
- [Lista las acciones recomendadas basadas en las políticas]

RESUMEN:
[Resumen breve en 2-3 líneas sobre qué políticas aplican y por qué]"""),
            ("user", "{context}")
        ])
        
        return template.format_messages(context=context)
    
    def _parse_response(self, response: str, policies: List[Dict]) -> Dict:
        """Parsear la respuesta del LLM"""
        
        applicable_policies = []
        recommendations = []
        summary = ""
        
        lines = response.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if "POLÍTICAS APLICABLES:" in line or "POLITICAS APLICABLES:" in line:
                current_section = "policies"
                continue
            elif "RECOMENDACIONES:" in line:
                current_section = "recommendations"
                continue
            elif "RESUMEN:" in line:
                current_section = "summary"
                continue
            
            # Procesar contenido según sección
            if current_section == "policies" and line.startswith("-"):
                policy_line = line[1:].strip()
                if policy_line and "ninguna" not in policy_line.lower():
                    # Extraer policy_id si está presente
                    for policy in policies:
                        if policy["policy_id"] in policy_line:
                            applicable_policies.append({
                                "policy_id": policy["policy_id"],
                                "rule": policy["rule"],
                                "version": policy["version"],
                                "explanation": policy_line
                            })
                            break
            elif current_section == "recommendations" and line.startswith("-"):
                recommendation = line[1:].strip()
                if recommendation:
                    recommendations.append(recommendation)
            elif current_section == "summary" and line:
                summary += line + " "
        
        return {
            "applicable_policies": applicable_policies,
            "recommendations": recommendations,
            "summary": summary.strip()
        }