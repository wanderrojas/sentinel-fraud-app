"""
RAG Service - Servicio de Retrieval Augmented Generation
Gestiona ChromaDB y búsqueda de políticas internas
"""
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import List, Dict
import json
from pathlib import Path
import os


class RAGService:
    """
    Servicio para gestionar la base vectorial de políticas de fraude
    """
    
    def __init__(self, persist_directory: str = "./chroma"):
        """
        Inicializar ChromaDB con embeddings de OpenAI
        
        Args:
            persist_directory: Directorio donde se guardan los datos
        """
        self.persist_directory = persist_directory
        
        # Crear cliente de ChromaDB
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Configurar función de embeddings de OpenAI
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("❌ OPENAI_API_KEY no está configurada en el entorno")
        
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=openai_api_key,
            model_name="text-embedding-3-small"  # Modelo económico y eficiente
        )
        
        # Nombre de la colección
        self.collection_name = "fraud_policies"
        
        # Obtener o crear colección
        try:
            self.collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            print(f"✅ Colección '{self.collection_name}' cargada con OpenAI embeddings")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Políticas de detección de fraude del BCP"},
                embedding_function=self.embedding_function
            )
            print(f"✅ Colección '{self.collection_name}' creada con OpenAI embeddings")
    
    def load_policies_from_json(self, json_path: str = "data/fraud_policies.json"):
        """
        Cargar políticas desde archivo JSON y agregarlas a ChromaDB
        
        Args:
            json_path: Ruta al archivo JSON con políticas
        """
        # Verificar si ya hay datos
        count = self.collection.count()
        if count > 0:
            print(f"   ℹ️  Ya hay {count} políticas en la base. Saltando carga.")
            return
        
        # Cargar JSON
        policy_path = Path(json_path)
        if not policy_path.exists():
            print(f"   ⚠️  No se encontró {json_path}")
            return
        
        with open(policy_path, "r", encoding="utf-8") as f:
            policies = json.load(f)
        
        # Preparar datos para ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for policy in policies:
            policy_id = policy["policy_id"]
            rule = policy["rule"]
            version = policy["version"]
            
            # El documento es la regla completa
            document = f"Política {policy_id} (versión {version}): {rule}"
            
            documents.append(document)
            metadatas.append({
                "policy_id": policy_id,
                "version": version,
                "rule": rule
            })
            ids.append(policy_id)
        
        # Agregar a ChromaDB (usará OpenAI para generar embeddings)
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"   ✅ {len(policies)} políticas cargadas en ChromaDB con OpenAI embeddings")
    
    def search_policies(
        self,
        query: str,
        n_results: int = 3
    ) -> List[Dict]:
        """
        Buscar políticas relevantes usando búsqueda semántica
        
        Args:
            query: Consulta en lenguaje natural
            n_results: Número de resultados a retornar
        
        Returns:
            Lista de políticas relevantes con metadatos
        """
        # Buscar en ChromaDB (usará OpenAI para el embedding del query)
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Formatear resultados
        policies = []
        
        if results and results["ids"] and len(results["ids"]) > 0:
            for i, policy_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i] if "distances" in results else None
                
                policies.append({
                    "policy_id": metadata["policy_id"],
                    "rule": metadata["rule"],
                    "version": metadata["version"],
                    "relevance_score": 1 - distance if distance else 0.5,
                    "chunk_id": str(i + 1)
                })
        
        return policies
    
    def get_policy_by_id(self, policy_id: str) -> Dict:
        """
        Obtener una política específica por su ID
        
        Args:
            policy_id: ID de la política
        
        Returns:
            Política con metadatos
        """
        try:
            result = self.collection.get(ids=[policy_id])
            
            if result and result["ids"]:
                metadata = result["metadatas"][0]
                return {
                    "policy_id": metadata["policy_id"],
                    "rule": metadata["rule"],
                    "version": metadata["version"]
                }
        except:
            pass
        
        return None
    
    def reset_collection(self):
        """Eliminar y recrear la colección (útil para testing)"""
        try:
            self.client.delete_collection(name=self.collection_name)
            print(f"   ✅ Colección '{self.collection_name}' eliminada")
        except:
            pass
        
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Políticas de detección de fraude del BCP"},
            embedding_function=self.embedding_function
        )
        print(f"   ✅ Colección '{self.collection_name}' recreada con OpenAI embeddings")


# ============================================
# INSTANCIA GLOBAL DEL SERVICIO
# ============================================

_rag_service = None

def get_rag_service() -> RAGService:
    """Obtener instancia única del servicio RAG"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
        # Cargar políticas al iniciar
        _rag_service.load_policies_from_json()
    return _rag_service