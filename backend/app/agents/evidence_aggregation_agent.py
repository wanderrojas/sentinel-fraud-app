"""
Evidence Aggregation Agent
Reúne todas las evidencias de los agentes anteriores
"""
from typing import Dict, List


class EvidenceAggregationAgent:
    """
    Agente que agrega toda la evidencia de los agentes previos
    """
    
    def __init__(self):
        self.name = "Evidence Aggregation Agent"
    
    def analyze(
        self,
        context_result: Dict,
        behavioral_result: Dict,
        policy_result: Dict,
        threat_result: Dict
    ) -> Dict:
        """
        Agregar todas las evidencias
        
        Returns:
            Dict con evidencia consolidada
        """
        
        print(f"\n🤖 {self.name} consolidando evidencias...")
        
        all_signals = []
        all_signals.extend(context_result.get("signals", []))
        all_signals.extend(behavioral_result.get("anomalies", []))
        all_signals.extend(policy_result.get("recommendations", []))
        all_signals.extend(threat_result.get("threats_found", []))
        
        # Remover duplicados
        all_signals = list(dict.fromkeys(all_signals))
        
        # Calcular score agregado
        risk_level = context_result.get("risk_level", "LOW")
        behavioral_score = behavioral_result.get("behavioral_score", 1.0)
        external_risk = threat_result.get("external_risk_level", "LOW")
        policies_count = len(policy_result.get("applicable_policies", []))
        
        # Score simple
        risk_scores = {"LOW": 0, "MEDIUM": 0.5, "HIGH": 1.0}

        
        aggregated_risk = (
            risk_scores[risk_level] * 0.3 +
            (1 - behavioral_score) * 0.3 +
            risk_scores[external_risk] * 0.15 +  # ← Reducido de 0.2 a 0.15
            min(policies_count * 0.25, 0.25)     # ← Aumentado de 0.2 a 0.25
        )
        # Total: 0.0
        
        # ============================================
        # AJUSTES POR SEÑALES ESPECÍFICAS
        # ============================================
        
        # Convertir todas las señales a texto para buscar patrones
        all_signals_text = " ".join(all_signals).lower()
        
        # Detectar factores
        has_new_device = "dispositivo nuevo" in all_signals_text or "dispositivo desconocido" in all_signals_text
        has_high_amount = "monto inusualmente alto" in all_signals_text or "monto muy alto" in all_signals_text or "monto elevado" in all_signals_text
        has_low_amount = "monto bajo" in all_signals_text or "monto inusualmente bajo" in all_signals_text
        has_unusual_time = "horario atípico" in all_signals_text
        has_different_country = "país diferente" in all_signals_text or "país no habitual" in all_signals_text
        
        
        # AJUSTE 1: Horario atípico + monto ALTO → CHALLENGE (0.40)
        # No aplicar si monto es BAJO
        if has_unusual_time and not has_low_amount:
            if aggregated_risk < 0.40:
                print(f"   ⚠️  Horario atípico (sin monto bajo) - Ajustando risk de {aggregated_risk:.2f} a 0.40 (CHALLENGE)")
                aggregated_risk = 0.40
        
        # AJUSTE 2: Monto alto solo → CHALLENGE (0.40)
        if has_high_amount and not has_new_device and not has_different_country:
            if aggregated_risk < 0.40:
                print(f"   ⚠️  Monto alto solo - Ajustando risk de {aggregated_risk:.2f} a 0.40 (CHALLENGE)")
                aggregated_risk = 0.40
        
        # AJUSTE 3: Dispositivo nuevo + monto ALTO + otra anomalía → ESCALATE (0.60)
        if has_new_device and has_high_amount and (has_different_country or has_unusual_time):
            if aggregated_risk < 0.60:
                print(f"   🚫 Dispositivo + monto alto + anomalía - Ajustando risk de {aggregated_risk:.2f} a 0.60 (ESCALATE)")
                aggregated_risk = 0.60
        
        # AJUSTE 4: País diferente + monto alto → ESCALATE (0.60)
        if has_different_country and has_high_amount:
            if aggregated_risk < 0.60:
                print(f"   🚫 País diferente + monto alto - Ajustando risk de {aggregated_risk:.2f} a 0.60 (ESCALATE)")
                aggregated_risk = 0.60
        
        # AJUSTE 5: 3+ señales CRÍTICAS → ESCALATE (0.75)
        # NO contar monto bajo ni dispositivo solo como crítico
        red_flags = [
            has_new_device and has_high_amount,                # Dispositivo + monto alto
            has_different_country,                             # País diferente
            has_unusual_time and has_high_amount,              # Horario + monto alto
            has_high_amount and behavioral_score < 0.5,        # Monto muy alto + mal score
            policies_count >= 2,                               # 2+ políticas
            external_risk == "HIGH" and has_high_amount        # Amenaza + monto alto
        ]
        red_flag_count = sum(red_flags)
        
        if red_flag_count >= 3:
            if aggregated_risk < 0.75:
                print(f"   🔴 {red_flag_count} señales críticas - Ajustando risk de {aggregated_risk:.2f} a 0.75 (ESCALATE)")
                aggregated_risk = 0.75
        
        # AJUSTE 6: Si solo hay factores menores, limitar risk score
        # Factores menores: monto bajo, dispositivo nuevo solo, horario atípico solo
        only_minor_flags = (
            (has_low_amount or has_new_device or has_unusual_time) and
            not has_high_amount and
            not has_different_country and
            policies_count == 0
        )
        
        if only_minor_flags and aggregated_risk > 0.45:
            print(f"   ℹ️  Solo factores menores - Limitando risk de {aggregated_risk:.2f} a 0.45")
            aggregated_risk = 0.45
        
        # IMPORTANTE: Si solo hay dispositivo nuevo (sin otras señales), NO ajustar
        # Dejar que el risk score natural fluya al Decision Arbiter
        
        print(f"   📊 Evidencias consolidadas: {len(all_signals)}")
        print(f"   📈 Risk score final: {aggregated_risk:.2f}")
        
        return {
            "agent": self.name,
            "all_signals": all_signals,
            "aggregated_risk_score": aggregated_risk,
            "summary": f"Consolidadas {len(all_signals)} señales de 4 agentes. Risk score: {aggregated_risk:.2f}"
        }