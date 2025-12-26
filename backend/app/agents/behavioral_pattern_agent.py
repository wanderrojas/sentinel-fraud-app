"""
Behavioral Pattern Agent
Analiza los patrones de comportamiento del cliente y detecta anomalías
"""
from app.models.schemas import Transaction, CustomerBehavior
from app.services.llm_service import get_llm
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, List
from datetime import datetime


class BehavioralPatternAgent:
    """
    Agente que analiza patrones de comportamiento del cliente
    y detecta desviaciones significativas
    """
    
    def __init__(self):
        self.llm = get_llm(temperature=0.2)  # Temperatura muy baja para análisis objetivo
        self.name = "Behavioral Pattern Agent"
        
    def analyze(
        self,
        transaction: Transaction,
        customer_behavior: CustomerBehavior,
        context_signals: List[str] = None
    ) -> Dict:
        """
        Analizar patrones de comportamiento
        
        Args:
            transaction: Datos de la transacción
            customer_behavior: Comportamiento habitual del cliente
            context_signals: Señales del Transaction Context Agent (opcional)
        
        Returns:
            Dict con análisis de patrones
        """
        
        print(f"\n🤖 {self.name} iniciando análisis...")
        
        if not customer_behavior:
            print("   ⚠️  Sin datos de comportamiento, análisis limitado")
            return {
                "agent": self.name,
                "patterns_analyzed": [],
                "anomalies": ["Sin datos históricos del cliente"],
                "behavioral_score": 0.5,
                "summary": "No hay suficiente información histórica para análisis de patrones"
            }
        
        # Calcular métricas de comportamiento
        metrics = self._calculate_behavioral_metrics(transaction, customer_behavior)
        
        # Construir contexto
        context = self._build_context(transaction, customer_behavior, metrics, context_signals)
        
        # Crear prompt
        prompt = self._create_prompt(context)
        
        # Invocar LLM
        print("   📡 Consultando al LLM para análisis de patrones...")
        response = self.llm.invoke(prompt)
        
        # Parsear respuesta
        analysis = self._parse_response(response.content)
        
        # Agregar métricas calculadas
        analysis["metrics"] = metrics
        analysis["behavioral_score"] = self._calculate_behavioral_score(metrics)
        
        print(f"   ✅ Análisis completado - Score: {analysis['behavioral_score']:.2f}")
        
        return {
            "agent": self.name,
            "patterns_analyzed": analysis.get("patterns", []),
            "anomalies": analysis.get("anomalies", []),
            "behavioral_score": analysis["behavioral_score"],
            "summary": analysis.get("summary", ""),
            "metrics": metrics,
            "raw_response": response.content
        }
    
    def _calculate_behavioral_metrics(
        self,
        transaction: Transaction,
        customer_behavior: CustomerBehavior
    ) -> Dict:
        """Calcular métricas de comportamiento"""
        
        # Ratio de monto
        amount_ratio = transaction.amount / customer_behavior.usual_amount_avg
        
        # Verificar horario
        hour = transaction.timestamp.hour
        usual_hours = customer_behavior.usual_hours.split("-")
        start_hour = int(usual_hours[0])
        end_hour = int(usual_hours[1])
        
        # Calcular desviación de horario
        if start_hour <= hour <= end_hour:
            hour_deviation = 0
            in_usual_hours = True
        else:
            # Calcular cuántas horas fuera del rango
            if hour < start_hour:
                hour_deviation = start_hour - hour
            else:
                hour_deviation = hour - end_hour
            in_usual_hours = False
        
        # Verificar dispositivo
        is_usual_device = transaction.device_id in customer_behavior.usual_devices
        
        # Verificar país
        is_usual_country = transaction.country in customer_behavior.usual_countries
        
        # Verificar canal
        # Asumimos que todos los canales son normales por ahora
        is_usual_channel = True
        
        # Día de la semana
        weekday = transaction.timestamp.strftime('%A')
        is_weekend = weekday in ['Saturday', 'Sunday']
        
        return {
            "amount_ratio": round(amount_ratio, 2),
            "amount_deviation_pct": round((amount_ratio - 1) * 100, 2),
            "in_usual_hours": in_usual_hours,
            "hour_deviation": hour_deviation,
            "is_usual_device": is_usual_device,
            "is_usual_country": is_usual_country,
            "is_usual_channel": is_usual_channel,
            "is_weekend": is_weekend,
            "transaction_hour": hour,
            "weekday": weekday
        }
    
    def _calculate_behavioral_score(self, metrics: Dict) -> float:
        """
        Calcular score de comportamiento (0 = muy anómalo, 1 = muy normal)
        """
        score = 1.0
        
        # Penalizar SOLO por monto ALTO (no por monto bajo)
        if metrics["amount_ratio"] > 5.0:
            score -= 0.4
        elif metrics["amount_ratio"] > 3.0:
            score -= 0.2
        elif metrics["amount_ratio"] > 2.0:
            score -= 0.1
        # NO penalizar por monto bajo (< 1.0)
        
        # Penalizar MÁS por horario atípico
        if not metrics["in_usual_hours"]:
            if metrics["hour_deviation"] > 6:
                score -= 0.5
            elif metrics["hour_deviation"] > 3:
                score -= 0.4
            else:
                score -= 0.3
        
        # Penalizar por dispositivo nuevo
        if not metrics["is_usual_device"]:
            score -= 0.25
        
        # Penalizar por país diferente
        if not metrics["is_usual_country"]:
            score -= 0.3
        
        # SOLO aplicar techo si horario atípico
        if not metrics["in_usual_hours"]:
            score = min(score, 0.60)
        
        return max(0.0, min(1.0, score))
    
    def _build_context(
        self,
        transaction: Transaction,
        customer_behavior: CustomerBehavior,
        metrics: Dict,
        context_signals: List[str] = None
    ) -> str:
        """Construir contexto para el prompt"""
        
        context = f"""
TRANSACCIÓN ACTUAL:
- ID: {transaction.transaction_id}
- Cliente: {transaction.customer_id}
- Monto: {transaction.amount} {transaction.currency}
- Hora: {transaction.timestamp.strftime('%H:%M')} ({metrics['weekday']})
- Dispositivo: {transaction.device_id}
- País: {transaction.country}
- Canal: {transaction.channel}

PERFIL DEL CLIENTE (Comportamiento Habitual):
- Monto promedio: {customer_behavior.usual_amount_avg} {transaction.currency}
- Horario habitual: {customer_behavior.usual_hours}
- Países habituales: {customer_behavior.usual_countries}
- Dispositivos habituales: {customer_behavior.usual_devices}

MÉTRICAS CALCULADAS:
- Ratio monto actual/promedio: {metrics['amount_ratio']}x
- Desviación de monto: {metrics['amount_deviation_pct']:+.1f}%
- ¿En horario habitual?: {'Sí' if metrics['in_usual_hours'] else f"No (desviación: {metrics['hour_deviation']} horas)"}
- ¿Dispositivo habitual?: {'Sí' if metrics['is_usual_device'] else 'No (NUEVO)'}
- ¿País habitual?: {'Sí' if metrics['is_usual_country'] else 'No (DIFERENTE)'}
- ¿Fin de semana?: {'Sí' if metrics['is_weekend'] else 'No'}
- Score de comportamiento: {self._calculate_behavioral_score(metrics):.2f}
"""
        
        if context_signals:
            context += f"""
SEÑALES DEL AGENTE DE CONTEXTO:
{chr(10).join(f'- {signal}' for signal in context_signals)}
"""
        
        return context
    
    def _create_prompt(self, context: str) -> str:
        """Crear prompt para el LLM"""
        
        template = ChatPromptTemplate.from_messages([
            ("system", """Eres un experto en análisis de comportamiento de clientes bancarios del BCP.
Tu especialidad es detectar anomalías en patrones de comportamiento que puedan indicar fraude.

Analiza cuidadosamente:
1. **Desviación de monto**: ¿Qué tan diferente es del comportamiento habitual?
2. **Patrón temporal**: ¿El horario y día son consistentes con su historial?
3. **Dispositivos y ubicación**: ¿Hay cambios sospechosos?
4. **Contexto general**: ¿Esta transacción encaja en el perfil del cliente?

IMPORTANTE: 
- Sé específico con los números (ej: "3.6x el promedio habitual")
- Menciona TODAS las anomalías detectadas
- Si el comportamiento es normal, di "Comportamiento consistente con el perfil"

Responde EXACTAMENTE en este formato:

PATRONES ANALIZADOS:
- [Lista cada aspecto del comportamiento analizado]

ANOMALÍAS DETECTADAS:
- [Lista cada desviación significativa. Si no hay anomalías, escribe "Sin anomalías significativas"]

RESUMEN:
[Resumen breve en 2-3 líneas sobre si el comportamiento es consistente o anómalo y por qué]"""),
            ("user", "{context}")
        ])
        
        return template.format_messages(context=context)
    
    def _parse_response(self, response: str) -> Dict:
        """Parsear la respuesta del LLM"""
        
        patterns = []
        anomalies = []
        summary = ""
        
        lines = response.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if "PATRONES ANALIZADOS:" in line:
                current_section = "patterns"
                continue
            elif "ANOMALÍAS DETECTADAS:" in line or "ANOMALIAS DETECTADAS:" in line:
                current_section = "anomalies"
                continue
            elif "RESUMEN:" in line:
                current_section = "summary"
                continue
            
            # Procesar contenido según sección
            if current_section == "patterns" and line.startswith("-"):
                pattern = line[1:].strip()
                if pattern:
                    patterns.append(pattern)
            elif current_section == "anomalies" and line.startswith("-"):
                anomaly = line[1:].strip()
                if anomaly and "sin anomalías" not in anomaly.lower():
                    anomalies.append(anomaly)
            elif current_section == "summary" and line:
                summary += line + " "
        
        return {
            "patterns": patterns,
            "anomalies": anomalies,
            "summary": summary.strip()
        }