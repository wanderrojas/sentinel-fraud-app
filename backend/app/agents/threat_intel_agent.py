"""
Threat Intel Agent (Simulado)
Simula búsqueda de amenazas externas
"""
from app.models.schemas import Transaction
from typing import Dict, List


class ThreatIntelAgent:
    """
    Agente que simula búsqueda de inteligencia externa sobre amenazas
    """
    
    def __init__(self):
        self.name = "Threat Intel Agent"
        # Base de datos simulada de amenazas
        self.threat_database = {
            "M-002": {
                "alerts": ["Reportes recientes de fraude en este comercio", "Incremento de transacciones sospechosas"],
                "risk_level": "HIGH",
                "url": "https://fraud-alerts.bcp.com.pe/M-002"
            },
            "M-999": {
                "alerts": ["Comercio no verificado", "Sin historial de transacciones"],
                "risk_level": "MEDIUM",
                "url": "https://fraud-alerts.bcp.com.pe/M-999"
            }
        }
    
    def analyze(
        self,
        transaction: Transaction,
        context_signals: List[str] = None
    ) -> Dict:
        """
        Simular búsqueda de amenazas externas
        
        Args:
            transaction: Datos de la transacción
            context_signals: Señales previas
        
        Returns:
            Dict con amenazas encontradas
        """
        
        print(f"\n🤖 {self.name} iniciando análisis...")
        print(f"   🔍 Buscando amenazas para merchant: {transaction.merchant_id}")
        
        # Simular búsqueda en base de amenazas
        merchant_id = transaction.merchant_id
        
        if merchant_id in self.threat_database:
            threat_info = self.threat_database[merchant_id]
            
            print(f"   ⚠️  Amenazas encontradas: {len(threat_info['alerts'])}")
            
            return {
                "agent": self.name,
                "threats_found": threat_info["alerts"],
                "external_risk_level": threat_info["risk_level"],
                "sources": [
                    {
                        "url": threat_info["url"],
                        "summary": " | ".join(threat_info["alerts"])
                    }
                ],
                "summary": f"Se encontraron {len(threat_info['alerts'])} alertas sobre el comercio {merchant_id}"
            }
        else:
            print(f"   ✅ Sin amenazas conocidas para este comercio")
            
            return {
                "agent": self.name,
                "threats_found": [],
                "external_risk_level": "LOW",
                "sources": [],
                "summary": f"No se encontraron amenazas conocidas sobre el comercio {merchant_id}"
            }