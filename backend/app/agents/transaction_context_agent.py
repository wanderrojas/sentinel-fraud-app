"""
Transaction Context Agent
Analiza las señales internas de una transacción usando LLM
"""
from app.models.schemas import Transaction, CustomerBehavior
from app.services.llm_service import get_llm
#from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, List
from datetime import datetime


class TransactionContextAgent:
    """
    Agente que analiza el contexto de una transacción
    y detecta señales sospechosas usando IA
    """
    
    def __init__(self):
        self.llm = get_llm(temperature=0.3)  # Temperatura baja para análisis
        self.name = "Transaction Context Agent"
        
    def analyze(
        self,
        transaction: Transaction,
        customer_behavior: CustomerBehavior = None
    ) -> Dict:
        """
        Analizar una transacción y detectar señales
        
        Args:
            transaction: Datos de la transacción
            customer_behavior: Comportamiento habitual del cliente
        
        Returns:
            Dict con señales detectadas y análisis
        """
        
        print(f"\n🤖 {self.name} iniciando análisis...")
        
        # Construir contexto
        context = self._build_context(transaction, customer_behavior)
        
        # Crear prompt
        prompt = self._create_prompt(context)
        
        # Invocar LLM
        print("   📡 Consultando al LLM...")
        response = self.llm.invoke(prompt)

        # Validar respuesta
        if response is None or not hasattr(response, "content") or response.content is None:
            print("⚠️ LLM no devolvió respuesta válida")
            return {
                "agent": self.name,
                "signals": [],
                "risk_level": "LOW",
                "summary": "",
                "raw_response": None
            }

        
        # Parsear respuesta
        analysis = self._parse_response(response.content)
        
        print(f"   ✅ Análisis completado - Riesgo: {analysis.get('risk_level', 'LOW')}")
        
        return {
            "agent": self.name,
            "signals": analysis.get("signals", []),
            "risk_level": analysis.get("risk_level", "LOW"),
            "summary": analysis.get("summary", ""),
            "raw_response": response.content
        }
    
    def _build_context(
        self,
        transaction: Transaction,
        customer_behavior: CustomerBehavior = None
    ) -> str:
        """Construir contexto para el prompt"""
        
        context = f"""
DATOS DE LA TRANSACCIÓN:
- ID: {transaction.transaction_id}
- Cliente: {transaction.customer_id}
- Monto: {transaction.amount} {transaction.currency}
- País: {transaction.country}
- Canal: {transaction.channel}
- Dispositivo: {transaction.device_id}
- Hora: {transaction.timestamp.strftime('%H:%M:%S')}
- Día de la semana: {transaction.timestamp.strftime('%A')}
- Comercio: {transaction.merchant_id}
"""
        
        if customer_behavior:
            # Calcular ratio de monto
            ratio = transaction.amount / customer_behavior.usual_amount_avg
            
            # Verificar horario
            hour = transaction.timestamp.hour
            usual_hours = customer_behavior.usual_hours.split("-")
            start_hour = int(usual_hours[0])
            end_hour = int(usual_hours[1])
            in_usual_hours = start_hour <= hour <= end_hour
            
            # Verificar dispositivo
            is_usual_device = transaction.device_id in customer_behavior.usual_devices
            
            context += f"""
COMPORTAMIENTO HABITUAL DEL CLIENTE:
- Monto promedio: {customer_behavior.usual_amount_avg} {transaction.currency}
- Ratio monto actual/promedio: {ratio:.2f}x
- Horario habitual: {customer_behavior.usual_hours}
- ¿Está en horario habitual?: {'Sí' if in_usual_hours else 'No'}
- Países habituales: {customer_behavior.usual_countries}
- Dispositivos habituales: {customer_behavior.usual_devices}
- ¿Es dispositivo habitual?: {'Sí' if is_usual_device else 'No'}
"""
        
        return context
    
    def _create_prompt(self, context: str) -> str:
        """Crear prompt para el LLM"""
        
        template = ChatPromptTemplate.from_messages([
            ("system", """Eres un experto analista de fraude financiero del BCP (Banco de Crédito del Perú). 
Tu tarea es analizar transacciones y detectar señales sospechosas que puedan indicar fraude.

Debes analizar cuidadosamente:
1. **Monto**: ¿Es inusualmente alto comparado con el promedio del cliente?
2. **Horario**: ¿La transacción ocurre en un horario atípico?
3. **Dispositivo**: ¿Se está usando un dispositivo nuevo o desconocido?
4. **País**: ¿Es diferente al país habitual del cliente?
5. **Patrón general**: ¿Hay algo más que no cuadra?

IMPORTANTE: Sé específico y objetivo. Base tu análisis en los datos proporcionados.

Responde EXACTAMENTE en este formato:

SEÑALES DETECTADAS:
- [Lista cada señal sospechosa encontrada. Si no hay ninguna, escribe "Sin señales sospechosas"]

NIVEL DE RIESGO: [LOW/MEDIUM/HIGH]

RESUMEN:
[Resumen breve del análisis en 2-3 líneas, explicando por qué llegaste a esa conclusión]"""),
            ("user", "{context}")
        ])
        
        return template.format_messages(context=context)
    
    def _parse_response(self, response: str) -> Dict:
        if not response:
            return {"signals": [], "risk_level": "LOW", "summary": ""}
        
        signals = []
        risk_level = "LOW"
        summary = ""
        
        lines = response.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if "SEÑALES DETECTADAS:" in line:
                current_section = "signals"
                continue
            elif "NIVEL DE RIESGO:" in line:
                current_section = "risk"
                # Extraer nivel de riesgo
                if "HIGH" in line.upper():
                    risk_level = "HIGH"
                elif "MEDIUM" in line.upper():
                    risk_level = "MEDIUM"
                else:
                    risk_level = "LOW"
                continue
            elif "RESUMEN:" in line:
                current_section = "summary"
                continue
            
            # Procesar contenido según sección
            if current_section == "signals" and line.startswith("-"):
                signal = line[1:].strip()
                if signal and "sin señales" not in signal.lower():
                    signals.append(signal)
            elif current_section == "summary" and line:
                summary += line + " "
        
        return {
            "signals": signals,
            "risk_level": risk_level,
            "summary": summary.strip()
        }